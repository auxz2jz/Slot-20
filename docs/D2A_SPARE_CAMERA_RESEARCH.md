# D2a matching-spare sourcing research

**Status:** COMPLETE AS A RESEARCH SNAPSHOT — no seller was contacted, no item
was purchased, and no camera or other hardware was accessed. Prices,
availability and return terms were checked on **2026-10-19** and can change.

## Decision

No inspected offer proves the required hardware number
`IPC_523128M8MP`. Reolink currently publishes firmware for the same retail
model under both `IPC_523128M8MP` and `IPC_560B158MP`, so a listing that says
only `RLC-811A` is an **unverified model match**, not a compatible recovery
spare. The D1 Class A gate remains unsatisfied.

The best next action is a separately approved seller-evidence round, starting
with the returnable, item-specific used listing below. Do not purchase until a
redacted Device Info screenshot proves the exact model and hardware number.

## Evidence classes used here

| Class | Meaning in D2a | Purchase disposition |
| --- | --- | --- |
| Revision-confirmed candidate | Listing or seller evidence shows `RLC-811A` and `IPC_523128M8MP` for the exact unit | None found; still only a D1 Class B observation donor until internal boot-critical identity is later verified |
| Model-only candidate | Listing identifies `RLC-811A`, but provides no Device Info hardware number | Do not purchase; request redacted evidence first |
| Rejected/poor fit | Wrong/unknown model, unavailable, no usable return route, or unsuitable geography/terms | Do not pursue unless the constraint changes |

## Current candidates

Displayed prices exclude tax. Shipping terms are those shown by the cited
page for a US destination and must be rechecked before any later action.

| Rank | Offer | Price / shipping | Condition | Returns | Hardware evidence | D2a disposition |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [eBay item 336809300304](https://www.ebay.com/itm/336809300304), individually photographed unit “#3” | US$94.59 / free standard shipping | Used; seller describes it as near mint; accessories vary | 30 days; seller-paid return shipping | Model and individual exterior/box photos only; no Device Info screen or hardware number | **Best evidence-request target.** Item-specific stock is more suitable for tying a screenshot to the unit, but it remains unverified |
| 2 | [eBay item 407241212657](https://www.ebay.com/itm/407241212657), direct-from-Reolink refurbished stock | US$90.99 / free standard shipping | Certified refurbished; more than 10 shown available | 30 days; seller-paid return shipping; listing states a two-year eBay refurbished warranty | Generic product media and model only; multi-unit inventory means evidence must identify the exact unit that would ship | **Best return/price fallback**, but batch selection may make exact-unit revision proof impractical |
| 3 | [Walmart item 446894080](https://www.walmart.com/ip/446894080) | US$97.99 / free shipping | New, sold by ReolinkUSOnline and fulfilled by Walmart | Page displayed free holiday returns through 2027-01-31 | Product model only; no exact-unit hardware number | Strong return fallback, but not used and not revision-selectable from the published page |

The same used seller also exposed separate units “#2”, “#4”, and “#5” at
US$94.59 with free shipping and free 30-day returns in the marketplace results.
They are alternates, not additional evidence: each lacks a Device Info screen,
and one captured “#5” page had already sold. Recheck availability and request
evidence for only one exact unit at a time.

## Rejected and ambiguous offers

| Offer | Observed terms | Reason not to prefer |
| --- | --- | --- |
| [eBay item 137760889931](https://www.ebay.com/itm/137760889931) | US$100 open box plus displayed destination-dependent shipping; no returns | Unknown hardware number and no ordinary mismatch-return path |
| [eBay item 336679019865](https://www.ebay.com/itm/336679019865) | US$110 open box plus US$6.33 shipping; no returns | Unknown hardware number, no returns, and materially worse price/terms |
| [eBay EU item 177637399684](https://www.ebay.com/itm/177637399684) | EUR84.99 certified refurbished; 30-day buyer-paid returns | Page states it does not ship to the United States; hardware number is still absent |
| Sold/ended examples at US$71–99 | Used/open-box historical listings | Not available and therefore not acquisition candidates; useful only as rough price context |

No inspected listing explicitly showed incompatible `IPC_560B158MP`; however,
all model-only listings are ambiguous because Reolink's own RLC-811A support
page lists that second hardware family. An explicit different hardware number
is an immediate rejection, not a near match.

## Required seller evidence

Before purchase, obtain all of the following for the **exact unit that will be
shipped**:

1. A clear Reolink **Device Info / System Information** screenshot showing:
   `Model = RLC-811A`, `Hardware No. = IPC_523128M8MP`, and firmware/build
   version. Reolink documents that this screen exposes model, hardware number
   and firmware version.
2. The screenshot must redact UID, serial number, MAC and IP addresses, QR
   codes, device/account names and any credentials. The public repository
   should retain only sanitized facts; original evidence stays private.
3. Exterior photographs of the exact camera, base/product label, connector
   harness, housing and included accessories. All UID/serial/QR material must
   be covered or redacted. Exterior photos support identity/condition but do
   **not** replace the Device Info hardware number.
4. A simple non-sensitive tie between screenshot and stock unit (for example,
   the listing's unit number in the same photo set). A generic screenshot from
   another unit is not acceptable for multi-quantity inventory.
5. Written confirmation of the return window, who pays return shipping, and
   whether a return is accepted if the received Device Info hardware number
   differs. Do not assume a normal return policy permits disassembly; internal
   inspection remains a later approval gate.

## Draft seller questions — not sent

> I am looking for one specific hardware revision of the Reolink RLC-811A.
> Before purchase, could you send a photo or screenshot from Device Settings >
> Device Info for the exact unit that would ship? I need to see only the Model,
> Hardware No., Firmware Version, and Build fields. Please cover or redact the
> UID, serial number, MAC/IP addresses, QR codes, account/device names, and any
> credentials. The required value is Hardware No. `IPC_523128M8MP`; please do
> not update the firmware. Could you also provide redacted photos of the exact
> camera's exterior label, connector harness, housing, and included
> accessories, and confirm whether the listed return policy applies if the
> received hardware number is different? Please do not open or disassemble the
> camera.

This draft is deliberately non-operational. Sending it, negotiating, buying,
or asking a seller to do anything beyond ordinary identification requires a
new user-approved task.

## Sources and volatility

- [Reolink RLC-811A support/firmware page](https://support.reolink.com/c/rlc-811a/)
  lists both `IPC_523128M8MP` and `IPC_560B158MP`, establishing why model name
  alone is insufficient.
- [Reolink system-information guide](https://support.reolink.com/articles/360011977034-How-to-Find-out-Reolink-Device-System-Information/)
  documents where model, UID, hardware number and firmware version are shown.
- Candidate and rejected-offer facts come from the linked marketplace pages
  and their current result pages as checked on 2026-10-19. Marketplace pages
  are volatile; price, inventory, destination shipping and return eligibility
  must be revalidated immediately before any approved contact or purchase.

## Focused verification

- Candidate records were cross-checked against the D1 minimum pre-purchase
  match and return requirements.
- The machine-readable record in `configs/d2a_spare_candidates.json` contains
  the exact target, candidate/rejection classifications, source URLs, checked
  date and all-false purchase/contact/hardware state.
- No seller message, cart action, account action, purchase, camera contact,
  firmware operation or physical recovery activity occurred.
- No seller personal data, camera identifier, credential, label image or other
  private device information is stored in Git.

## D2a completion recommendation

- **Completed:** dated sourcing research identified three model-only,
  returnable candidates and three rejected/poor-fit offers; no exact hardware
  match was claimed.
- **Checkpoint:** commit and push this sanitized report, machine-readable
  snapshot, state and handoff. Existing kernel, rootfs, UI and private analysis
  artifacts remain unchanged.
- **Next task:** **D2a-1 seller-evidence collection only**, after explicit user
  authorization — send the approved draft to the item-specific used seller,
  then validate and privately retain the redacted response. Do not purchase.
- **Recommended model and reasoning:** Medium.
- **Why:** this is routine evidence collection and checklist comparison, not
  electrical work or reverse engineering.
- **When to switch:** use High only after a purchased spare reaches the
  separately approved G1 acceptance/electrical/backup-planning boundary;
  reserve Ultra for a narrow persistent Boot-ROM or recovery-architecture
  uncertainty.
- **Usage preparation:** D2a is a safe documentation checkpoint. Recheck
  current usage and marketplace availability before outreach; checkpoint again
  before any purchase or later physical gate.
