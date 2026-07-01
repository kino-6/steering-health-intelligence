---
name: future-need-interviewing
description: Use this skill when Codex needs to deepen customer needs, market pain, business model hypotheses, product requirements, or interview questions by mapping the customer's current stated need, worst future, best future, desired emotion, and underlying true need. Trigger it for customer discovery, hearing/interview design, "who is happy?", "what does the market want?", feature value validation, and cases where a proposed solution may be technically interesting but commercially weak.
---

# Future Need Interviewing

## Overview

Use the hearing matrix to move from a shallow stated need to a concrete business-relevant need. Explore both emotional range and future time horizon before proposing features, demos, or business models.

The core principle:

> Need resolution increases when you ask about the first need, the worst future, the best future, and the emotion the customer wants to feel.

## Workflow

### 1. Identify the stated need

Capture the user's first stated need without over-interpreting it.

Ask or infer:

- What do they say they want now?
- What job are they trying to complete?
- What current workaround do they use?
- Who owns the problem and budget?

Do not stop here. This is usually the lowest-resolution need.

### 2. Explore the worst future

Ask what happens if the problem continues for 5-10 years or at the next major program milestone.

Use prompts like:

- If nothing changes, what gets worse?
- What cost, delay, blame, risk, or lost opportunity accumulates?
- Who gets pulled into the pain later?
- What would make this politically or commercially painful?

Look for negative emotions: fear, embarrassment, blame, uncertainty, wasted work, loss of trust, slow escalation, audit pain.

### 3. Explore the best future

Ask what the customer would feel or be able to do if the ideal outcome became true.

Use prompts like:

- If this worked extremely well, what changes?
- What would become faster, easier, safer, or more defensible?
- What emotion would they want to feel: relief, confidence, control, pride, freedom, trust?
- What would they be able to tell their boss, customer, OEM, supplier, or auditor?

Look for positive emotions and business outcomes, not only functional outputs.

### 4. Infer the true need

Translate the gap between worst future and best future into the underlying need.

Good true needs are specific enough to drive product decisions:

- Bad: "They need more logs."
- Better: "They need evidence that reduces NTF investigation time and makes OEM responses defensible."
- Bad: "They want AI prediction."
- Better: "They want earlier confidence about where to investigate without accepting false liability."

### 5. Convert into product and business hypotheses

For each true need, produce:

- Buyer / user
- Pain owner
- Current workaround
- Worst future
- Best future
- Desired emotion
- True need
- Proposed offer
- Evidence required
- Why existing tools are insufficient
- Budget path
- Validation question
- Demo that would prove value

## Output Template

Use this compact table when exploring a new hypothesis:

| Field | Answer |
|---|---|
| Stated need | |
| Current workaround | |
| 5-10 year worst future | |
| Best future | |
| Desired emotion | |
| True need | |
| Buyer / user | |
| Budget path | |
| Proposed offer | |
| Proof demo | |
| Kill criteria | |

## Interview Prompts

Use these questions when designing customer interviews:

1. What made this problem worth discussing now?
2. What happens if this remains unsolved through the next program, audit, warranty cycle, or customer review?
3. What would be embarrassing or expensive if the issue repeats?
4. If the ideal tool existed, what would you be able to say with confidence?
5. What emotion would a good solution give you: relief, control, trust, speed, defensibility, freedom, or something else?
6. What evidence would make the answer credible to your customer or internal approver?
7. What do you use today, and where does it break?
8. Who pays when this goes wrong?
9. Who benefits if the problem is solved?
10. What result would make you stop caring about this solution?

## Quality Bar

Reject shallow outputs that only restate the proposed feature.

Before finalizing, check:

- Does the answer name a specific buyer or user?
- Does it distinguish technical interest from business value?
- Does it include a negative future and a positive future?
- Does it name the emotion the customer wants?
- Does it produce a falsifiable validation question?
- Does it say when the idea is weak or not worth pursuing?

For this repository, prefer EPS supplier and ECU supplier realities over OEM-owned data assumptions unless the user explicitly asks for future optional extensions.
