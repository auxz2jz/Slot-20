# Slot-20 — Current task handoff

**Status:** D2a RESEARCH COMPLETE — NO REVISION-CONFIRMED SPARE. No seller was
contacted, no purchase/account/cart action occurred, and no camera was
accessed, powered, opened, rebooted, read from or written.

**LAST TASK ID / STATUS:** D2a matching-spare sourcing research — **COMPLETE;
ZERO `IPC_523128M8MP` OFFERS CONFIRMED**.

**EVIDENCE AND TESTS:**

- `docs/D2A_SPARE_CAMERA_RESEARCH.md` is the dated 2026-10-19 candidate,
  rejection, evidence and seller-question record.
- Three returnable RLC-811A model-only offers were recorded at US$90.99–97.99.
  The preferred evidence-request target is used eBay item `336809300304` at
  US$94.59 with free shipping and seller-paid 30-day returns because it is an
  individually photographed unit. Direct-from-Reolink refurbished eBay item
  `407241212657` is the lowest observed price/return fallback at US$90.99, but
  it is multi-unit inventory. Walmart item `446894080` is a US$97.99 new-stock
  return fallback.
- None shows an exact-unit Device Info hardware number. Reolink's current
  RLC-811A support page lists both `IPC_523128M8MP` and `IPC_560B158MP`, so the
  retail model name does not prove compatibility.
- Two no-return US offers and one EU offer that does not ship to the US were
  rejected/flagged. Sold/ended offers are price context only.
- `configs/d2a_spare_candidates.json` records the candidates, rejection reasons,
  required evidence and all-false contact/purchase/hardware state. JSON parse,
  fixed-target/count checks, local Markdown-link checks and `git diff --check`
  must pass before the completion commit.
- Verified SHA-256 values are
  `96c44f18ead8a739f7f7f2898e091aa9e8e1edbc9c2610149ef47583ba3c19c4` for
  the report and
  `86b5bb416d46fb665b7300c76dea07623cc51901c249620f675553c96e895fed` for
  the machine-readable record.
- Seller questions are drafted but were not sent. Required proof is a redacted
  exact-unit Device Info screen showing `RLC-811A`, `IPC_523128M8MP` and
  firmware/build, plus redacted exterior/label/connector photos and confirmed
  mismatch-return terms.

**GIT BRANCH / COMMIT / PUSHED?:** `main`; D2a content checkpoint `5970221` is
pushed. The handoff-finalization commit containing this status must match
`origin/main` after push.

**LOCAL UNTRACKED OR PRIVATE WORK:** Preserve the completed kernel and both
rootfs trees under `/home/firmware-analysis/slot20_private/` and all existing
private firmware-analysis inputs. D2a did not inspect or modify them. No seller
response, device screenshot, label photograph, private identifier or hardware
artifact was created.

**NEXT SINGLE TASK ID + INPUT:** **D2a-1 seller-evidence collection only,
BLOCKED until the user explicitly authorizes sending messages.** Recheck the
preferred listing, send the approved draft to that seller only, and privately
validate/redact the response. Do not purchase.

**PASS CRITERION FOR NEXT TASK:** Exact-unit evidence visibly proves
`Model = RLC-811A` and `Hardware No. = IPC_523128M8MP`, exposes firmware/build,
has all UID/serial/MAC/IP/QR/account data redacted, is tied to the unit that
would ship, and includes acceptable mismatch-return terms. Otherwise reject or
remain unverified. Seller proof advances only the pre-purchase identity gate,
not D1 Class A status.

**RECOMMENDED REASONING + WHY:** **Medium.** D2a-1 is bounded communication and
evidence comparison against the fixed D1 checklist.

**WHEN TO SWITCH:** High is required before any separately approved G1–G5
physical acceptance, electrical or backup work. Ultra/highest capability is
reserved for one narrow persistent BootROM or recovery-architecture question
after a safe checkpoint and explicit selection.

**USAGE VISIBLE? CURRENT VALUE/TIME OR UNKNOWN:** Reliable closeout telemetry
on 2026-10-19 showed 18% of the five-hour window used (82% remaining) and 51%
of the weekly window used (49% remaining). This is a point-in-time snapshot,
not continuous monitoring; refresh at the next task boundary.

**USAGE PREPARATION:** D2a is a bounded safe checkpoint. Recheck usage and
listing availability before outreach. Checkpoint again before any purchase or
separately approved physical operation.

**CONTINUE OR STOP + REASON:** STOP after D2a. Sending seller messages,
purchasing, D2b acceptance and every physical gate require new explicit
authorization.

**CAMERA CONTACT/FLASH:** NONE. No discovery, authentication, network contact,
power, reboot, opening, probing, UART, NAND read/write, firmware assembly or
flash was performed or authorized.
