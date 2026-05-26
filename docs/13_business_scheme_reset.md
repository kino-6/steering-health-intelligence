# 13. Business Scheme Reset

## Why this reset is needed

The current technical hypothesis is reasonable:

> EPS ECU signals can be used to define health / stress / control-effort indicators.

However, the business scheme is still weak.

The main issue is not whether the indicators are technically interesting.

The main issue is:

> Who pays for this, from which budget, and why now?

A useful indicator set does not automatically become a sellable product.

## Current weakness

The current `EPS Health Intelligence Package` concept has several business-side weaknesses.

### 1. Payer is unclear

The repo currently identifies:

- Primary value target: EPS system / gear supplier
- Required gatekeeper: Vehicle OEM

This is structurally correct, but it creates a business problem.

The party that can benefit from the indicators is not always the party that controls production adoption, vehicle data access, or connected diagnostics integration.

In short:

```text
EPS / gear supplier may want the value.
Vehicle OEM controls adoption and data access.
```

This makes production-scale monetization difficult unless the value is translated into an OEM-facing specification, option, or development-review benefit.

### 2. Development usefulness does not automatically become revenue

Development and durability indicators may be useful for engineering teams.

However, usefulness inside development does not directly imply:

- additional piece price
- production option revenue
- service revenue
- warranty cost reduction
- fleet maintenance revenue

If the first value is development evaluation, the first sellable unit should also be framed as development evaluation support, not as a full production health-intelligence business.

### 3. EPS-only predictive maintenance is weak as a standalone story

EPS failures are generally not frequent enough to make EPS-only predictive maintenance an obvious first business.

Leading with individual RUL, end-user notification, or fleet monitoring creates difficult questions:

- How often does the target failure occur?
- How much downtime or warranty cost is avoided?
- Who is responsible for false positives?
- Who owns the vehicle data?
- Who operates the monitoring workflow?

Therefore, EPS-only failure prediction should remain a later-stage or downstream use case.

### 4. `Health Intelligence` sounds bigger than the first proof point

`EPS Health Intelligence Package` is a useful long-term concept.

But as a first business object, it may sound too close to:

- production health monitoring
- connected vehicle data business
- RUL prediction
- warranty decision automation
- end-user notification

The first proof point should be narrower and closer to an existing budget.

## Revised business scheme

The business should be staged.

```text
L1: EPS Development Evidence Package
  Development / bench / durability evaluation support.

L2: OEM Design Review Add-on
  Evidence package for OEM proposal, design review, and durability explanation.

L3: Health-ready EPS Option
  Production EPS carries selected low-bandwidth health / stress summary indicators.

L4: Connected Diagnostics / VHM Integration
  OEM health platform, remote diagnostics, service, warranty, and market-quality use.
```

This changes the initial sellable object from a broad health-intelligence concept to a practical evidence package.

## First sellable unit

### Recommended first product framing

> EPS Development Evidence Package

Alternative names:

- EPS Control Effort Evaluation Package
- EPS Gear/Rack Stress Evaluation Kit
- EPS Durability Indicator Package
- Health-ready EPS Evidence Kit

The recommended name is:

> EPS Development Evidence Package

Reason:

- It is close to existing development and evaluation budgets.
- It does not overpromise production prediction.
- It can produce concrete deliverables.
- It can later become the evidence base for a health-ready EPS option.

## Target buyer and budget source

### Initial buyer

```text
EPS system supplier / gear supplier development organization
```

Possible internal users:

- EPS system development team
- gear / rack design team
- bench evaluation team
- durability evaluation team
- diagnostic engineering team
- quality engineering team
- OEM proposal / application engineering team

### Budget source

More plausible first budgets:

- development evaluation budget
- durability test budget
- OEM proposal support budget
- design review support budget
- quality improvement budget
- diagnostic concept development budget

Less plausible first budgets:

- end-user service revenue
- fleet monitoring revenue
- OTA platform revenue
- warranty automation budget
- individual RUL prediction budget

## What the first package contains

The first package should not be sold as AI failure prediction.

It should be sold as evidence and evaluation support.

Possible contents:

- gear / rack design A/B comparison indicators
- control effort comparison under matched steering conditions
- durability before / after indicator comparison
- high-load low-speed stress accumulation
- thermal / voltage / current-tracking stress view
- false-positive factor list
- indicator dictionary
- HILS / bench / durability validation plan
- OEM-facing evidence summary

## Business value logic

### Development-side value

The first value is not:

> Predict when EPS will fail.

The first value is:

> Make EPS mechanical behavior, control effort, stress, and margin more observable during development and evaluation.

Expected benefits:

- faster gear / rack design comparison
- clearer durability before / after explanation
- stronger OEM design review evidence
- reduced ambiguity in bench / HILS / vehicle evaluation
- reusable indicator definitions for future production diagnostics
- foundation for later health-ready EPS proposal

### OEM-facing value

The OEM-facing message should be:

> This EPS is designed with measurable health / stress / control-effort indicators that are validated during development and can be reused for diagnostics and future vehicle health management.

This is safer than:

> This EPS predicts failures.

## Business model options

### Option A: Evaluation service / engineering package

Sell as a project-based service or internal engineering package.

Revenue model:

- one-time evaluation project
- benchmark report
- HILS / bench / durability analysis package
- engineering consulting

Strength:

- easiest to start
- does not require production adoption
- can use existing logs and tests

Weakness:

- limited scalability
- may remain engineering support rather than product revenue

### Option B: OEM proposal add-on

Use the package to strengthen EPS proposals to OEMs.

Revenue model:

- bundled into EPS development proposal
- application engineering value-add
- differentiated design-review evidence

Strength:

- supports actual product acquisition
- easier to justify internally than standalone software sales

Weakness:

- hard to directly price
- value may appear as win-rate improvement rather than explicit revenue

### Option C: Production health-ready EPS option

Embed selected indicators into production EPS as a low-bandwidth health summary.

Revenue model:

- feature option
- software-enabled value-add
- diagnostic feature package

Strength:

- scalable if adopted
- connects to OEM VHM / service / diagnostics

Weakness:

- needs OEM specification and approval
- data ownership and responsibility become heavy
- false-positive handling must be designed carefully

### Option D: Connected diagnostics / VHM plugin

Provide EPS-specific health logic to an OEM or SDV / connected vehicle platform.

Revenue model:

- software logic license
- platform plugin
- analytics module

Strength:

- potentially scalable
- aligns with SDV / vehicle health trends

Weakness:

- too far for the first proof point
- requires ecosystem access
- EPS-only value may be too narrow

## Recommended path

The recommended sequence is:

```text
Step 1: EPS Development Evidence Package
  Prove usefulness in development, bench, durability, and design comparison.

Step 2: OEM Design Review Add-on
  Convert the evidence into OEM-facing proposal and review material.

Step 3: Health-ready EPS Option
  Select robust indicators for production storage and diagnostic readout.

Step 4: Connected Diagnostics / VHM Integration
  Connect selected EPS health summaries to OEM service, warranty, market-quality, and VHM workflows.
```

## What must be validated next

The next validation questions should be business questions, not only technical questions.

### Buyer validation

- Which team has an explicit pain that this solves?
- Which team owns the budget?
- Is the budget development, quality, warranty, diagnostic, or OEM proposal budget?
- Would this be bought as a tool, service, report, option, or embedded feature?

### Value validation

- Does this shorten design comparison?
- Does this reduce durability evaluation ambiguity?
- Does this improve OEM explanation quality?
- Does this help turn tacit expert judgment into reusable evidence?
- Does this reduce re-test, root-cause analysis, or cross-team negotiation cost?

### Adoption validation

- Can the package be used before production adoption?
- Can it work with existing ECU logs or bench data?
- Does it require OEM vehicle data permission?
- Can it be piloted on one product / platform / test condition?

### Monetization validation

- Can it be priced as an engineering evaluation package?
- Can it become part of an EPS development proposal?
- Can selected indicators become a production software option?
- Can the same indicator dictionary be reused across programs?

## Positioning statement

### Avoid

> EPS failure prediction AI.

### Better

> EPS Development Evidence Package for control-effort, stress, and margin evaluation.

### Long-term

> Health-ready EPS option for future connected diagnostics and vehicle health management.

## Summary

The technical hypothesis remains useful, but the business scheme should be reset.

The first business should not be framed as production predictive maintenance.

The first business should be framed as:

> A development and OEM-design-review evidence package that makes EPS gear / rack behavior, control effort, stress, and margin more observable using ECU-side signals.

This creates a practical bridge:

```text
engineering usefulness
  -> development evidence package
  -> OEM design review value
  -> health-ready EPS option
  -> connected diagnostics / VHM integration
```

This staged scheme is more realistic than trying to sell EPS-only predictive maintenance from the beginning.
