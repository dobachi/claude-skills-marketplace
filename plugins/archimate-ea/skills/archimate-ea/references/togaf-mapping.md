# TOGAF ADM ↔ ArchiMate mapping (reference)

The skill's core is **method-agnostic** — it models in ArchiMate regardless of the
governing method. This mapping is provided for teams running TOGAF: it shows which
ArchiMate layers and deliverables each ADM phase typically produces. Use it to
sequence the facilitation when a TOGAF engagement demands it; ignore it otherwise.

| ADM phase | Focus | ArchiMate layers in play | Typical deliverables / views |
|-----------|-------|--------------------------|------------------------------|
| **Preliminary** | Principles, frameworks | Motivation (Principle) | Architecture principles catalog |
| **A. Architecture Vision** | Scope, stakeholders, goals | Motivation, Strategy | Stakeholder view, Goal view, high-level capability map |
| **B. Business Architecture** | Business services & processes | Business (+ Strategy) | Business process cooperation, Organization, Service realization |
| **C. Information Systems (Data)** | Data structures | Application (DataObject), Business (BusinessObject) | Information structure view |
| **C. Information Systems (Application)** | Application landscape | Application | Application cooperation, Application usage |
| **D. Technology Architecture** | Infrastructure | Technology, Physical | Technology view, Implementation & deployment |
| **E. Opportunities & Solutions** | Work packages, increments | Implementation & Migration | Plateaus, gaps, work packages |
| **F. Migration Planning** | Roadmap, sequencing | Implementation & Migration | Migration view, roadmap |
| **G. Implementation Governance** | Conformance | all (as built) | Conformance/baseline views |
| **H. Change Management** | Drivers for change | Motivation (Driver, Assessment) | Re-assessment of drivers/goals |
| **Requirements Management** (center) | Continuous | Motivation (Requirement, Constraint) | Requirements realization view |

## How to use it in facilitation

- Treat ADM phases A→D as the default *adaptive top-down* descent through the
  motivation → strategy → business → application → technology layers.
- Map **Requirements Management** to the Motivation layer kept live across the whole
  engagement — revisit requirements at every checkpoint, not just at the start.
- Phases E/F correspond to the Implementation & Migration layer; do them last.
- None of this is enforced. If the user is not doing TOGAF, drop the phase framing
  entirely and use the layer-by-layer playbook directly.
