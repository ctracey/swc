---
name: swc_skill--naming
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
swc _ <object> _ <sub-object> - <action>
swc _ <object> -- <knowledge>
swc _ <typedObject> _ <stage>
```

## Examples

```
swc_context-init          swc → context object → init action
swc_context-lookup        swc → context object → lookup action
swc_context--files        swc → context object → files knowledge
swc_context--workload     swc → context object → workload knowledge

swc_workload-update       swc → workload object → update action
swc_workload_item-start   swc → workload → item sub-object → start action

swc_workflowDemo          swc → workflowDemo (demo is-a workflow)
swc_workflowDemo_start    swc → workflowDemo → start stage (has-a)
swc_workflowDemo_middle   swc → workflowDemo → middle stage (has-a)
swc_workflowDemo_end      swc → workflowDemo → end stage (has-a)
```

## Alphabetical ordering

Single dash (`-`) sorts before double dash (`--`), so within any object's skills, actions appear above knowledge in a sorted list. This is intentional — actions are the common case; knowledge is reference material you scroll down to find.

## Rules of thumb

- If the skill *does* something → `-`
- If the skill *explains* something → `--`
- If the concept is a named type of a parent object → camelCase the compound (e.g. `workflowDemo`)
- If an object *has* something → `_` to descend
- Stage skills always use `_` — a workflow has stages, stages are not actions on the workflow
