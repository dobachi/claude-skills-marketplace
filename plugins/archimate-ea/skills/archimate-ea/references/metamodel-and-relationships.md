# ArchiMate 3.2 metamodel — elements, aspects, allowed relationships

The catalog and rules below are encoded in `scripts/archimate_metamodel.json` and
shared by the validator and both emitters. Edit the JSON to change behaviour; this
doc explains it.

## Element catalog (61 types across 7 aspects + composite + connector)

Each element has a **layer** and an **aspect**. Aspect drives the relationship
rules (ArchiMate's relationship table is largely aspect-structured).

| Layer | Active structure | Behaviour | Passive structure | Motivation |
|-------|------------------|-----------|-------------------|------------|
| **Motivation** | — | — | — | Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value |
| **Strategy** | Resource | Capability, CourseOfAction, ValueStream | — | — |
| **Business** | BusinessActor, BusinessRole, BusinessCollaboration, BusinessInterface | BusinessProcess, BusinessFunction, BusinessInteraction, BusinessEvent, BusinessService | BusinessObject, Contract, Representation, Product | — |
| **Application** | ApplicationComponent, ApplicationCollaboration, ApplicationInterface | ApplicationFunction, ApplicationInteraction, ApplicationProcess, ApplicationEvent, ApplicationService | DataObject | — |
| **Technology** | Node, Device, SystemSoftware, TechnologyCollaboration, TechnologyInterface, Path, CommunicationNetwork | TechnologyFunction, TechnologyProcess, TechnologyInteraction, TechnologyEvent, TechnologyService | Artifact | — |
| **Physical** | Equipment, Facility, DistributionNetwork | — | Material | — |
| **Implementation** | — | WorkPackage, ImplementationEvent | Deliverable | Gap (motivation), Plateau (composite) |

Composite/cross-layer: **Location**, **Grouping**. Connector: **Junction**.

## Relationships (11 types)

Structural: **Composition, Aggregation, Assignment, Realization**.
Dependency: **Serving, Access, Influence, Association**.
Dynamic: **Triggering, Flow**. Other: **Specialization**.

## Allowed-relationship rules (aspect-based approximation)

The validator answers "is relationship R legal from element type S to type T?"
using aspect pairs (`scripts/archimate_metamodel.json` → `rules`), plus three
special cases handled in code:

- **Association** — allowed between any two elements.
- **Specialization** — allowed only when `source.type == target.type`.
- **Junction endpoints** — any edge touching a Junction bypasses the aspect check;
  legality is instead enforced by *junction consistency* (all edges through one
  junction must be the same relationship type).

Aspect-pair rules (s = source aspect, t = target aspect; `*` = any):

| Relationship | Allowed (s → t) pairs |
|--------------|------------------------|
| Composition / Aggregation | active→active, behavior→behavior, passive→passive, motivation→motivation, composite→* |
| Assignment | active→behavior, active→active, active→passive, behavior→passive |
| Realization | behavior→behavior, active→behavior, passive→passive, active→passive, behavior→passive, passive→active, *→motivation |
| Serving | active→active, active→behavior, behavior→active, behavior→behavior, active→motivation, behavior→motivation |
| Access | behavior→passive, passive→behavior |
| Influence | motivation→motivation, *→motivation, motivation→* |
| Triggering | behavior→behavior, active→behavior, behavior→active |
| Flow | behavior→behavior, active→active, behavior→active, active→behavior |

**This is an approximation of ArchiMate 3.2 Appendix B**, deliberately *generous
via Association* and conservative elsewhere. It catches the common illegal edges
(e.g. Triggering from a Goal to a component) that matter in dialogue, but does not
reproduce every cell of the full derivation matrix. When the validator flags an
edge you believe is legal, it will list what *is* permitted between those types;
if it is a genuine spec case the rules miss, widen the relevant rule in the JSON.

## Modifiers

| Modifier | Relationship | YAML | XML |
|----------|--------------|------|-----|
| accessType | Access | `none / read / write / readWrite` | `Access / Read / Write / ReadWrite` |
| isDirected | Association | boolean | `isDirected="true"` |
| strength | Influence | free text | (not an XML attribute — kept in YAML, rendered in PlantUML) |
| junctionType | Junction (element) | `and / or` | `xsi:type="AndJunction" / "OrJunction"` |
