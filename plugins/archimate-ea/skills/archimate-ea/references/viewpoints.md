# ArchiMate standard viewpoints (reference)

Use a viewpoint to decide *which* elements and relationships belong in a view —
each view's `viewpoint:` field is a label naming the intent. This is reference
only; the validator does not enforce viewpoint element rules in v1. Pick the
viewpoint that matches the conversation you are having, then list only the
elements that serve that purpose in the view's `elements`.

## Basic / introductory viewpoints

| Viewpoint | Purpose | Typical elements |
|-----------|---------|------------------|
| Organization | Show internal structure of the enterprise | Actor, Role, Collaboration, Interface, Location |
| Business Process Cooperation | How processes relate and depend | BusinessProcess, BusinessService, BusinessObject, events |
| Application Cooperation | App components and their interdependencies | ApplicationComponent, ApplicationService, Interface, DataObject |
| Application Usage | How apps support the business | ApplicationService serving BusinessProcess/Function |
| Implementation & Deployment | How apps map to technology | ApplicationComponent, Artifact, Node, SystemSoftware |
| Technology | Technology infrastructure | Node, Device, SystemSoftware, Network, TechnologyService |
| Information Structure | Business/data/representation objects | BusinessObject, DataObject, Representation, Artifact |
| Service Realization | How services are realized by behaviour | Service, Process/Function, realizing elements |
| Layered | Cross-layer overview of the whole stack | one or two elements per layer with the chain between them |

## Motivation viewpoints

| Viewpoint | Purpose |
|-----------|---------|
| Stakeholder | Stakeholders, drivers, assessments and the goals they motivate |
| Goal Realization | How goals are refined into outcomes and requirements |
| Requirements Realization | How requirements are realized by core elements |
| Motivation | Any combination of the motivation elements |

## Strategy & implementation viewpoints

| Viewpoint | Purpose |
|-----------|---------|
| Strategy | Capabilities, resources, courses of action, value streams |
| Capability Map | Capabilities and their structure |
| Outcome Realization | How outcomes are produced by capabilities/courses of action |
| Migration | Plateaus and the gaps between them |
| Implementation & Migration | Work packages, deliverables, plateaus, gaps |

Common `viewpoint:` label values used by the example model: `Motivation`,
`Application_Cooperation`, `Layered`, `Migration`.
