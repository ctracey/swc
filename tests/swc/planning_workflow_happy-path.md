# SWC Workflow Test Scripts

## SCENARIO: Planning workflow happy path
each workflow stage should confirm corrent interpretation with user
workflow progress should be displayed at the start of each phase
should report on satisfaction of stage exit criteria before moving to next workflow stage

### Trigger Skill (swc_workflow_plan)

```lets start a new project```

should trigger swc_workflow_plan

### Planning Workflow Stage: context
should check and encourage git branch & PR usage

```init a local repo and call the primary branch main```

should ask user about branch naming

```branch called feature/test-swc```


### Planning Workflow Stage: intent
should ask the user about the intent for this work

```I want to test that I can rapidly create a simple website```

should be considerate of user time and how much detail they want to go into

```understand enough so we can identify a task breakdown that supports a feedback loop```


### Planning Workflow Stage: solution

should check if user has direction for solution

```something that runs locally in the browser is good for this purpose. I want it to be a rambling of lorem ipsum but instead of lorem ipsum its douglas adams inspired content.```

```I need a title which is rapid demo, a subtitle which is the intent I just shared. then 3 sections, something about space, something about space ships, something about exploring```

```card column layout. needs to be a dark theme, something that fits with douglas adams books```

```single file distribution build using react```

should check if user would like to use relevant template (dependant on local skill for this template)

### Planning Workflow Stage: delivery
should ask user if they have direction on delivery strategy at high level
```scaffolding, header, section placeholders, content per section```


### Planning Workflow Stage: breakdown
 - for happy path it should prompt user to validate attempted breakdown
 - user should be able to provide feedback

### Planning Workflow Stage: finalise
should play back summary of plan, workfload and notes 
should display file path for documents so user can view full documents
should check if user has any feedback
