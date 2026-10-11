# Lightweight firmware development roadmap

**End goal:** replace stock Reolink software, not just skin it. Maintain core hardware functionality and optional external AI processing.

| Phase | Work | Camera risk | Exit gate |
|---|---|---|---|
| A (current) | Offline identify partitions, file trees, boot sequence, hardware drivers | None | Reproducible extraction, documented unknowns |
| B | Trace sensor/video encoder, zoom/focus, networking, AI model and events | None | Evidence-backed interface and dependency maps |
| C | Build external local-PC proof of concept: RTSP → object detection → polygon/tripwire → snapshot → CodeProject.AI / fallback OCR → searchable event | Read-only connection only after separate approval | Demo on prerecorded clips first; camera untouched |
| D | Assemble independent Buildroot/Linux userspace, RTSP/ONVIF and control APIs | None while built/tested offline | Reproducible cross-build and appropriate unit tests |
| E | Verify hardware-specific full flash backup and recovery on matching spare | **High** | Backup restore and rescue tested, not inferred |
| F | Explore verified RAM boot / hardware tests on spare only | **High** | Hardware peripherals and recovery validated |
| G | Consider permanent install only after explicit approval and all recovery gates | **High** | Working standalone image and established rollback |

## Prioritized capabilities
1. Reliable basic video pipeline, encoder, network access, recording, optical zoom/focus, IR/spotlight and audio.
2. User-defined zone polygons, directional line-crossing and event API.
3. Vehicle/person/object tracking and ALPR with modular inference backends.
4. System security, updates, limited log export and recoverability.

## Constraints
- The NA51055 platform likely cannot host the complete CodeProject.AI server; treat lightweight onboard inference as research.
- No unrealistic promises of 4K60, local OCR performance or vendor-independent ISP support before measurement.
- Never publish vendor firmware, credential material, unique identifiers or recovered proprietary binaries.
- Minimize diagnostics: keep crash/boot logs, parser validations and concise test results only.
