# AbletonBridge — Verified Bug Report

**Repo:** hidingwill/AbletonBridge
**Reported by user environment:** macOS · Ableton Live 12.4.3 (build 2026-07-07) · Live 12 Suite
**Bridge commit tested:** `01c31c4` (main, 2026-06-09)
**Date:** 2026-07-15

These four issues have been reproduced repeatedly in real sessions. Each section is written so it can be pasted directly as its own GitHub issue. Line numbers refer to commit `01c31c4`.

---

## Issue 1 — `set_compressor_sidechain` wires routing but never enables the sidechain

**Severity:** High (silent failure — no error, but ducking does nothing)

**Where:** `MCP_Server/tools/devices.py:882` (`set_compressor_sidechain`), and the corresponding remote-script handlers for `set_sidechain_by_name` / `set_compressor_sidechain`.

**Symptom:** The tool resolves and sets the sidechain *input routing* correctly, but the device's **`S/C On`** toggle stays `Off`. Result: routing looks correct in the UI, the tool returns success, but no compression/ducking occurs. No error is raised.

**Repro:**
1. Add a Compressor to a track.
2. Call `set_compressor_sidechain(track_index, device_index, source_track_name="Kick")`.
3. Observe the return message reports success and routing is set.
4. Inspect the device — the S/C enable button is still off; no ducking happens.

**Current workaround (client-side):** After calling the tool, force the hidden LOM parameter on: `batch_set_hidden_parameters` → parameter `[20] S/C On = 1`, then verify with `get_device_hidden_parameters`.

**Suggested fix:** In the `set_compressor_sidechain` / `set_sidechain_by_name` handler, after routing is applied, set the device parameter named `"S/C On"` (Compressor / Glue Compressor / Multiband Dynamics) to `1`. Expose an optional `enable: bool = True` argument so callers can opt out. This makes the tool's success message truthful.

---

## Issue 2 — `get_full_session_state` returns stale / incomplete data

**Severity:** High (can lead to destructive mistakes)

**Where:** `MCP_Server/tools/workflows.py:254` (`get_full_session_state`).

**Symptom:** Reported 4 tracks with **no** M4L device on track 0, while `get_all_tracks_info` (queried at the same moment) correctly showed track 0 as an audio track hosting the `AbletonBridge_M4L` device. Trusting `get_full_session_state` blindly would have led to deleting the bridge track itself.

**Repro:** In a session that contains the `AbletonBridge_M4L` device, call `get_full_session_state` and `get_all_tracks_info` back to back and diff the track/device listings.

**Impact:** Any cleanup/automation logic that relies on `get_full_session_state` as source of truth can act on wrong state.

**Suggested fix:** Have `get_full_session_state` build its track/device listing from the same live LOM walk that `get_all_tracks_info` uses, or drop any cached snapshot. Until fixed, consider documenting `get_all_tracks_info` as the authoritative source in the tool description.

---

## Issue 3 — `load_instrument_or_effect` creates duplicates and returns an empty device list

**Severity:** Medium

**Where:** `MCP_Server/tools/devices.py:786` (`load_instrument_or_effect`).

**Symptom:** A single call loaded **two** Compressor devices onto the same track. Additionally the response sometimes returns an empty device list (`"Devices on track: "`) despite the load having succeeded.

**Repro:** Call `load_instrument_or_effect(track_index, uri=<Compressor URI>)` once and inspect the device chain — two identical devices may appear.

**Suggested fix:**
- Investigate whether the browser-load command is being dispatched/acknowledged twice (double-fire or retry-on-timeout without idempotency).
- Populate the response device list from a fresh post-load device query so the returned list is never empty on success.
- Client mitigation today: re-query devices after every load and delete duplicates.

---

## Issue 4 — `delete_track` success message can reflect a stale cache

**Severity:** Medium (misleading, not destructive by itself)

**Where:** `MCP_Server/tools/tracks.py:74` (`delete_track`).

**Symptom:** Returned `"Deleted track '3-MIDI'"` although no track of that name existed in any query before or after. The success string is not a reliable confirmation of *what* was deleted.

**Repro:** Delete a track by index and compare the returned name against `get_all_tracks_info` before/after.

**Suggested fix:** Resolve and cache the target track's name *before* deletion and echo that, or return the deleted `track_index` plus a fresh post-delete track count rather than a name pulled from a possibly-stale cache.

---

## Notes for maintainers

- All four are reproducible on Live 12.4.3; none appear caused by the 12.4.3 update (that release only touched Re-Pitch groove handling and control-surface mappings — no LOM/M4L changes).
- Issues 1 and 4 have clean, low-risk fixes. Issues 2 and 3 need a look at the caching/dispatch layer.
- Happy to test candidate fixes against a live 12.4.3 Suite session.
