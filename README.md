# Sessionless Workload Context

[Intent](/README.md) | [Usage](/docs/usage.md) | [Plugin Design](/docs/plugin-design.md)


<table><tr><td width="33%">

<h3>Claude forgets
<br/>Your project shouldn't</h3>

A Claude Code plugin for structured software delivery - Agents implement from a backlog, context is externalised from sessions, and your project keeps moving whether Claude remembers or not.
<br /><br />

</td><td width="67%">

<p align="center"><img src="docs/img/ephemeral-orchestration.png"></p>

</td></tr></table>


## Intent

Sessionless Workload Context (SWC) is a suite of skills that embodies a delivery operating model that guides an agent through the complete lifecycle - from capturing intent and breaking down work, through clarifying requirements and quality validations, to deliverying solutions.

SWC onboards an agent to best practice delivery culture — the same way you would onboard a skilled person to your team. It prescribes workflows, conventions, and feedback loops so you can act as product owner: breaking down work, steering agents through small focused workitems, and validating quality at each stage.

Taking a systems based orchestrated delivery approach to agentic onboarding we can support adoption and scale by:
 - externalising culture with system workflows & conventions
 - externalising project domain context by externalising requirements, design & state


### Continuity thinking applied to agentic work

Good teams don't keep a project alive in one person's head — they externalise it with systems and documents. Its possible for a new developer to pick up a well-documented piece of work without a handoff call (this doesnt replace super valuable human conversations, but you get the idea). SWC applies that same thinking to AI sessions. A conversation with Claude is ephemeral; the work is not. By persisting intent, requirements, decisions, and progress into files that live alongside your code, SWC means the next session — whether it starts in five minutes, five days or five months — inherits the full context of what came before.



## Application

The plugin uses skills to guides an agent through the complete delivery lifecycle in collaboration with the user — from capturing intent and breaking down work, through clarifying requirements and solution design, to implementing and reviewing the solution — with persisted context at every step.



<table><tr>
<td width="10%"></td>
<td width="20%">

<h3>3 key pillars</h3>

 - workload
 - workflows
 - context
<br /><br />

</td><td width="70%">

<p align="center"><img src="docs/img/swc-pillars.png" width="70%"></p>

</td></tr></table>


### SWC Workflows

3 main workflows guide the delivery lifecycle:

| Workflow | Description |
|----------|-------------|
| **Plan** | A structured conversation that captures intent, solution direction, delivery shape, and work breakdown, producing a set of planning docs any future session can execute from cold. |
| **Deliver** | Drives a single work item from backlog to done: clarifying requirements, defining acceptance specs, solution design, implementation, code review, and user sign-off. |
| **Implement** | An agent-side workflow that orients against the brief, implements the solution scenario by scenario, and writes a summary artefact on completion. |


## SWC Benefits

- Scope adherence — agents work against a clear, bounded brief
- Continuity — pick up any session without context loss
- Documented project IP — decisions and rationale are captured, not lost TODO:(SPEC format)
- Quality — supported through BDD and user feedback loops
- Consistency — agent behaviour governed by documented conventions