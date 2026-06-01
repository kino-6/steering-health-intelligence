---
name: chain-of-verification
description: Use this skill when Codex needs to verify its own research, business hypotheses, technical claims, market conclusions, article drafts, strategy memos, or requirements before presenting or committing them. Trigger it for hallucination-prone tasks, source-backed analysis, "is this true?", "what are we assuming?", market research, competitor research, EPS/ECU business-model exploration, and any conclusion that should be checked against evidence rather than accepted from a first-pass answer.
---

# Chain Of Verification

## Overview

Use Chain-of-Verification to force a draft answer through adversarial evidence checks before producing a final answer. The goal is not to sound certain; it is to separate supported conclusions, weak assumptions, unknowns, and corrected claims.

For this repository, use this skill whenever a market, business, or EPS/ECU diagnostic conclusion might otherwise drift into plausible but unsupported strategy talk.

## Workflow

### 1. Draft the answer

Create a concise first-pass answer or hypothesis.

Mark it explicitly as draft when useful.

### 2. Extract risky claims

Identify claims that could be wrong, overstated, underspecified, or outside available evidence.

Prioritize:

- factual claims
- market-size or demand claims
- "customers want X" claims
- "this is new" or "already exists" claims
- technical feasibility claims
- ownership or responsibility claims
- causal claims
- claims that would change the recommended strategy

### 3. Convert risks into verification questions

Create 5-10 pointed questions.

Good questions are falsifiable:

- Bad: "Is this good?"
- Good: "Is ECU event memory already covered by AUTOSAR DEM / UDS?"
- Bad: "Do customers care?"
- Good: "Which role owns budget or workflow pain for this problem?"
- Bad: "Can EPS suppliers do this?"
- Good: "Which parts require OEM-owned warranty DB, service tools, or diagnostic approval?"

### 4. Answer each question with evidence

Use the strongest available evidence.

Preferred order:

1. User-provided facts and repo documents
2. Primary standards, official docs, papers, filings, or vendor documentation
3. Market pages, credible reports, or public examples
4. Reasoned inference clearly labeled as inference

When external facts matter, browse or use available research tools. When browsing is not available or not needed, state the evidence boundary.

For each answer, label confidence:

- High: directly supported by source or local evidence
- Medium: supported but context-dependent
- Low: plausible inference or incomplete evidence
- Unknown: cannot be determined from available evidence

### 5. Repair the draft

Revise the draft based on verification.

Required repairs:

- remove unsupported claims
- soften overconfident claims
- split "known" from "assumed"
- name OEM / supplier / user boundaries explicitly
- convert vague value claims into stakeholder-specific value
- add kill criteria when an idea may be weak
- preserve useful negative conclusions

### 6. Produce the final answer

The final answer should include:

- Final conclusion
- What changed after verification
- Evidence-backed claims
- Remaining assumptions / unknowns
- Next verification step

Do not include a long self-dialogue unless the user asks for it. Keep the verification useful, not theatrical.

## Output Template

Use this structure for research or strategy work:

```markdown
## Draft
...

## Verification Questions
1. ...
2. ...

## Evidence Checks
| Question | Evidence | Confidence | Impact on draft |
|---|---|---:|---|
| ... | ... | High/Medium/Low/Unknown | Keep / revise / remove |

## Corrected Conclusion
...

## Still Unknown
- ...

## Next Check
- ...
```

For concise user-facing answers, collapse the template into:

```markdown
結論:
...

検証で修正した点:
- ...

まだ仮説:
- ...
```

## Repo-Specific Guidance

For EPS / ECU business-model exploration:

- Treat "ECU-local evidence" as suspicious until checked against existing DTC, freeze frame, extended data, DEM, UDS, and NvM patterns.
- Do not claim OEM demand from generic warranty market evidence. Separate workflow pain from EPS-specific proof.
- Separate OEM-owned domains from supplier-owned domains.
- Treat "20-50 case classification" as an internal primary research step, not an external-market-research result.
- Prefer "customer quality report / return-part analysis / NTF investigation / D2-D4 fact summary" over broad claims like "8D automation."
- Always include kill criteria for business ideas.

## Quality Bar

Before finalizing, ask:

- Which claims would embarrass us if false?
- What would a skeptical OEM or EPS supplier reject?
- Which facts are already standard industry practice?
- What requires internal data that public research cannot provide?
- What is the strongest reason this idea may not be valuable?
- What decision becomes possible after this analysis?
