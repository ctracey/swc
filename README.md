# Sessionless Workload Context

[Intent](/README.md) | [Usage](/docs/usage.md) | [Plugin Design](/docs/plugin-design.md)


**Claude forgets. Your project shouldn't.**

A Claude Code plugin for structured software delivery - Agents implement from a backlog, context is externalised from sessions, and your project keeps moving whether Claude remembers or not.

<p align="center"><a href="docs/img/ephemeral-orchestration.png"><img src="docs/img/ephemeral-orchestration.png" width="60%"></a></p>

## Intent

Sessionless Workload Context (SWC) is a suite of skills that embodies a delivery operating model to guides agent through the complete lifecycle - from capturing intent and breaking down work, through clarifying requirements and quality validations, to deliverying solutions.

SWC onboards an agent to best practice delivery culture — the same way you would onboard a skilled person to your team. It prescribes workflows, conventions, and feedback loops so you can act as product owner: breaking down work, steering agents through small focused workitems, and validating quality at each stage.

Taking a systems based orchestrated delivery approach to agentic onboarding we can support adoption by:
 - externalising culture with system workflows & conventions
 - externalising project domain context by externalising requirements, design & state


### Continuity thinking applied to agentic work

Good teams don't keep a project alive in one person's head — they externalise it with systems and documents. Its possible for a new developer to pick up a well-documented piece of work without a handoff call (this doesnt replace super valuable human conversations, but you get the idea). SWC applies that same thinking to AI sessions. A conversation with Claude is ephemeral; the work is not. By persisting intent, requirements, decisions, and progress into files that live alongside your code, SWC means the next session — whether it starts in five minutes, five days or five months — inherits the full context of what came before.



## Application

The SWC plugin uses skills to guide an agent through the complete delivery lifecycle in collaboration with the user — from capturing intent and breaking down work, through clarifying requirements and solution design, to implementing and reviewing the solution — with persisted context at every step.

<p align="center"><a href="docs/img/swc-pillars.png"><img src="docs/img/swc-pillars.png" width="60%"></a></p>
<p align="center"><em>3 key SWC pillars: workload, workflows, context</em></p>


### SWC Workflows

3 main workflows guide the delivery lifecycle:

| Workflow | Description |
|----------|-------------|
| [**Plan**](/docs/usage.md#plan-workflow) | A structured conversation that captures intent, solution direction, delivery shape, and work breakdown, producing a set of planning docs any future session can execute from cold. |
| [**Deliver**](/docs/usage.md#deliver-workflow) | Drives a single work item from backlog to done: clarifying requirements, defining acceptance specs, solution design, implementation, code review, and user sign-off. |
| [**Implement**](/docs/usage.md#implement-workflow) | An agent-side workflow that orients against the brief, implements the solution scenario by scenario, and writes a summary artefact on completion. |


## SWC Benefits

- Scope adherence — agents work against a clear, bounded brief
- Continuity — pick up any session without context loss
- Documented project IP — decisions and rationale are captured, not lost TODO:(SPEC format)
- Quality — supported through BDD and user feedback loops
- Consistency — agent behaviour governed by documented conventions