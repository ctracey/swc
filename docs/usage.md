# Sessionless Workload Context

[Intent](/README.md) | [Getting Started](/docs/usage.md#getting-started) | [User Guide](/docs/usage.md#using-the-workflows) | [Plugin Design](/docs/plugin-design.md)


## Getting Started
Install it via a locally hosted Claude Code marketplace such as [ctracey/claude-code-plugin-marketplace](https://github.com/ctracey/claude-code-plugin-marketplace).


## Using the Workflows

The SWC plugin uses skills to guide an agent through the complete delivery lifecycle in collaboration with the user — from capturing intent and breaking down work, through clarifying requirements and solution design, to implementing and reviewing the solution — with persisted context at every step.

In your claude code session you can see the list of skills with: `/swc:`

<p align="center"><a href="docs/img/swc-pillars.png"><img src="img/swc-pillars.png" width="60%"></a></p>
<p align="center"><em>3 key SWC pillars: workload, workflows, context</em></p>


### SWC Workflows

3 main workflows guide the delivery lifecycle:

| Workflow | Description |
|----------|-------------|
| [**Plan**](/docs/usage.md#plan-workflow) | A structured conversation that captures intent, solution direction, delivery shape, and work breakdown, producing a set of planning docs any future session can execute from cold. |
| [**Deliver**](/docs/usage.md#deliver-workflow) | Drives a single work item from backlog to done: clarifying requirements, defining acceptance specs, solution design, implementation, code review, and user sign-off. |
| [**Implement**](/docs/usage.md#implement-workflow) | An agent-side workflow that orients against the brief, implements the solution scenario by scenario, and writes a summary artefact on completion. |


## Plan Workflow


## Deliver Workflow


## Implement Workflow

