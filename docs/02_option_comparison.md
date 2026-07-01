# 02. Option Comparison

## Summary Table

| Option | Market Business Fit | Supplier Feasibility | OEM Dependency | Interest | Current Verdict |
|---|---:|---:|---:|---:|---|
| End-user Fault Warning | Low | Medium | Medium | Low | Avoid |
| Fleet EPS Prediction | Low-Medium | Low | Medium | Low | Not main target |
| OEM Market Quality Monitoring | High | Low-Medium | High | High | Future extension |
| OTA / ADAS Safety Monitoring | Medium-High | Low | High | High | Future extension |
| Diagnostic Evidence Package | Medium | High | Medium | Medium | Current main proposal |
| Development / HILS Quality AI | Low as market service | High | Low | Medium | Separate project |

## Key Evaluation Points

### 1. EPS prediction has low frequency value

Fleet operators pay for frequent operational pain points. EPS failures are likely too rare to justify standalone subscription value.

### 2. EPS has high severity value

Although frequency is low, steering-related issues can have large safety, recall, warranty, and brand impact.

### 3. OEM is the natural customer for high-severity, low-frequency risks

OEM can view all market vehicles as a mega fleet. However, OEM-side data and infrastructure are required.

### 4. ECU supplier cannot own OEM-wide risk triage

ECU supplier generally cannot see:

- all vehicle logs
- OTA deployment history
- regional usage context
- warranty repair data
- customer complaints
- vehicle-level ADAS behavior
- other ECU data

Therefore, supplier-side proposal must stay within the area where the supplier has evidence and responsibility.

### 5. Supplier-side value is diagnostic evidence

The realistic value proposition is:

> Provide deeper ECU-side diagnostic evidence so that OEM / Tier1 teams can perform faster and better field issue analysis.

## Reframed Value Chain

```text
ECU Supplier
  provides:
    - internal counters
    - DTC-adjacent evidence
    - Freeze Frame / Extended Data
    - cause-candidate hints
    - data dictionary

OEM
  combines with:
    - vehicle data
    - warranty data
    - complaints
    - OTA records
    - production information
    - market region

OEM / Tier1 together
  use it for:
    - field issue analysis
    - suspected cause classification
    - faster engineering review
    - future trend monitoring
```

## Recommended Positioning

Avoid:

> We can predict EPS failures in the market.

Prefer:

> We provide steering ECU diagnostic evidence that improves field issue analysis and enables future OEM-side risk monitoring.

Best current phrasing:

> Steering Diagnostic Evidence Package for OEM / Tier1 field issue analysis.
