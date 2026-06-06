"""ArchiMate 3.2 metamodel loader.

Single source of truth shared by the validator and both emitters. Reads
archimate_metamodel.json (element catalog, aspect-based allowed-relationship
rules, PlantUML macro map, Open Exchange xsi:type rules) and exposes lookup
helpers. The relationship rules are an aspect-category approximation of the
ArchiMate 3.2 relationship matrix (Appendix B): generous via Association,
conservative elsewhere. See references/metamodel-and-relationships.md.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_PATH = os.path.join(_HERE, "archimate_metamodel.json")


class Metamodel:
    def __init__(self, data: dict):
        self.spec = data.get("spec", "ArchiMate")
        self.elements = data["elements"]
        self.relationships = data["relationships"]
        self.rules = {k: v for k, v in data["rules"].items() if not k.startswith("_")}
        self.modifiers = data["modifiers"]
        self.macros = data["macros"]

    # ---- element catalog -------------------------------------------------
    def is_element_type(self, t: str) -> bool:
        return t in self.elements

    def layer_of(self, t: str) -> str | None:
        e = self.elements.get(t)
        return e["layer"] if e else None

    def aspect_of(self, t: str) -> str | None:
        e = self.elements.get(t)
        return e["aspect"] if e else None

    def element_types(self) -> list[str]:
        return sorted(self.elements)

    # ---- relationship catalog -------------------------------------------
    def is_relationship_type(self, t: str) -> bool:
        return t in self.relationships

    def relationship_types(self) -> list[str]:
        return sorted(self.relationships)

    # ---- allowed-relationship logic -------------------------------------
    def _aspect_pair_allowed(self, rel_type: str, src_aspect: str, dst_aspect: str) -> bool:
        pairs = self.rules.get(rel_type, [])
        for s, d in pairs:
            if (s == "*" or s == src_aspect) and (d == "*" or d == dst_aspect):
                return True
        return False

    def relationship_allowed(self, rel_type: str, src_type: str, dst_type: str) -> bool:
        """Return True if rel_type is permitted from src_type to dst_type.

        Junction endpoints bypass the aspect check (a junction is a connector;
        its real legality is enforced by the junction-consistency check in the
        validator). Association is universally allowed. Specialization requires
        the same element type. Everything else consults the aspect-pair rules.
        """
        if not self.is_relationship_type(rel_type):
            return False
        src_aspect = self.aspect_of(src_type)
        dst_aspect = self.aspect_of(dst_type)
        if src_aspect is None or dst_aspect is None:
            return False
        if src_aspect == "connector" or dst_aspect == "connector":
            return True
        if rel_type == "Association":
            return True
        if rel_type == "Specialization":
            return src_type == dst_type
        return self._aspect_pair_allowed(rel_type, src_aspect, dst_aspect)

    def allowed_relationships(self, src_type: str, dst_type: str) -> list[str]:
        """List relationship types permitted from src_type to dst_type (for hints)."""
        return [r for r in self.relationship_types()
                if self.relationship_allowed(r, src_type, dst_type)]

    # ---- emit helpers ----------------------------------------------------
    def plantuml_macro(self, element_type: str) -> str | None:
        return self.macros.get(element_type)

    def relationship_macro(self, rel_type: str) -> str | None:
        r = self.relationships.get(rel_type)
        return r["macro"] if r else None

    def xsi_type(self, element_type: str, junction_type: str | None = None) -> str:
        """Open Exchange xsi:type. Identity for most elements; junctions map to
        AndJunction / OrJunction based on junction_type."""
        if element_type == "Junction":
            jt = (junction_type or "or").lower()
            return self.modifiers["junctionXsi"].get(jt, "OrJunction")
        return element_type

    def access_type_xml(self, access_type: str) -> str:
        return self.modifiers["accessTypeXml"].get(access_type, "Access")


@lru_cache(maxsize=1)
def load(path: str | None = None) -> Metamodel:
    with open(path or _DATA_PATH, encoding="utf-8") as fh:
        return Metamodel(json.load(fh))


if __name__ == "__main__":
    mm = load()
    print(f"{mm.spec}: {len(mm.elements)} element types, "
          f"{len(mm.relationships)} relationship types.")
    print("Example — ApplicationComponent -> DataObject allows:",
          ", ".join(mm.allowed_relationships("ApplicationComponent", "DataObject")))
