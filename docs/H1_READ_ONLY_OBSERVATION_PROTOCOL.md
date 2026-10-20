# H1 read-only observation protocol

**Status:** H1 planning complete. This document proposes a later H2 session;
it does **not** authorize or perform H2. No camera connection, authentication,
query, scan, reboot, setting change, actuation, update or physical operation
occurred during H1.

## Purpose

The proposed H2 task would refresh the three public identity fields in the H0
baseline and give them an actual observation date. It is intentionally narrower
than general diagnostics. It does not attempt to identify the physical SoC,
DRAM, NAND, PCB, sensor, drivers, network configuration or recovery behavior.

The camera remains in active security service. The owner is the sole operator.
Codex must not control the app, receive credentials or receive a camera address.

## Exact proposed interface and screen allowlist

Use only the owner's **already installed, already configured Reolink mobile
app** and its existing device entry. Do not add the camera to another client or
sign in again for this task.

The only allowed navigation is:

1. On the existing device list, tap the target camera's **Settings gear**
   directly. Do not tap the video preview or camera tile.
2. On **Device Settings**, tap **Device Info**.
3. If this app version calls the same read-only page **System Information**, that
   label is the only allowed alternate. If neither exact entry exists, abort;
   do not search other menus.
4. Read the three allowlisted fields below, create at most one private
   screenshot if the owner chooses, then back out and close the app without
   opening another screen.

The device-list and Device Settings pages are navigation surfaces only. No
information is to be collected from them. Ordinary app status traffic needed
to open this existing entry is part of the proposed H2 approval, but discovery,
scanning, a new login and any alternate protocol/client are not.

## Minimum information to collect

| Item | Allowed value | Purpose |
| --- | --- | --- |
| Observation date/time | Owner's local date/time and timezone abbreviation or UTC offset; no location | Replaces H0's unknown capture date for this observation only |
| Model | Exact text shown for `Model`; expected `RLC-811A` | Confirm target selection |
| Hardware version | Exact text shown for `Hardware No.` or `Hardware Version`; expected `IPC_523128M8MP` | Enforce exact revision separation |
| Firmware version | Exact full text shown for firmware/build; expected current H0 value unless legitimately changed before H2 | Record installed software identity without opening an update screen |
| Screen label | `Device Info` or allowed alternate `System Information` | Records the observation interface |

Do not collect fields merely because they appear nearby. In particular, do not
record or publish UID, serial number, MAC/IP address, QR code, device/account
name, email, username, storage identifier, Wi-Fi details or cloud status.

## Operator procedure

### Before opening the app

1. Confirm H2 has a fresh approval that matches the approval text below without
   expansion.
2. Confirm the owner can perform one uninterrupted session of at most **five
   minutes** and that no active security incident needs attention.
3. Confirm screen recording and automatic screenshot sharing are off. The task
   does not require changing camera settings; phone-side privacy controls may be
   checked without interacting with the camera.
4. Prepare a private note containing only the five allowlisted items. Do not
   place a credential, camera address or identifier into chat or the repository.
5. If the app is signed out, requests a password/MFA, requests device discovery,
   or asks to add/initialize a device, abort. Do not authenticate or proceed.

### Observation

1. Start the five-minute window and open the already configured Reolink app.
2. Tap only the target device's Settings gear. If live video starts, immediately
   leave the view and abort the session; do not continue to Device Info.
3. Open only Device Info or its allowed System Information alternate.
4. Transcribe the screen label, model, hardware version and complete firmware
   version exactly. Record the observation date/time separately.
5. Optional evidence: take one private screenshot of this page. Do not upload or
   commit the original. If the page exposes any private field, create a cropped,
   flattened derivative with every non-allowlisted field removed or irreversibly
   covered, then inspect the derivative before sharing it. When safe redaction
   cannot be confirmed, supply only the manual transcription.
6. Back out without pressing Save, Apply, Update, Restore, Reboot or any control,
   and close the app. Do not navigate elsewhere to answer follow-up questions.

One observation attempt is allowed. If it aborts, record only the reason and
return to planning; do not improvise or retry in the same H2 task.

### After closing the app

Record the following zero-change attestation from the operator:

- only the allowlisted path was used;
- no setting was edited and no Save/Apply control was used;
- no live view, audio, motor, zoom/focus, preset, siren, spotlight or IR control
  was opened or activated;
- no update, reset, restore, reboot, diagnostic-log, storage, network, user or
  account action was opened or accepted;
- no unexpected camera light, sound, motor movement, reboot, offline period or
  security-coverage interruption was observed; and
- the session ended within five minutes.

Do not create extra traffic or operate a camera function solely to prove the
after-state. The attestation reports what was observed during the bounded
session, not a separate test.

## Prohibited actions

H2 approval under this protocol would **not** permit:

- requesting or sharing a username, password, MFA code, UID, QR code, IP
  address, MAC address, serial number or account information;
- discovery, scanning, pinging, port access, browser access, ONVIF, RTSP, SSH,
  Telnet, API calls, packet capture or use of any new client;
- opening live view or capturing camera video/audio;
- PTZ, digital zoom, optical zoom/focus, presets, tracking, siren, spotlight,
  IR-cut, microphone, speaker or other actuator/control use;
- opening or changing Network, Storage, Users, Security, Recording, Detection,
  Push, Email, FTP, Cloud, Date/Time or other configuration pages;
- opening Firmware Update, checking for updates, changing auto-update, uploading
  a package or accepting an update prompt;
- Save, Apply, Reset, Restore, Reboot, Export, Format, Initialize or diagnostic
  log collection;
- power cycling, PoE/network changes, physical access, opening, UART, test-pad
  probing, NAND reads/writes or firmware operations; or
- publishing an original screenshot or any device-instance identifier.

## Immediate abort conditions

Close or back out without accepting a prompt and stop H2 if:

- fresh approval is absent, unclear or differs from this protocol;
- the app requires login, MFA, credentials, discovery, device addition,
  initialization, a permission change or terms acceptance;
- tapping Settings opens live view, or the allowed Device Info/System
  Information entry is absent or ambiguous;
- an update, reset, restore, reboot, migration or setup prompt appears;
- the page cannot be viewed without exposing private data that cannot be safely
  withheld;
- the model or hardware revision differs from the H0 baseline;
- the interface presents an unexpected Save/Apply workflow or any uncertainty
  about whether an action is read-only;
- the camera becomes unavailable, restarts, moves, illuminates, sounds an alert,
  behaves unexpectedly or security coverage may be affected; or
- the five-minute window or operator attention budget is exceeded.

After an abort, retain only a sanitized reason. Do not troubleshoot the camera
under H2 authority.

## Evidence handling and H2 pass criterion

The H2 public record may contain only the five allowlisted items, the zero-change
attestation and a sanitized abort reason if applicable. Any original screenshot
remains private. A derivative must be reviewed at full resolution for visible
and metadata-carried private data before any separate decision to commit it;
text-only publication is preferred.

H2 passes only if the exact model and hardware revision match H0, the full
firmware version and actual observation time are recorded, the zero-change
attestation is complete, and no abort condition occurred. A mismatch or abort
is an evidence result, not permission for further access.

## Prepared approval request for H2

The following text is a template for a later user decision. Including it here
does not request or imply approval now:

> I approve H2 only as specified in `docs/H1_READ_ONLY_OBSERVATION_PROTOCOL.md`:
> I, the owner, may use my already configured Reolink mobile app for one session
> of at most five minutes, tap the existing camera's Settings gear, open only
> Device Info (or the exact System Information alternate), and record only the
> observation time, screen label, model, hardware version and firmware version.
> I will not provide credentials or an address and will perform no live-view,
> configuration, update, reboot, reset, actuation, physical or storage action.
> Any abort condition ends the task immediately. This approval does not extend
> beyond H2.

Without an explicit later approval substantially matching that scope, H2 is
blocked.

## H1 completion recommendation

- **Completed:** Defined the exact owner-operated app path, five allowlisted
  values, five-minute procedure, privacy handling, zero-change attestation,
  prohibited actions, abort conditions and scoped approval text.
- **Checkpoint:** Commit and push this sanitized protocol with state and handoff.
  Existing baselines, software and private artifacts remain unchanged.
- **Next task:** **H2 approved identification observation only**, blocked until
  the owner explicitly approves the prepared scope.
- **Recommended model and reasoning:** High.
- **Why:** H2 is small but would be the project's first deliberate live-device
  observation; procedural precision and accurate evidence handling matter.
- **When to switch:** Return to Medium for H3 offline reconciliation if H2
  completes cleanly. Stop and reassess at High if H2 aborts or evidence differs;
  Ultra is not warranted unless a later narrow recovery problem remains.
- **Usage preparation:** H1 is the required checkpoint before asking for H2
  approval. Refresh usage immediately before any approved live session; do not
  start if attention or checkpoint capacity is insufficient.
