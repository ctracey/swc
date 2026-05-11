# SWC Implement Workflow Test Scripts
this is usually triggered by deliver workflow Implement stage via an agent.

this workflow is designed to have minimal user interaction and run off the captured context (specs & solution design)

NOTE: for testing you can manually trigger this workflow in the main session with

```/swc:workflowImplement```
it will likely pick up the first WIP item


## Orient Stage
should read the context from the .swc/ context files for this work item

it should make sure that the work item is marked as in progress


## Implement Stage
should implement the solution based on context


## Summarise Stage
should write a summary.md file to the .swc/ workitem context so that the main session can easily follow what has been done and handover to user / other agents in the workflows

