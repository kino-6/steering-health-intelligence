# 06. Next Actions

## Immediate Next Actions

### 1. Decide repository name

Recommended:

```text
steering-diagnostic-evidence
```

Alternative:

```text
steering-health-intelligence
eps-diagnostic-intelligence
steering-risk-intelligence
```

### 2. Commit current docs

Suggested initial commit message:

```text
docs: add steering diagnostic evidence concept notes
```

### 3. Create an issue list

Suggested GitHub issues:

1. Define target field issue scenarios
2. List candidate diagnostic evidence signals
3. Define DTC-below-threshold event counters
4. Draft suspected cause categories
5. Create data dictionary template
6. Estimate ECU resource impact
7. Design offline validation using HILS / bench logs
8. Rewrite project charter for OEM-facing proposal

## Suggested Issue Details

### Issue 1: Define target field issue scenarios

Goal:

- Identify realistic EPS / steering field issue cases where DTC alone is insufficient.

Examples:

- temporary assist reduction
- EPS warning with no reproducible symptom
- motor current deviation DTC
- torque sensor plausibility DTC
- low voltage related event
- thermal limitation event

### Issue 2: List candidate diagnostic evidence signals

Goal:

- List ECU internal signals useful for cause analysis.

Candidate columns:

- signal name
- physical meaning
- unit
- sampling / update condition
- storage condition
- suspected cause relevance
- resource cost

### Issue 3: Define DTC-below-threshold event counters

Goal:

- Define events that do not become DTCs but are useful for analysis.

Examples:

- current tracking deviation warning count
- torque sensor redundancy warning count
- low voltage assist limitation count
- thermal derating count
- transient abnormal recovery count

### Issue 4: Draft suspected cause categories

Goal:

- Define non-deterministic cause categories for engineering review.

Candidate categories:

- power supply related
- thermal limitation related
- motor current tracking related
- sensor redundancy related
- transient event likely
- persistent degradation tendency
- external factor suspected
- additional data required

### Issue 5: Create data dictionary template

Goal:

- Standardize interpretation of diagnostic evidence.

Columns:

- name
- description
- unit
- valid condition
- invalid condition
- update condition
- reset condition
- related DTC
- suspected cause category
- interpretation caution

### Issue 6: Estimate ECU resource impact

Goal:

- Estimate CPU, RAM, NVM, and diagnostic payload impact.

Need to consider:

- counter width
- write frequency
- NVM endurance
- reset policy
- diagnostic readout time
- integration with existing DEM / DCM concepts

### Issue 7: Design offline validation

Goal:

- Validate that proposed evidence helps separate known abnormal modes.

Data sources:

- HILS logs
- bench logs
- fault injection
- environmental test logs
- historical issue logs, if available

### Issue 8: Rewrite OEM-facing proposal

Goal:

- Convert internal concept into OEM-facing short proposal.

Structure:

1. Problem: DTC alone is insufficient for fast field issue analysis
2. Proposal: diagnostic evidence package
3. Value: faster suspected-cause classification
4. Scope: ECU-side evidence, not fleet monitoring
5. Roadmap: future OEM-side market trend analysis

## Suggested Roadmap

```text
Milestone 1:
  Concept notes and issue list

Milestone 2:
  Candidate evidence signal list

Milestone 3:
  Data dictionary draft

Milestone 4:
  Offline validation plan

Milestone 5:
  OEM-facing project charter

Milestone 6:
  Prototype analysis notebook or CLI
```

## Optional Prototype Idea

A small Python tool could be built later:

```text
input:
  CSV log / diagnostic snapshot

output:
  suspected cause category
  evidence summary
  missing data suggestions
```

This would demonstrate that the proposal is more than "provide more logs".

Possible name:

```text
steering-evidence-analyzer
```
