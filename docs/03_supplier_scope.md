# 03. Supplier Scope

## Why Scope Matters

Several earlier ideas were attractive but too OEM-dependent:

- OTA after-monitoring
- ADAS availability monitoring
- vehicle population risk triage
- regional / lot trend detection
- recall target narrowing

These are valuable but cannot be fully owned by an ECU supplier without OEM-side data.

Therefore, the project scope must be defined from the supplier's defensible position.

## Supplier Can See / Control

An ECU supplier can typically control or reason about:

- own ECU internal signals
- diagnostic design
- DTC definitions
- Freeze Frame contents
- Extended Data contents
- internal event counters
- NVM evidence
- software version
- calibration ID
- ECU-level production information, depending on process
- bench / HILS / internal evaluation logs
- limited logs shared by OEM during field issue analysis
- return part analysis evidence

## Supplier Cannot Assume Access To

An ECU supplier should not assume direct access to:

- all market vehicle logs
- always-on CAN logs
- OEM cloud telemetry
- warranty repair database
- customer complaints
- OTA campaign history
- regional usage context
- other ECU internal logs
- fleet operation data
- vehicle-level ADAS availability metrics

## Supplier-Appropriate Use Cases

### 1. Field issue analysis support

When OEM reports steering discomfort, EPS warning, DTC occurrence, or temporary assist reduction, ECU-side diagnostic evidence helps narrow suspected causes.

### 2. DTC root-cause assistance

DTC alone indicates what failed. Extended evidence helps understand why it may have failed.

Examples:

- low voltage context
- thermal limitation context
- current tracking context
- torque sensor redundancy deviation
- transient recovery history

### 3. DTC-below-threshold event memory

Not all important events become DTCs. Temporary events can be captured as counters or summary statistics for later analysis.

### 4. Return part NVM evidence

When returned parts are analyzed, internal counters and event histories provide clues about operating conditions and prior transient abnormalities.

### 5. Quality explanation

The supplier can explain that the ECU is designed not only to detect confirmed faults, but also to preserve diagnostic evidence useful for engineering analysis.

## Supplier-Inappropriate Claims

Avoid claiming:

- We can monitor OEM market fleet risk.
- We can detect OTA issues across the market.
- We can guarantee ADAS availability.
- We can narrow recall targets independently.
- We can predict individual vehicle failures.
- We can continuously analyze all market vehicles.

## Better Claim

> We provide ECU-side diagnostic evidence and suspected-cause hints that OEMs can combine with their own market data for field quality analysis.
