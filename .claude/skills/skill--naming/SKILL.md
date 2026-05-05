---
name: skill--naming
description: SWC skill naming convention — separator rules for objects, actions, knowledge, and typed objects. Use when creating a new skill or reviewing an existing skill name.
---

# SWC Skill Naming Convention

Skill names are structured identifiers that encode the object model. Each separator has a distinct meaning.

## Separators

| Separator | Meaning | Relationship |
|---|---|---|
| `_` | sub-object | has-a (descending into the hierarchy) |
| `-` | action attribute | the skill *does* something to the object |
| `--` | knowledge attribute | the skill *describes* the object (reference material) |
| camelCase | typed object | is-a (this is a named type of the parent object) |

## Structure

```
<object> _ <sub-object> - <action>
<object> -- <knowledge>
<typedObject> _ <stage>
```

## Examples

```
context-init          context object → init action
context-lookup        context object → lookup action
context--files        context object → files knowledge
context--workload     context object → workload knowledge

workload-update       workload object → update action
workload_item-start   workload → item sub-object → start action

workflowDemo          workflowDemo (demo is-a workflow)
workflowDemo_start    workflowDemo → start stage (has-a)
workflowDemo_middle   workflowDemo → middle stage (has-a)
workflowDemo_end      workflowDemo → end stage (has-a)
```

## Alphabetical ordering

Single dash (`-`) sorts before double dash (`--`), so within any object's skills, actions appear above knowledge in a sorted list. This is intentional — actions are the common case; knowledge is reference material you scroll down to find.

## Rules of thumb

- If the skill *does* something → `-`
- If the skill *explains* something → `--`
- If the concept is a named type of a parent object → camelCase the compound (e.g. `workflowDemo`)
- If an object *has* something → `_` to descend
- Stage skills always use `_` — a workflow has stages, stages are not actions on the workflow
