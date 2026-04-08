# Maven Directive — Keep Momentum, Don't Wait for Data

**Date:** 2026-04-08  
**From:** Maven (Co-op Chair)  
**To:** All team members  
**Re:** Real data is coming — but we don't stall. Here's what moves NOW.

---

## Context

The project owner has received our data spec (`workspace/deliverables/data-spec/real-comp-data-spec.md`) and real comparable sales data is being sourced. When it arrives, we'll swap out the synthetic data and re-run everything.

**Until then: we use what we have.** Every tool works with synthetic data. Every analysis we run now validates our methodology, surfaces tool bugs, and builds the decision framework so we're ready to pull the trigger when real numbers land.

No one waits. Here are assignments.

---

## M5 — Member Agreement Finalization (Statton + Ledger)

**Status:** Member agreement v2 is DRAFT. It needs to be FINAL TEMPLATE before April 29.

**Statton — due April 22:**
1. Resolve the **$40K vs $50K Maven buy-in discrepancy** — check the OA against the member agreement and the capital-call-schedule. Pick one number and document the rationale. If it's $50K in the OA, the member agreement says $50K. Period.
2. Fill in the blanks: OA execution date, EIN, Oregon SOS entity number (Section 1.2).
3. Confirm the **minimum monthly hours commitment** number (Section 5.1) — propose a number based on first-flip labor needs. Recommend: 40 hours/month minimum for founding members.
4. Set the **Contribution Deadline** (Section 3.2 and Exhibit A) — align with the capital-call-schedule target of June 21.
5. Change document status from "DRAFT" to "FINAL TEMPLATE — Approved for individual execution copy preparation."

**Ledger — due April 22:**
1. Reconcile the **financial exhibits** (Exhibit A capital table) with the actual founding cohort numbers: Maven $50K, Birch $12-15K, Slate $7.5-10K, Copper $20-25K, Volt $15K (conditional).
2. Confirm: Does the **moderate capitalization scenario ($106.5K)** support first acquisition at 85% LTV hard money? This was flagged URGENT on April 8 and I haven't seen an answer. I need a yes/no with math by April 22.
3. Update `capital-call-schedule.md` with confirmed bank account opening timeline.

**Deliverable:** Member agreement v2 at FINAL TEMPLATE status, ready to distribute as advance reading before April 29 founders' meeting. Not for signature — for review.

---

## M6 — Property Search: Run the Tools NOW (Reeves)

**Status:** Three candidate properties identified. Manual ARV estimates done. But NO formal tool output exists. The comp-analyzer, arv-calculator, and deal-scorer are sitting there with synthetic data and nobody has run them.

**Reeves — due April 15:**

### Task 1: Run comp-analyzer on all 3 candidate properties
Create subject property JSON files and run the comp-analyzer tool. Even with synthetic comps, this validates:
- Whether the tool's adjustment methodology produces values consistent with manual estimates
- Whether the indicated value ranges bracket the ARVs in `top3-evaluation.md`
- Whether the relevance scoring works as expected

**Property #1 — 6847 NE Killingsworth (Cully):**
```json
{
  "address": "6847 NE Killingsworth St, Portland, OR",
  "neighborhood": "cully",
  "sqft": 1180,
  "beds": 3,
  "baths": 1.0,
  "year_built": 1948,
  "lot_sqft": 5200,
  "condition": "poor"
}
```

**Property #2 — 3312 NE 112th Ave (Parkrose):**
```json
{
  "address": "3312 NE 112th Ave, Portland, OR",
  "neighborhood": "parkrose",
  "sqft": 1100,
  "beds": 3,
  "baths": 1.5,
  "year_built": 1955,
  "lot_sqft": 6200,
  "condition": "poor"
}
```

**Property #3 — 4523 SE 92nd Ave (Lents):**
```json
{
  "address": "4523 SE 92nd Ave, Portland, OR",
  "neighborhood": "lents",
  "sqft": 1050,
  "beds": 3,
  "baths": 1.0,
  "year_built": 1952,
  "lot_sqft": 5000,
  "condition": "poor"
}
```

Run each: `python comp_analyzer.py --input {file}.json --count 5 --seed 42 --output {neighborhood}-comp-results.json`

### Task 2: Feed comp output into arv-calculator
Use the comp results from Task 1 as input to the ARV calculator for each property. Compare tool ARV output against the manual ARV estimates in `top3-evaluation.md`:
- Property #1 manual ARV: $399,000
- Property #2 manual ARV: $372,000
- Property #3 manual ARV: $386,000

Document any significant divergence.

### Task 3: Run deal-scorer on target neighborhoods
Run the neighborhood scoring on all 7 neighborhoods using current data in `data/portland-neighborhoods/*.json`. Compare tool output against the manual scores in `neighborhood-scores.md`:
- Lents manual: 78/100
- Cully manual: 73/100
- Parkrose manual: 71/100

### Task 4: Produce a formal evaluation package
Consolidate all tool output into a single document: `workspace/deliverables/m06-property-search/tool-evaluation-results.md`

This becomes the baseline. When real data drops, we re-run everything and diff against these synthetic results.

---

## M4 — Founders Meeting Prep (Calloway)

**Status:** Agenda is DRAFT (April 15). Pre-meeting email is drafted (April 22). Volt at 4.5/5 interest. Harlan meeting should happen this week.

**Calloway — due dates below:**

1. **By April 23:** Confirm Volt-Harlan meeting is scheduled and happening this week. Report back on outcome. This is the gate for Volt's observer invitation to April 29.

2. **By April 25:** Finalize the founders' meeting agenda. It's been DRAFT since April 15. Changes needed:
   - Add Volt as confirmed observer (pending Harlan meeting outcome)
   - Update the OA key terms section to reflect any amendments Statton completed
   - Add 5-minute slot for Reeves to present property search progress (show the candidates — founders want to know where their money goes)
   - Confirm room booking and AV/whiteboard availability

3. **By April 25:** Distribute advance materials to all attendees:
   - pitch-deck.md
   - member-financial-guide.md (from M3)
   - member-agreement-v2.md (FINAL TEMPLATE version from Statton)
   - founders-meeting-agenda.md (final)
   - candidate-info-packet.md (for Volt if attending)

4. **By April 25:** Send the pre-meeting email. It's drafted — update it with:
   - Confirmed Volt status (attending or not)
   - Final materials list
   - Any parking/logistics updates

5. **Ongoing:** Continue Sparks (electrician Lead 3) outreach. We want the backup pipeline warm in case Volt stalls.

---

## Other Work That Doesn't Wait for Data

| Owner | Task | Due | Notes |
|-------|------|-----|-------|
| **Harlan** | Meet with Volt (electrician) | April 23-25 | Trade-to-trade technical conversation. Assess K&T remediation skills. Report to Calloway. |
| **Harlan** | Preliminary rehab scope for Property #1 (Cully) | April 25 | Desktop estimate using listing photos and condition notes. Doesn't need real data. |
| **Statton** | Confirm entity filing is complete, EIN received | April 22 | Needed for member agreement blanks |
| **Ledger** | Update break-even model with moderate capitalization scenario | April 22 | Use $106.5K capitalization, $180-200K acquisition, $48K rehab |
| **Reeves** | Drive-by assessments — Properties #1 and #2 | April 25-26 | Exterior condition, neighborhood feel, street traffic, comparable houses nearby |

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Continue with synthetic data for all tool runs | Real data ETA unknown; synthetic data validates methodology and surfaces tool issues | 2026-04-08 |
| Member agreement target: FINAL TEMPLATE by April 22 | Must be distributable as advance reading for April 29 founders' meeting | 2026-04-08 |
| Reeves to run all 3 tools on candidate properties immediately | No dependency on real data; establishes baseline for comparison when real data arrives | 2026-04-08 |
| Harlan-Volt meeting is gate for April 29 observer invitation | Can't invite to founders' meeting without trade skills verification | 2026-04-08 |

---

## Next Check-In

**April 22 — All hands status.** I want to see:
- Member agreement v2 at FINAL TEMPLATE ✓/✗
- Capitalization sufficiency answer from Ledger ✓/✗
- Comp-analyzer + ARV results for 3 properties from Reeves ✓/✗
- Volt-Harlan meeting outcome from Calloway ✓/✗
- Founders meeting agenda finalized ✓/✗

No vague updates. Deliverables or blockers. That's it.

— Maven
