# 16. Pivot Candidate: Common ECU Hardware Health

## Why this pivot is needed

The previous direction focused on EPS-specific health indicators:

- gear / rack load proxy
- steering control effort
- assist current margin
- high-load low-speed steering stress
- durability before / after comparison

This direction is useful for an EPS-focused development evidence package.

However, as a business scheme, EPS-specific indicators may be too narrow.

The stronger commonization opportunity is:

> Move from EPS-mechanics-specific health indicators to ECU-common hardware health indicators.

In particular, power supply, smoothing components, electrolytic capacitors, temperature exposure, ripple stress, voltage margin, and brownout / reset history are more horizontally reusable across ECU products.

## Key insight

The issue is not that EPS indicators are technically wrong.

The issue is that EPS gear / rack indicators depend heavily on EPS-specific mechanics and vehicle steering behavior.

For wider business applicability, the target should shift toward hardware health themes that are common across ECUs.

```text
EPS-specific health
  -> useful but narrow

ECU-common power / hardware health
  -> more reusable across products, platforms, and customers
```

## Recommended reframing

### Before

> EPS Health Intelligence Package

### Intermediate

> EPS Development Evidence Package

### New broader frame

> Common ECU Hardware Health Layer

or

> ECU Power Health Evidence Package

The recommended near-term name is:

> ECU Power Health Evidence Package

Reason:

- It is not limited to EPS mechanics.
- It can apply to many ECU families.
- It is close to reliability, durability, diagnostic, and design-review concerns.
- It can start with development evidence and later connect to remote diagnostics / warranty evidence.

## First target component family

The first target should not be framed as a single component monitor.

### Avoid

> Electrolytic Capacitor Health Monitoring

This may sound like an existing component reliability / derating activity.

### Better

> ECU power health / lifetime margin evidence

The first indicator family can include:

- electrolytic capacitor stress
- DC-link / smoothing capacitor stress
- voltage ripple proxy
- ESR increase proxy
- capacitance degradation proxy
- thermal exposure
- load transient margin
- brownout / reset history
- power supply lifetime margin

## Why electrolytic capacitor / power supply health is a good first target

Electrolytic capacitors and power-supply smoothing components are attractive first targets because:

- degradation mechanisms are easier to explain than EPS gear / rack friction
- temperature and ripple-current stress can be modeled
- lifetime margin can be normalized by component rating
- similar concepts can apply across ECUs
- symptoms connect to resets, brownouts, voltage dips, and intermittent malfunction
- development, durability, diagnostics, and warranty teams can understand the value

The key is to avoid claiming direct degradation measurement unless the required sensing path exists.

For most existing ECUs, the practical first output should be a proxy indicator, not a direct ESR or capacitance measurement.

## Observable signals

Possible observable or derivable signals:

```text
supply_voltage
min_voltage
voltage_dip_count
voltage_ripple_proxy
load_current_proxy
temperature
operation_time
reset_count
brownout_count
watchdog_reset_history
power_on_cycle_count
high_load_event_count
thermal_exposure_time
```

Depending on ECU design, some signals may not be available.

The indicator set should clearly separate:

- directly measured signals
- derived proxy signals
- synthetic simulation signals
- unavailable but desirable signals

## Candidate indicator families

### 1. Thermal exposure indicator

Tracks accumulated exposure to high temperature.

```text
thermal_exposure_score = sum(f(temperature) * dt)
```

Use:

- lifetime margin review
- durability comparison
- component derating evidence

### 2. Ripple / load stress proxy

Tracks power-supply stress using load current, voltage ripple, or load-event proxies.

```text
ripple_stress_proxy = sum(load_current_proxy^2 * dt)
```

Use:

- capacitor stress proxy
- power supply stress comparison
- high-load operation analysis

### 3. Voltage margin indicator

Tracks how close the ECU power supply is to low-voltage or brownout conditions.

```text
voltage_margin = supply_voltage - minimum_required_voltage
```

Use:

- brownout risk review
- transient malfunction investigation
- external power-stress separation

### 4. Brownout / reset evidence

Tracks reset and voltage-dip history.

```text
power_abnormal_event_count = voltage_dip_count + brownout_count + unexpected_reset_count
```

Use:

- intermittent issue triage
- warranty / return-part evidence
- market-quality analysis

### 5. Lifetime margin proxy

Combines thermal exposure, load stress, and voltage stress into a normalized score.

```text
lifetime_margin_proxy = 1 - normalized_accumulated_stress
```

Use:

- development evidence
- design-review evidence
- health-ready ECU option

## Rating profile scaling

The same concept can be scaled by component or ECU rating.

Example profile:

```yaml
name: generic_12v_ecu_power_stage
rated_voltage_v: 16
minimum_operating_voltage_v: 6
rated_temperature_c: 105
rated_lifetime_hours: 5000
rated_ripple_current_a: 1.2
initial_esr_mohm: 80
capacitance_uf: 470
thermal_class: automotive_high_temp
```

Possible normalized indicators:

- normalized thermal exposure
- normalized ripple stress
- voltage margin ratio
- lifetime consumption proxy
- reset / brownout event rate

## Business scheme

This pivot improves the business scheme because the target becomes more reusable.

### Initial business

> ECU Power Health Evidence Package for development, durability, and design review.

### Buyer

- ECU platform development team
- hardware design team
- reliability engineering team
- diagnostic engineering team
- quality engineering team
- OEM application / proposal team

### Budget source

- development evaluation budget
- reliability / durability validation budget
- design review support budget
- quality improvement budget
- diagnostic concept development budget

### Later extension

> Common ECU Hardware Health Layer for diagnostics, warranty evidence, and vehicle health management.

## Why this is stronger than EPS-only business

### EPS-specific approach

Strength:

- concrete EPS domain story
- easy to connect to steering behavior and development evaluation

Weakness:

- narrow target
- depends on steering-specific signals
- hard to generalize across ECU families
- business scale may be limited

### Common ECU power health approach

Strength:

- horizontally reusable
- closer to common reliability concerns
- can apply to multiple ECUs
- easier to justify as platform capability
- can connect to diagnostics, warranty, and market quality

Weakness:

- may be perceived as existing reliability engineering
- direct component degradation measurement may require additional sensing
- value must be framed as evidence / margin / proxy, not magic prediction

## Recommended relationship to EPS work

The EPS work should not be discarded.

Instead, the project can use a two-layer story.

```text
Layer 1: Common ECU Hardware Health
  power health, capacitor stress, thermal exposure, voltage margin, reset evidence

Layer 2: Domain-specific Health Extensions
  EPS control effort, steering stress, rack / gear load proxy
```

This makes EPS a domain extension, not the entire product.

## Proposed repository direction

The repository can evolve from:

```text
steering-health-intelligence
```

into a broader concept:

```text
ECU health intelligence
  common hardware health layer
  + EPS domain extension
```

This can be handled in the current repository for now.

If the ECU-common direction becomes dominant, a future separate repository may be appropriate:

```text
ecu-power-health-evidence
ecu-health-intelligence
common-ecu-health-layer
```

## Updated product hierarchy

```text
L0: Common ECU Hardware Health Layer
  Cross-ECU health evidence and lifetime margin indicators.

L1: ECU Power Health Evidence Package
  Power supply, capacitor stress, voltage margin, thermal exposure.

L2: Domain-specific Health Extension
  EPS-specific control effort / steering stress indicators.

L3: Health-ready ECU Option
  Production ECU stores selected low-bandwidth health summaries.

L4: Connected Diagnostics / VHM Integration
  OEM service, warranty, market quality, and vehicle health use.
```

## What to validate next

### Technical validation

- Which ECU-common signals are already available?
- Can voltage dip, reset, temperature, and load proxies be stored cheaply?
- Can lifetime margin proxy be defined without additional hardware?
- Which indicators require additional sensing or design changes?

### Business validation

- Does hardware design / reliability engineering value a common evidence package?
- Can this be justified as development evidence rather than a new production feature?
- Can OEM design reviews benefit from common ECU power-health indicators?
- Is there a platform-level budget for common ECU health / diagnostic readiness?

### PoC validation

- Build a simple power health simulator.
- Define rating profiles for capacitor / power stage.
- Inject thermal and ripple stress scenarios.
- Generate synthetic voltage margin, ripple stress, and lifetime margin indicators.
- Produce a sample development evidence report.

## Summary

The project should not rely only on EPS-specific mechanics.

For stronger commonization and business scalability, it should add an ECU-common hardware health layer.

The first practical target is not simply `capacitor monitoring`, but:

> ECU power health / lifetime margin evidence.

EPS-specific indicators can remain as a domain extension.

This creates a more scalable structure:

```text
Common ECU Hardware Health Layer
  -> ECU Power Health Evidence Package
  -> EPS Domain Extension
  -> Health-ready ECU Option
  -> Connected Diagnostics / VHM Integration
```
