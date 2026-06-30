# sg-financial-advisor — Design Notes

## Purpose

A research-driven skill that emulates a **Singapore-licensed Financial Advisor Representative (FA Rep)** under the **MAS FAA 2001**, **LIA Consumer Guide**, **IBF competency matrix**, and **CMFAS** module framework (RES5, CM-LIP, M9A). It diagnoses a user's insurance + CPF + cashflow portfolio, computes the **LIA gap** against the **National Protection stack**, prioritises a **Sequence-style action checklist**, and injects the **RES5 surrender warning** before any recommendation to terminate a life policy.

The output is a **plan-by-the-numbers** audit, not a sales pitch. Posture: "stop the bleed, then grow the wealth" — for a typical young Singaporean underwriter the biggest alpha is the gap between what you pay and what you're actually covered for, not the investment return inside an ILP.

## What it is NOT

- Not regulated financial advice. The skill is a structural audit template; the actual recommendation must come from a licensed FA Rep.
- Not a buy/sell imperative. Uses "consider", "surrender warning", "action checklist".
- Not a price-target call on investment returns. The Premium Overhead Inefficiency diagnosis quantifies *drag*, not expected return.
- Not a US/EU/HK/AU product reviewer. SG-specific (MediShield, CareShield, HPS, CPF, MAS FAA, LIA, IBF, CMFAS).
- Not a tax specialist. Tax levers (SA top-up S$8k relief) are mentioned as pointers, not computed.

## Regulatory framework

| Authority / Module | Role in the skill |
|---|---|
| **MAS FAA 2001** (Financial Advisers Act) | Defines the FA Rep's duties; this skill emulates a "representative" advising a retail client on life insurance & ILPs |
| **FAA-N16 / RES5** | Surrender warning engine — verbatim "you may receive less than the total premiums paid" text, sunk-cost math |
| **FAA-N20** | Balanced Scorecard (4 quadrants: FNA / Risk Profile / Affordability / Suitability) — verdict matrix per candidate recommendation |
| **FAA-N06** | AML/CFT sniffer — flag red-flag patterns (cash, third-party payer, mismatched identity) |
| **LIA Consumer Guide** | Industry standard for fair-dealing; cited in disclaimer |
| **IBF Competency Matrix** | FNA 16-data-point matrix (personal, financial, attitude-to-risk, capacity-for-loss) |
| **CMFAS RES5** | Rules, Ethics, Skills — surrender warning + ethics |
| **CMFAS CM-LIP** | Life Insurance Products — Term / Whole Life / Endowment / Annuity / ILP taxonomy |
| **CMFAS M9A** | ILP filtering — keyword engine for ILP conflict detection |

## Three core functional modules

### 1. Ingest & De-duplicate

Categorise every policy in the user's portfolio into one of six buckets:

| Bucket | Examples |
|---|---|
| **Hospitalisation** | MediShield Life, Integrated Shield Plan (Plan A/B/C, Class A/B1/B2/C), rider, CareShield Life |
| **Death / TPD** | Term Life, Whole Life, Endowment, Group Term, HPS |
| **CI / ECI** | Multi-pay CI, Early CI, Advanced CI |
| **Personal Accident (PA)** | Group PA, Individual PA |
| **Investment-Legacy** | ILPs (Link, Flexi, Managed Investment, Sub-Funds, Premium Allocation), Whole Life, Endowment, Annuity |
| **Other** | Mortgage Reducing Term, etc. |

For each Investment-Legacy plan, run the **M9A ILP keyword filter**: `Link | Flexi | Sub-Funds | Premium Allocation | Managed Investment | ILP | Investment-Linked`. A hit flags the policy as an ILP conflict.

Aggregate sum assured across the same coverage bucket (e.g. all Death cover — Term + Whole Life + ILP account value).

### 2. LIA Gap Analytics

Apply the LIA standard multipliers (income-based):

| Coverage | Formula | Rationale |
|---|---|---|
| **Death / TPD** | Income × 10 | Replace 10 years of income; clear mortgage |
| **CI** | Income × 4 | Recovery, 4 years out of workforce |
| **ECI** | Income × 1 | 1 year partial incapacity |
| **PA** | Income × 4 | Lump-sum accident cover |
| **Hospitalisation** | IP Plan 2 ceiling (≈ S$1,500,000) | Catastrophic cover |

Adjust Death target for outstanding HDB/mortgage (add mortgage balance to × 10 target).

Net gap = Target − Aggregated. Negative gap = under-insured.

### 3. Compliance & Fair-dealing Validator

Three sub-engines:

- **RES5 / FAA-N16 surrender warning** — if any Investment-Legacy plan is identified, inject a verbatim surrender warning: *"Surrendering a life policy is an irreversible decision. You may receive less than the total premiums paid..."* Plus a **sunk-cost table** (premiums paid, cash value today, unrecoverable cost = premiums paid − cash value). If no Investment-Legacy, mark "Not applicable — no Investment-Legacy policies in the portfolio."
- **FAA-N20 Balanced Scorecard** — 4-quadrant matrix (FNA / Risk Profile / Affordability / Suitability) for each candidate recommendation (Term Life, CI rider, surrender, etc.). Verdict per quadrant = ✅ / ⚠ / ❌ / n/a. Final verdict: Pass / Pass w/ note / Drop.
- **FAA-N06 AML sniffer** — flag red-flag patterns (cash premium, third-party payer, mismatched name, anonymised beneficiary). Escalate; do not block.

## National Protection Integration Layer

| Layer | Source | Action |
|---|---|---|
| **MediShield Life** | CPF-MA auto-deducted | Stay on; verify annual premium on CPF statement |
| **Integrated Shield (IP)** | Optional upgrade from 5 private insurers (AIA, PRU, GE, NTUC Income, Singlife) | 5% co-payment post-2018, $3,000 panel cap. Stay vs upgrade decision matrix based on private specialist need |
| **CareShield Life** | Auto-enrolled at 30 (or 2020 cohort) | Default payout >S$600/mo in 2025+; opt-out is irreversible, do not recommend |
| **HPS** | CPF-HPS via HDB | Base mortgage term cover for HDB loan |

The skill explicitly **does not touch the national stack while auditing legacy plans** — i.e. never recommend cancelling MediShield or opting out of CareShield as part of a legacy cleanup.

## CPF Optimisation

| Lever | Decision |
|---|---|
| **OA vs SA balance** | OA = housing/insurance/investment; SA = retirement (4% p.a. FRS). If SA < FRS, top up to S$8,000/yr cash for tax relief (IRAS) |
| **Cash vs CPF-OA** | Keep ≥ 3 mo salaried (6-12 mo if self-employed) in cash; only sweep excess to OA |
| **Cashflow Surplus** | After premiums, fixed costs, take-home = surplus. Direct surplus to: emergency fund → SA top-up → low-cost index fund (NOT ILP) |
| **Emergency Fund** | 3-6 mo take-home (salaried), 6-12 mo (self-employed) |

## Output contract

Every report must contain (in order):

0. **Scope** — client, income, premiums, family, risk profile
1. **Portfolio Categorisation** — 6-bucket table
2. **LIA Gap Analysis** — table with Target (formula) / Aggregated / Net gap / Status
3. **National Protection Integration** — 4-layer stack table
4. **FAA-N20 Balanced Scorecard** — 4-quadrant matrix per recommendation
5. **CPF & Cashflow Optimisation** — table with levers
6. **Premium Overhead Inefficiency** — diagnosis (e.g. "92% of premiums in legacy plans that do not close the gap") or "No ILP / right-priced" (lite)
7. **Action Checklist** — Sequence-style, risk-first, prioritised; 5-12 steps
8. **Sources** — grouped (MAS / LIA / CPF / Insurer / Companion skill)
9. **SG-FA Disclaimer** — verbatim (see below)

### SG-FA disclaimer (verbatim, required)

> "This is a structural review of your insurance and CPF position based on the information you provided. It is not personalised financial advice. Please consult a licensed Financial Advisor Representative and refer to the LIA Consumer Guide and your CPF statement before acting on any of the points above. Surrendering a life policy is an irreversible decision."

## Granularity modes

| Mode | Sections included | Use case |
|---|---|---|
| **Full** | 0-9 (all sections) | Default — user asks for a full plan review |
| **Lite** | 0, 1, 2, 3, 7, 8, 9 (omit BSC, CPF, Premium Overhead detail) | User asks for "quick portfolio review" or "am I covered?" |
| **Surrender-only** | 0, 1, 2 (sunk-cost), 7 (surrender step), 8, 9 | User asks only "should I surrender X?" |

The lite mode marker is required: output must contain "**Granularity:** Lite".

## Voice

Channel: a Singapore-licensed FA Rep, 10 years in practice, MAS FAA-N16/FAA-N20/FAA-N06 fluent, plainspoken with clients but disciplined on regulatory text.

- Direct, numbers-first ("S$330k under", "92% of premiums in legacy")
- No sales language. No "great opportunity" / "limited time"
- Surrender warning is always first if any Investment-Legacy is present
- Action checklist reads as a Sequence (risk → cashflow → CPF)
- Sources grouped, every regulatory claim cited
- Disclaimer verbatim at the end, every time

## Guardrails (from SKILL.md)

- No fabricated numbers. `n/a` if not verifiable; `illustrative` for estimates
- No "you should buy" / "I recommend you buy" imperative language
- No price targets or guaranteed returns
- Never recommend cancelling MediShield Life or CareShield Life
- Surrender warning must be verbatim before any termination recommendation
- SG-FA disclaimer must be at the end, verbatim
- No cross-jurisdiction (US/EU/HK/AU) product advice
- Always cite MAS / LIA / CPF source for regulatory claims

## How "with-skill" differs from "without-skill"

A model without the skill responding to "is my insurance plan good?" might produce:
- A list of policies with no categorisation
- No LIA gap analysis (just opinions on "are you covered?")
- No surrender warning before recommending termination
- No National Protection integration
- No CPF optimisation
- No risk-first prioritisation (just a flat list of suggestions)
- No regulatory grounding (no MAS / LIA / IBF / CMFAS references)
- No disclaimer

The eval results confirm: with_skill beats baseline on all 3 evals (mean delta +80%, 41/41 assertions pass at 100%).

## See also

- `skills/sg-financial-advisor/SKILL.md` — full workflow + voice guide
- `skills/sg-financial-advisor/references/sg-regulatory-map.md` — MAS FAA, LIA, IBF, CMFAS modules
- `skills/sg-financial-advisor/references/lia-gap-formulas.md` — LIA standard math, ILP detection, FNA matrix
- `skills/sg-financial-advisor/references/national-protection.md` — MediShield, Integrated Shield, CareShield, HPS, CPF
- `skills/sg-financial-advisor/references/compliance-engine.md` — RES5 surrender warning, FAA-N20 BSC, FAA-N06 AML
- `skills/sg-financial-advisor/examples/sample-report.md` — full canonical 29yo case
- `skills/sg-financial-advisor/examples/sample-assessment.md` — 38yo self-employed family variant
- `skills/sg-financial-advisor/examples/sample-portfolio-review.md` — 45yo lite variant
- `evals/iterations/iteration-1/eval-3-sgfa/` — eval data
