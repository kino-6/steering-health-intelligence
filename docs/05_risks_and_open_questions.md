# 05. Risks and Open Questions

## Major Risks

### 1. It may still look like "more logs"

Even after reframing, the proposal can still be perceived as:

> We provide more data.

To avoid this, the proposal must emphasize:

- faster field issue analysis
- suspected cause classification
- better DTC explanation
- return part evidence
- engineering review support

### 2. OEM may not value it

If the OEM does not have a strong pain point in field issue analysis, the feature may look like extra cost.

Potential mitigations:

- focus on cases where DTC alone is insufficient
- show example investigation flow
- demonstrate reduced analysis time
- connect to quality explanation and warranty discussion

### 3. It can be misunderstood as fault prediction

DTC-below-threshold counters and health indicators may be interpreted as predictive failure warnings.

Mitigation:

- avoid terms like failure prediction and RUL in the core proposal
- use diagnostic evidence, suspected cause, engineering review
- explicitly state non-goals

### 4. ECU resource constraints

Adding counters, NVM evidence, and Extended Data consumes resources.

Need to evaluate:

- CPU cost
- RAM cost
- NVM cost
- write endurance
- communication payload
- diagnostic readout time

### 5. Evidence may not separate failure modes

Some indicators may not clearly distinguish between true abnormality and normal variation.

Need validation using:

- HILS
- bench tests
- fault injection
- environmental tests
- historical logs

### 6. Responsibility expansion

If the supplier provides more evidence or suspected-cause hints, responsibility boundaries may become sensitive.

Mitigation:

- present outputs as engineering review support
- avoid automated warranty / safety judgment
- define interpretation cautions in data dictionary

## Open Questions

### Business

- Who is the actual buyer inside OEM?
  - quality assurance?
  - market quality?
  - diagnostic engineering?
  - EPS system owner?
  - service engineering?
- Is this paid as NRE, unit price uplift, or diagnostic feature package?
- Does OEM currently struggle with EPS field issue analysis?
- Are there known cases where DTC alone was insufficient?

### Technical

- Which internal signals are already available in the ECU?
- Which signals can be stored without safety impact?
- What NVM budget is realistic?
- What update/reset policy is acceptable?
- Can DTC-below-threshold events be standardized?
- What fault modes can be simulated or injected?

### Data / Validation

- Are HILS or bench logs available?
- Are historical field issue logs available?
- Are return part NVM dumps available?
- Can we compare cases with and without additional evidence?
- Can suspected-cause classification be validated offline?

### Product Positioning

- Should the name emphasize evidence, intelligence, or risk?
- Is "Diagnostic Evidence" too conservative?
- Is "Risk Intelligence" too ambitious?
- Should the first proposal be framed as a diagnostic design improvement rather than AI?

## Current Leaning

Use conservative external positioning:

> Steering Diagnostic Evidence Package

Use aspirational internal roadmap:

> Steering Risk Intelligence
