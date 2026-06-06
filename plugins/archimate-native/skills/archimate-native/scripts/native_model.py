"""Parse and index an Archi-native .archimate model, retaining the lxml tree for
in-place (round-trip-safe) mutation.

Archi's native type vocabulary is version-dependent; this module normalizes every
native xsi:type to the canonical ArchiMate 3.2 name used by archimate_metamodel.py
(via native_vocab.json), and — when writing new nodes — maps canonical names back
to the spelling matching the file's own era, so vocabulary is never silently
upgraded. See references/vocabulary-map.md.
"""

from __future__ import annotations

import json
import os
import re
import uuid

from lxml import etree

from archimate_metamodel import load as load_metamodel

_HERE = os.path.dirname(os.path.abspath(__file__))
_VOCAB_PATH = os.path.join(_HERE, "native_vocab.json")

ARCHI_NS = "http://www.archimatetool.com/archimate"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XSI_TYPE = f"{{{XSI_NS}}}type"

DIAGRAM_TYPE = "ArchimateDiagramModel"
VISUAL_ONLY = {"Group", "Note", "DiagramModelReference"}


def _local_xsi(el) -> str | None:
    """Return the local part of an element's archimate:xsi:type (e.g. 'BusinessActor')."""
    v = el.get(XSI_TYPE)
    if not v:
        return None
    return v.split(":", 1)[1] if ":" in v else v


class Concept:
    __slots__ = ("el", "id", "native_type", "canonical_type", "name", "folder")

    def __init__(self, el, native_type, canonical_type, folder):
        self.el = el
        self.id = el.get("id")
        self.native_type = native_type
        self.canonical_type = canonical_type
        self.name = el.get("name") or ""
        self.folder = folder


class Relationship:
    __slots__ = ("el", "id", "native_type", "canonical_type", "name", "source", "target")

    def __init__(self, el, native_type, canonical_type):
        self.el = el
        self.id = el.get("id")
        self.native_type = native_type
        self.canonical_type = canonical_type
        self.name = el.get("name") or ""
        self.source = el.get("source")
        self.target = el.get("target")


class DiagramObject:
    __slots__ = ("el", "id", "concept_id", "view_id")

    def __init__(self, el, view_id):
        self.el = el
        self.id = el.get("id")
        self.concept_id = el.get("archimateElement")
        self.view_id = view_id

    def bounds(self):
        b = self.el.find("bounds")
        if b is None:
            return None
        return {k: int(b.get(k, 0)) for k in ("x", "y", "width", "height")}


class Connection:
    __slots__ = ("el", "id", "source", "target", "relationship_id", "view_id")

    def __init__(self, el, view_id):
        self.el = el
        self.id = el.get("id")
        self.source = el.get("source")
        self.target = el.get("target")
        self.relationship_id = el.get("relationship")
        self.view_id = view_id


class Diagram:
    __slots__ = ("el", "id", "name", "viewpoint", "objects", "connections")

    def __init__(self, el):
        self.el = el
        self.id = el.get("id")
        self.name = el.get("name") or ""
        self.viewpoint = el.get("viewpoint")
        self.objects = {}       # diagObjId -> DiagramObject
        self.connections = {}   # connId -> Connection


class Folder:
    __slots__ = ("el", "id", "name", "type", "parent")

    def __init__(self, el, parent=None):
        self.el = el
        self.id = el.get("id")
        self.name = el.get("name") or ""
        self.type = el.get("type")
        self.parent = parent


class NativeModel:
    def __init__(self, path):
        self.path = path
        self.vocab = json.load(open(_VOCAB_PATH, encoding="utf-8"))
        self.mm = load_metamodel()
        parser = etree.XMLParser(remove_blank_text=False)
        self.tree = etree.parse(path, parser)
        self.root = self.tree.getroot()
        self.name = self.root.get("name") or ""
        self.id = self.root.get("id")
        self.version = self.root.get("version") or ""
        p = self.root.find("purpose")
        self.purpose = p.text if p is not None else None

        self.concepts = {}        # id -> Concept
        self.relationships = {}    # id -> Relationship
        self.folders = []          # list[Folder]
        self.concept_folder = {}   # concept id -> Folder
        self.diagrams = {}         # view id -> Diagram
        self.diagobjs_by_concept = {}        # concept id -> [DiagramObject]
        self.connections_by_relationship = {}  # rel id -> [Connection]
        self._all_ids = set()

        self.era = self._detect_era()
        self._index()

    # ---- era / vocabulary -------------------------------------------------
    def _detect_era(self) -> str:
        eras = self.vocab["version_eras"]
        modern_types = set(self.vocab["modern_only_native_types"])
        # presence of modern-only native types is decisive
        for el in self.root.iter("element"):
            if _local_xsi(el) in modern_types:
                return "modern"
        if re.match(eras["modern"]["version_regex"], self.version):
            return "modern"
        if re.match(eras["legacy"]["version_regex"], self.version):
            return "legacy"
        return "legacy"

    def to_canonical(self, native_type: str | None) -> str | None:
        if native_type is None:
            return None
        m = self.vocab["native_to_canonical"].get(native_type)
        if m:
            return m
        if self.mm.is_element_type(native_type):
            return native_type            # identity concept (BusinessActor, …)
        if native_type == "Junction":
            return "Junction"
        if native_type.endswith("Relationship"):
            base = native_type[: -len("Relationship")]
            if self.mm.is_relationship_type(base):
                return base
        return None

    def to_native(self, canonical_type: str, kind: str) -> str:
        """Map a canonical type back to the era-appropriate native spelling.
        kind ∈ {'concept','relationship'}."""
        era = self.vocab["canonical_to_native_by_era"][self.era]
        if kind == "relationship":
            return era["_relationships"].get(canonical_type, canonical_type + "Relationship")
        return era["_concepts"].get(canonical_type, canonical_type)

    # ---- indexing ---------------------------------------------------------
    def _index(self):
        for el in self.root.iter():
            if el.get("id"):
                self._all_ids.add(el.get("id"))
        for child in self.root:
            if child.tag == "folder":
                self._walk_folder(child, None)

    def _walk_folder(self, folder_el, parent):
        folder = Folder(folder_el, parent)
        self.folders.append(folder)
        for el in folder_el:
            if el.tag == "folder":
                self._walk_folder(el, folder)
            elif el.tag == "element":
                self._classify(el, folder)

    def _classify(self, el, folder):
        native = _local_xsi(el)
        if el.get("source") is not None and el.get("target") is not None:
            rel = Relationship(el, native, self.to_canonical(native))
            self.relationships[rel.id] = rel
        elif native == DIAGRAM_TYPE:
            self._index_diagram(el)
        elif native in VISUAL_ONLY:
            pass
        else:
            c = Concept(el, native, self.to_canonical(native), folder)
            self.concepts[c.id] = c
            self.concept_folder[c.id] = folder

    def _index_diagram(self, el):
        d = Diagram(el)
        self.diagrams[d.id] = d
        for child in el.iter("child"):
            t = _local_xsi(child)
            if t == "DiagramObject" and child.get("archimateElement"):
                do = DiagramObject(child, d.id)
                d.objects[do.id] = do
                self.diagobjs_by_concept.setdefault(do.concept_id, []).append(do)
        for conn in el.iter("sourceConnection"):
            c = Connection(conn, d.id)
            d.connections[c.id] = c
            if c.relationship_id:
                self.connections_by_relationship.setdefault(c.relationship_id, []).append(c)

    # ---- reverse lookups (computed on demand) -----------------------------
    def rels_of(self, concept_id, direction="both"):
        out = []
        for r in self.relationships.values():
            if direction in ("out", "both") and r.source == concept_id:
                out.append(r)
            if direction in ("in", "both") and r.target == concept_id:
                out.append(r)
        return out

    # ---- helpers ----------------------------------------------------------
    def find_concept(self, id_or_name):
        if id_or_name in self.concepts:
            return self.concepts[id_or_name]
        matches = [c for c in self.concepts.values() if c.name == id_or_name]
        return matches[0] if len(matches) == 1 else (matches or [None])[0]

    def label(self, concept_id):
        c = self.concepts.get(concept_id)
        return c.name if c else f"<{concept_id}>"

    def new_id(self):
        while True:
            cand = uuid.uuid4().hex[:8]
            if cand not in self._all_ids:
                self._all_ids.add(cand)
                return cand

    def folder_for_layer(self, layer):
        ftype = self.vocab["folder_type_by_layer"].get(layer, "other")
        for f in self.folders:
            if f.type == ftype and f.parent is None:
                return f
        return None

    def serialize(self) -> bytes:
        # Match Archi's declaration exactly (double quotes) and trailing newline,
        # so an unedited load+save is byte-identical and edit diffs stay minimal.
        body = etree.tostring(self.tree, xml_declaration=False, encoding="UTF-8")
        out = b'<?xml version="1.0" encoding="UTF-8"?>\n' + body
        if not out.endswith(b"\n"):
            out += b"\n"
        return out

    def save(self, path=None):
        with open(path or self.path, "wb") as fh:
            fh.write(self.serialize())


if __name__ == "__main__":
    import sys
    m = NativeModel(sys.argv[1])
    print(f"{m.name} (version {m.version}, era={m.era})")
    print(f"concepts={len(m.concepts)} relationships={len(m.relationships)} "
          f"views={len(m.diagrams)} folders={len(m.folders)}")
    bad = [c.id for c in m.concepts.values() if c.canonical_type is None]
    if bad:
        print("unmapped concept types:", bad)
