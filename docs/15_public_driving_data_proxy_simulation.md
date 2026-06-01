# 15. Public Driving Data Proxy Simulation

## Purpose

This note defines a practical PoC direction for `Steering Health Intelligence`.

The idea is to use public driving behavior data, such as Kaggle or other open driving datasets, as the external operating input, then generate synthetic EPS internal signals with a simplified proxy model.

The goal is not to reproduce a real EPS system exactly.

The goal is:

> Convert driving behavior data into synthetic EPS control-effort, stress, and margin indicators so that the Health Indicator workflow can be demonstrated before real EPS bench / HILS / vehicle logs are available.

## Why this is useful

Public datasets rarely contain EPS-internal signals such as:

- assist motor current
- target current
- actual current
- rack force
- torque sensor redundancy values
- assist limitation state
- thermal derating state

However, some public driving datasets may contain external driving behavior signals such as:

- vehicle speed
- steering angle
- steering angle speed
- lateral acceleration
- throttle
- brake
- yaw rate

These signals can be used as driving inputs for a simplified EPS proxy simulator.

This creates a bridge:

```text
public driving behavior data
  -> synthetic EPS internal signals
  -> health / stress / control-effort indicators
  -> sample report / dashboard
  -> later replacement with HILS, bench, or vehicle logs
```

## Important positioning

This simulation should be described as a proxy simulation, not as a physically validated EPS model.

### Avoid

> Reproduce actual EPS internal behavior from public driving data.

### Better

> Generate synthetic EPS internal signals for workflow validation using a simplified proxy model.

### English positioning

> A proxy simulator that converts driving behavior data into synthetic EPS control-effort, stress, and margin indicators.

The word `synthetic` is important.

It means the signals are generated for PoC and workflow validation, not measured from a real EPS.

## Input data assumption

Minimum useful input signals:

```text
timestamp
vehicle_speed
steering_angle
steering_angle_speed
```

Optional useful signals:

```text
lateral_acceleration
yaw_rate
brake
throttle
road_type
weather
```

If steering angle speed is missing, it can be estimated from steering angle time difference.

If lateral acceleration is missing, the first PoC can still proceed using speed and steering behavior only.

## Synthetic EPS signal generation concept

The simulator should use a layered structure.

```text
driving input
  -> steering demand model
  -> rack load proxy
  -> assist torque target model
  -> motor current target model
  -> motor current actual model
  -> thermal / tracking / margin model
  -> health indicator calculation
```

## Simplified model structure

### 1. Steering demand proxy

A simple steering demand proxy can be calculated from steering angle, steering angle speed, and vehicle speed.

Example concept:

```text
steering_demand =
    a * abs(steering_angle_speed)
  + b * abs(steering_angle)
  + c * low_speed_factor
  + d * rapid_reversal_factor
```

The exact formula is not important for the first PoC.

The important point is that low-speed steering and rapid steering reversal should increase demand.

### 2. Low-speed factor

Low-speed or parking-like steering tends to create higher assist demand.

Example:

```text
low_speed_factor = 1 / (vehicle_speed + k)
```

The factor should be clipped to avoid unrealistic explosion near zero speed.

### 3. Rack load proxy

Rack load can be represented as a proxy value.

```text
rack_load_proxy =
    steering_demand
  * tire_road_factor
  * friction_factor
```

Important factors:

- tire-road condition
- front axle load
- rack friction
- alignment
- temperature

For the first PoC, these can be simplified as scenario parameters.

### 4. Assist torque target

Assist torque target can be generated from rack load proxy and speed-dependent assist gain.

```text
assist_torque_target = assist_gain(vehicle_speed) * rack_load_proxy
```

The assist gain should generally be larger at low speed and smaller at high speed.

### 5. Motor current target

Motor current target can be derived from assist torque target and motor torque constant.

```text
motor_current_target = assist_torque_target / motor_torque_constant
```

The value should be normalized by rated current.

```text
normalized_current_target = motor_current_target / rated_motor_current
```

### 6. Motor current actual

Actual current can be modeled with a first-order lag and saturation.

```text
motor_current_actual = first_order_lag(motor_current_target)
```

Additional effects can be added later:

- voltage limitation
- thermal derating
- control delay
- current tracking degradation

### 7. Current tracking error

```text
current_tracking_error = motor_current_target - motor_current_actual
```

This can be used to generate a synthetic DTC-below-threshold warning count.

### 8. Thermal stress accumulation

Thermal stress can be approximated using current squared accumulation.

```text
thermal_load += motor_current_actual^2 * dt
```

A simple cooling term can be added later.

```text
thermal_load = thermal_load + heat_gain - cooling
```

### 9. Assist margin

Assist margin can be derived from rated current or rated assist torque.

```text
assist_margin = 1 - abs(motor_current_actual) / rated_motor_current
```

This is useful because it expresses how close the EPS is to its assumed rating.

## Rating profile scaling

The simulator should support rating profiles.

This allows the same driving data to be applied to different EPS classes.

Example compact vehicle profile:

```yaml
name: compact_vehicle_eps
rated_assist_torque_nm: 55
rated_motor_current_a: 70
rated_motor_temperature_c: 120
motor_torque_constant_nm_per_a: 0.08
thermal_time_constant_s: 300
nominal_voltage_v: 12
```

Example SUV profile:

```yaml
name: suv_vehicle_eps
rated_assist_torque_nm: 90
rated_motor_current_a: 120
rated_motor_temperature_c: 130
motor_torque_constant_nm_per_a: 0.09
thermal_time_constant_s: 420
nominal_voltage_v: 12
```

This makes it possible to compare normalized indicators such as:

- normalized assist current
- normalized assist torque
- assist margin
- thermal stress ratio

## Degradation profile injection

The simulator should support degradation profiles.

The same driving input can be replayed under multiple EPS conditions.

Example:

```yaml
healthy:
  friction_factor: 1.0
  current_tracking_delay_factor: 1.0
  voltage_margin_factor: 1.0

mild_friction_increase:
  friction_factor: 1.2
  current_tracking_delay_factor: 1.0
  voltage_margin_factor: 1.0

severe_friction_increase:
  friction_factor: 1.5
  current_tracking_delay_factor: 1.1
  voltage_margin_factor: 0.95
```

Expected behavior:

```text
same driving data
  + higher friction factor
  -> higher assist torque target
  -> higher motor current target
  -> higher thermal stress
  -> lower assist margin
  -> more current tracking warning events
```

This demonstrates the core project hypothesis:

> Mechanical degradation may be hidden from the driver by EPS control, but it can appear as increased control effort and reduced margin in internal indicators.

## Candidate indicators generated by this PoC

This proxy simulator can generate synthetic versions of existing candidate indicators.

| Existing ID | Indicator | Synthetic PoC support |
|---|---|---|
| EHI001 | assist_current_baseline_deviation | Strong |
| EHI002 | steering_torque_to_motor_current_ratio | Partial, if synthetic torque is generated |
| EHI003 | current_tracking_warning_count | Strong |
| EHI007 | thermal_derating_accumulation | Strong, as synthetic thermal load |
| EHI008 | low_voltage_stress_history | Partial, if voltage scenario is injected |
| EHI009 | assist_limitation_recurrence | Partial, through saturation / derating |
| EHI010 | high_load_low_speed_event_count | Strong |
| EHI011 | rapid_reversal_high_load_count | Strong |

Sensor redundancy indicators such as torque sensor redundancy delta should not be generated from public driving data unless a separate sensor fault injection model is added.

## Recommended first demo

### Scenario

Use the same driving data under three simulated EPS conditions.

```text
1. healthy EPS
2. mild rack friction increase
3. severe rack friction increase
```

### Output indicators

Generate and compare:

- normalized assist current
- assist current baseline deviation
- thermal stress accumulation
- current tracking warning count
- high-load low-speed event count
- assist margin

### Expected result

```text
healthy EPS
  -> lower normalized current
  -> lower thermal stress
  -> higher assist margin

mild friction increase
  -> moderate current increase
  -> moderate thermal stress increase
  -> small margin decrease

severe friction increase
  -> high current increase
  -> high thermal stress accumulation
  -> more warning events
  -> lower assist margin
```

## Suggested repository structure

```text
sim/
  eps_proxy_model.py
  eps_indicator_calculator.py
  rating_profiles.yml
  degradation_profiles.yml

notebooks/
  eps_indicator_simulation_demo.ipynb

reports/
  sample_eps_indicator_report.md

data/
  input/
    driving_sample.csv
  synthetic/
    eps_synthetic_signals.csv
```

## What this PoC proves

This PoC can prove:

- The workflow can convert driving data into EPS-like indicator data.
- Rating profiles can scale the same driving behavior across EPS classes.
- Degradation profiles can show interpretable indicator changes.
- Health indicator reports can be generated before real EPS logs are available.
- The project can move from abstract market discussion to an executable demo.

## What this PoC does not prove

This PoC does not prove:

- Real EPS internal signal accuracy.
- Real rack friction estimation accuracy.
- Real failure prediction performance.
- Production-ready threshold values.
- OEM acceptance.
- Warranty or service decision validity.

These require HILS, bench, durability, or real vehicle logs.

## Validation path after PoC

Recommended validation sequence:

```text
Step 1: Public driving data + proxy simulation
  Validate workflow and reporting shape.

Step 2: Synthetic controlled driving cycles
  Validate indicator response to known injected degradation.

Step 3: HILS / bench logs
  Replace synthetic internal signals with measured EPS-side signals.

Step 4: Durability before / after logs
  Check whether indicators respond to real aging or stress.

Step 5: Vehicle test logs
  Validate robustness under tire, road, temperature, and driver variation.
```

## Business relevance

This PoC supports the `EPS Development Evidence Package` business scheme.

It helps demonstrate:

- how control effort indicators can be generated
- how degradation-like scenarios affect the indicators
- how rating-based normalization can compare different EPS classes
- how reports can support development evaluation and OEM design review

The first commercial story should remain:

> Development and design-review evidence, not production failure prediction.

## Summary

Public driving datasets are unlikely to contain real EPS internal signals.

However, they can still be useful as external driving inputs.

By adding a simplified EPS proxy simulator, the project can generate synthetic internal signals and demonstrate the complete health indicator workflow.

This approach is useful for early PoC, as long as it is clearly labeled as synthetic and proxy-based.

The key message is:

> Use public driving data to demonstrate the workflow; use HILS, bench, and vehicle logs later to validate EPS-specific accuracy.
