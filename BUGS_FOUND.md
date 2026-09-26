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

---

## Issue 5 — `create_track_automation` cannot automate Arrangement clips

**Severity:** High (feature is advertised but unusable for Arrangement automation)

**Environment:** macOS · Ableton Live 12.4.5 (2026-08-19 build) · active script at `~/Music/Ableton/User Library/Remote Scripts/AbletonBridge/`.

**Where:** `handlers/automation.py:create_track_automation`, specifically the call to `target_clip.create_automation_envelope(parameter)`.

**Symptom:** Every Arrangement automation write fails before creating an envelope. Live reports: `RuntimeError: Not a session clip or parameter belongs to another track.` This occurs for both device parameters and mixer parameters, including a clip that begins at beat 0.

**Minimal repro:**
1. Put a MIDI clip in Arrangement view.
2. Call `create_track_automation(track_index=4, parameter_name="Volume", automation_points=[{"time": 0.01, "value": 0.49}, {"time": 14.0, "value": 0.59}])`.
3. Read `get_arrangement_clip_info(track_index=4, clip_index_in_arrangement=0)`.
4. The command returns `Internal error`; `has_envelopes` remains `false`.
5. Live Log contains the exception at `handlers/automation.py:280` during `create_automation_envelope`.

**Confirmed controls:** The failure repeats for Kick/Saturator `Drive` on an Arrangement clip beginning at beat 16 and Perc/Mixer `Volume` on a clip beginning at beat 0. It is neither a parameter-name nor a song-time/clip-time conversion issue.

**Suggested fix:** Do not present this path as supported until the Live 12.4.5 LOM offers a valid Arrangement-envelope owner/API. Add a capability check that returns the exact Live limitation without attempting `create_automation_envelope` on an Arrangement clip. Keep the existing Session `create_step_automation` path separate. A valid implementation needs a Live-supported Arrangement automation API rather than a Session Clip envelope call.

## create_track_automation is broken (arrangement automation impossible)

`create_track_automation` always fails with:

```
RuntimeError: Not a session clip or parameter belongs to another track.
  File ".../handlers/automation.py", line 280, in create_track_automation
    if hasattr(target_clip, "automation_envelope"):
```

Cause: `Clip.automation_envelope()` is only valid on **session** clips. The handler
picks an arrangement clip and calls `automation_envelope(parameter)` on it, which the
Live API rejects. Arrangement automation needs track/song-level envelopes instead.

Verified separately: session-clip envelopes do **not** survive
`duplicate_clip_to_arrangement` — only notes are copied. Test with the Auto Filter LFO
set to 0 showed a constant cutoff (0.52) across the whole duplicated clip, while the
source session clip carried a 0.46/0.72/0.54/0.46 envelope.

Consequence: the bridge currently cannot write any automation that is audible in the
Arrangement view. Device-intrinsic modulation (Auto Filter LFO, Echo Mod, Beat Repeat
Variation) is the working alternative.

## duplicate_clip_to_arrangement: parameter is `time`, not `destination_time`

An unknown key is silently ignored and defaults to `0.0`, so the clip lands on beat 0
and pollutes the arrangement instead of erroring out.

## start_playback / continue_playing ignore the playhead position

`set_song_time` reports success and `get_song_transport` confirms the new position, but
starting playback jumps back to beat 0. Any measurement taken "at beat X" is therefore
invalid unless the playhead is sampled via `get_song_transport.current_time`.

**Fixed in fork (commit `2dbd1e3`, verified on Live 12.4.6):** `start_playback` calls
`continue_playing()` and re-applies the playhead via `schedule_message` on the next ticks.
A `current_song_time` write in the same main-thread task is overwritten when the
transport starts. Verified: playhead 32 -> 34.4 after 0.5 s / 38.4 after 1.5 s;
playhead 64 -> 66.6 / 70.5 (130 BPM), with a different previous stop position.
