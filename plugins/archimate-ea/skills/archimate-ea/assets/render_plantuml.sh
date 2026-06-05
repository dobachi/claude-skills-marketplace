#!/usr/bin/env bash
# Render emitted .puml view files to PNG/SVG. Best-effort: needs the `plantuml`
# CLI (or plantuml.jar) AND Graphviz `dot` AND the bundled ArchiMate stdlib.
# Degrades with a clear message when those are absent — missing tooling is not a
# skill failure (validate + emit are the testable core).
#
# Usage: render_plantuml.sh [-f png|svg] FILE.puml [FILE.puml ...]
set -euo pipefail

FORMAT="png"
if [[ "${1:-}" == "-f" ]]; then FORMAT="$2"; shift 2; fi
if [[ $# -eq 0 ]]; then echo "usage: render_plantuml.sh [-f png|svg] FILE.puml ..." >&2; exit 2; fi

if ! command -v dot >/dev/null 2>&1; then
  echo "Graphviz 'dot' not found — install graphviz to render. Skipping." >&2; exit 0
fi

run_plantuml() {
  if command -v plantuml >/dev/null 2>&1; then plantuml "-t${FORMAT}" "$@"
  elif [[ -n "${PLANTUML_JAR:-}" && -f "$PLANTUML_JAR" ]]; then java -jar "$PLANTUML_JAR" "-t${FORMAT}" "$@"
  else
    echo "PlantUML not found. Install the 'plantuml' CLI or set PLANTUML_JAR=/path/plantuml.jar. Skipping." >&2
    exit 0
  fi
}

run_plantuml "$@"
echo "Rendered ${#} file(s) to ${FORMAT}."
