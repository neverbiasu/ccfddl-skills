# Domain-to-Category Mapping

Upstream `ccfddl` has no native "domain" label (e.g. "Computer Vision"). It
organises conferences by technical **categories** (`AI`, `CG`, `MX`, ...).
This reference documents how an agent can map a research domain to one or more
upstream categories.

## Principle

Domain labels are **not** upstream native categories. They are a convenience
layer that helps users who think in terms of their research field rather than
ccfddl categories. The mapping is deterministic (keyword-driven) and does **not**
involve semantic matching of paper titles or abstracts.

## Mappings

| Domain            | Primary Categories | Optional Category | Rationale |
|-------------------|--------------------|-------------------|-----------|
| CV                | `AI`, `CG`, `MX`   | —                 | CV spans AI venues (CVPR, ICCV, ECCV), CG venues (SIGGRAPH), and mixed (ACM MM). |
| Computer Vision   | `AI`, `CG`, `MX`   | —                 | Alias for CV. |
| Image Editing     | `AI`, `CG`         | `MX`              | Deep learning models land in AI; rendering/graphics techniques in CG; multimedia applications may also fit MX. |
| Relighting        | `AI`, `CG`         | `MX`              | Same logic as Image Editing. |

When the user's domain is not listed, the agent should fall back to structured
filters (category, rank, status, deadline window) and note the absence of a
domain preset.

## How to Explain Mapping Uncertainty to the User

- **State the mapping explicitly**: "Computer Vision is not a native ccfddl
  category. The recommended categories are AI, CG, and MX."
- **Explain inclusion rationale**: "AI covers vision conferences (CVPR, ICCV,
  ECCV). CG covers computer graphics venues (SIGGRAPH, Eurographics). MX
  captures multimedia conferences (ACM MM) that also publish vision work."
- **Let the user refine**: after seeing results, the user can add or remove
  categories with `--category`.

## User Scenarios

### Scenario 1: Computer Vision

> "我做计算机视觉，有哪些会议可以投？"

Agent action:

```
list --domain cv --status open --within-days 180 --format json
```

The agent maps `cv` → `AI, CG, MX`, fetches open conferences in those
categories, and presents the results sorted by nearest deadline. It notes
that domain mapping is a convenience layer, not a native ccfddl category.

### Scenario 2: Image Editing

> "我做 Image Editing，有哪些会议可以考虑？"

Agent action:

```
list --domain image-editing --status open --within-days 180 --format json
```

The agent maps `image-editing` → `AI, CG` (primary) and optionally adds
`MX` if the user's work touches multimedia. It explains the choice:
"Image editing papers primarily appear in AI venues (deep learning methods)
or CG venues (shader/graphics techniques)."

### Scenario 3: Relighting

> "我做 Relighting，有哪些会议可以考虑？"

Agent action:

```
list --domain relighting --status open --within-days 180 --format json
```

The agent maps `relighting` → `AI, CG` (primary) with optional `MX`.
It explains: "Relighting research spans AI (learning-based methods) and
CG (physically based rendering). Add --category MX if your work has a
multimedia angle."

## What This Reference Does NOT Do

- It does not modify the upstream ccfddl data.
- It does not add a "domain" field to any conference entry.
- It does not perform semantic matching against paper titles or abstracts.
- It does not guarantee that every conference in the mapped categories
  publishes work in the given domain.
