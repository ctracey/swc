# SWC Deliver Workflow Test Scripts
This test follows the happy path scenario for a single file react html static website

## SCENARIO: Check the plan
```whats the plan```

given a plan exists for the current branch
when the user asks about the plan
then the report-plan skill is used to give a summary


## SCENARIO: Deliver workflow happy path
each workflow stage should confirm corrent interpretation with user
workflow progress should be displayed at the start of each phase
should report on satisfaction of stage exit criteria before moving to next workflow stage

### Trigger Skill (swc:workflowDeliver)

```list workitems```
given an existing workload
then the workload list should be displayed

```lets work on 1.3```
should trigger skill (swc:workflowDeliver)
then show the user the Deliver workflow stages and confirm they want to use this workflow

```yes```
should mark the target workitem as in progress
and then start the requirements stage


## Requirements Stage
should recap with the user the intent that is already understood from the documented context
then should check if the user wants to add or clarify anything

```proceed```


## Specs Stage
should talk to the user about BDD or lightweight specs and ask the user what good looks like
```css and javascript files used in dev are packaged as a single html file in dist folder```

it should ask the user about what shouldn't happen
```there should be no other files in dist other than a single html file```

specs should then be written to file


## Solution Design Stage
should confirm the implementation approach with the user

```Use a TDD loop```

should check if anything else to cover
```proceed```


## Implement Stage
should ask the user if they want to run a health check before spawning the implementation agent so its clear if test fail due to changes or current state
```y```

should then spawn an agent to implement the change based on the context
when the agent exists the implementation stage exit criteria should be satisfied.

when the summary is missing the agent should be prompted to capture the summary context.

## Refine Stage
once implement agent completes with a summary
the refine stage can evaluate the summary context file 
then the swc:code-reviewer skill can do a code review and advise on any recommendations


## Review Stage
The user should be prompted to review the changes and advise if the requirements have been satisfied.
A summary of changes should be provided
along with a brief to provide the user with confidence on the quality (e.g. code quality, test results, instructions on how to run test server or where to find it if already running


### feedback loop
when the user has feedback for changes
```no instead of index.html can you call this demo.html```

then the deliver workflow starts again to implement these changes
NOTE: here you should be able to move fast through the workflow without comprehensive details for simple changes
requirements, specs & solution design should all be updated before next implementation pass if required

```update docs and proceed to implement. Ask me if you have questions but should be clear```


### accept changes
when the user is happy with the changes
then it should confirm user is ready to commit and push

```yes```


## Accept Stage
when the user is happy the swc:ship skill should be triggered

The ship skill should summarise the changes it recognises
then update the docs
```ready to commit & push```

the workitem should be marked as done in the workload context file

if on a repo with a remote using github it should encourage a PR on a branch with comments added



