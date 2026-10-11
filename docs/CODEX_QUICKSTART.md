# Codex handoff / next steps (2026-10-11)

This is a real GitHub repo, not an automatically synchronized conversation. **Clone or pull it in Codex on Windows.** Codex should commit and push source/report changes so another ChatGPT conversation can inspect the latest results.

## First Codex task (offline only)

1. Read `AGENTS.md`, `docs/STATE.md`, `docs/HARDWARE.md`, and `docs/ROADMAP.md`. Do **not** load the full Master Instruction Library.
2. Inspect the existing Python tools in `tools/`; these are copied from the previous offline extraction toolkit. Do not rewrite unless tests identify a specific defect.
3. Keep the exact firmware matching installed hardware in an **ignored local directory** at `firmware_inputs/`. The file is user-supplied and intentionally **not** on public GitHub.
4. For LZO decompression, run the scripts in **WSL2/Linux** (requires Python 3.9+ and `liblzo2.so.2`; on Ubuntu the package is normally `liblzo2-2`). Do not assume native Windows DLL compatibility.
5. Check the firmware SHA-256 against the value in `docs/HARDWARE.md`.
6. Reproduce the offline manifest from the reference `.pak`:

```bash
python3 tools/unpack_reolink_offline.py \
  firmware_inputs/IPC_523128M8MP.1643_2402219117.RLC-811A.IMX415.8MP.AF.REOLINK.pak \
  --out firmware_workspace/analysis
```

Do not pass `--write-files` by default; that option materializes proprietary files to your private machine. **Never commit any outputs of that extraction.**

7. Check script assumptions with existing `mtd-utils`/`ubireader` or independent parsing where possible; the original script is a helpful static forensic parser, not a complete journal replay.
8. Investigate static ABI/call relationships: `device`, `rtsp`, `recorder`, `alarmcenter`, `cgiserver.cgi`, motor driver and AI modules. Produce a *sanitized* findings summary and small testable milestones.
9. Stop after the analysis/handoff and update `docs/STATE.md`, with no camera connection or firmware deployment.

## Availability

- **Already in repository:** small startup docs and the two original independent offline Python extraction scripts.
- **Not in repository:** firmware `.pak`, extracted vendor filesystem, raw firmware catalog, proprietary binaries, personal device identifiers, full device backup, and previous report ZIP. The source toolkit ZIP/report from the ChatGPT discussion can be supplied privately to Codex for reference.
- **No firmware is yet built**; neither a flash backup nor a recovery method has been verified.

## Time/compute discipline

Keep one narrow task at a time, record evidence once, use concise summaries, preserve last known-good commits, and change hypothesis rather than repeating failed attempts. Minimal boot/crash logs are important later; do not introduce an elaborate diagnostics framework.
