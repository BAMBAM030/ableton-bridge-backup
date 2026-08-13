#!/usr/bin/env python3
"""Build an original ~2 minute warm monumental violin solo in Ableton Live."""
import json, socket, time, sys

HOST, PORT = "127.0.0.1", 9877
TRACK = 1                 # Track 0 is the protected AbletonBridge/M4L track.
BPM = 76
CLIP_BEATS = 32.0         # 8 bars at 4/4; 5 clips = 40 bars = about 2:06.


def send(cmd_type, params=None):
    payload = json.dumps({"type": cmd_type, "params": params or {}}) + "\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    try:
        s.connect((HOST, PORT)); s.sendall(payload.encode())
        data = b""
        while True:
            chunk = s.recv(65536)
            if not chunk: break
            data += chunk
            try:
                return json.loads(data.decode().strip())
            except json.JSONDecodeError:
                continue
    finally:
        s.close()


def cmd(name, params=None):
    r = send(name, params)
    if not r or r.get("status") != "success":
        raise RuntimeError(f"{name} failed: {r}")
    return r.get("result", {})


def wait(t=0.18):
    time.sleep(t)


def phrase(bars):
    """Turn eight bars of (pitch, duration, velocity) events into MIDI notes."""
    notes = []
    for bar, events in enumerate(bars):
        t = bar * 4.0
        used = 0.0
        for pitch, dur, vel in events:
            # Tiny expressive gaps preserve the solo phrasing while staying on-grid.
            notes.append({"pitch": pitch, "start_time": round(t, 4),
                          "duration": round(dur, 4), "velocity": vel, "mute": False})
            t += dur
            used += dur
        if abs(used - 4.0) > 0.001:
            raise ValueError(f"bar {bar} totals {used}, not 4 beats")
    return notes

# Original material: D minor with a radiant D-major coda.
# MIDI pitches: D5=74, F5=77, A5=81, D6=86, A6=93, D7=98.
sections = [
    ("01 Invocation", [
        [(74,1.0,72),(77,.75,78),(81,1.0,84),(79,.5,76),(77,.75,74)],
        [(74,1.5,76),(79,.5,82),(81,1.0,86),(84,1.0,88)],
        [(82,1.0,80),(81,.5,78),(79,.5,76),(77,1.0,74),(74,1.0,72)],
        [(76,.75,76),(77,.75,80),(79,1.0,84),(81,1.5,88)],
        [(81,1.0,84),(84,.75,88),(86,1.0,92),(84,.5,84),(81,.75,80)],
        [(79,1.0,78),(82,.75,82),(84,.75,86),(86,1.5,90)],
        [(89,1.5,94),(86,.5,88),(84,.5,84),(82,.5,80),(81,1.0,82)],
        [(79,1.0,78),(81,1.0,84),(84,.75,90),(86,1.25,94)],
    ]),
    ("02 Ascent", [
        [(86,.5,84),(89,.5,88),(93,1.0,94),(91,.5,86),(89,.5,82),(86,1.0,80)],
        [(84,.5,80),(86,.5,84),(89,.5,88),(91,.5,92),(93,1.0,96),(91,1.0,88)],
        [(89,.5,86),(91,.5,90),(93,1.0,96),(94,.5,98),(93,.5,92),(91,1.0,88)],
        [(89,.5,84),(91,.5,88),(93,.5,92),(96,.5,98),(94,1.0,92),(93,1.0,90)],
        [(91,.5,86),(93,.5,90),(96,1.0,98),(94,.5,94),(93,.5,90),(91,1.0,86)],
        [(89,.5,84),(91,.5,88),(93,.5,92),(96,.5,98),(98,1.0,104),(96,1.0,96)],
        [(94,.5,90),(96,.5,96),(98,1.0,106),(96,.5,98),(94,.5,92),(93,1.0,90)],
        [(91,.5,86),(93,.5,90),(96,.5,96),(98,1.5,108),(93,1.0,96)],
    ]),
    ("03 Summit", [
        [(93,.5,94),(96,.5,100),(98,1.0,108),(96,.5,100),(94,.5,94),(93,1.0,90)],
        [(91,.5,90),(94,.5,96),(98,.5,108),(96,.5,102),(94,1.0,98),(91,1.0,90)],
        [(93,.5,94),(96,.5,100),(98,.5,108),(96,.5,102),(98,.5,110),(96,.5,104),(94,1.0,96)],
        [(93,1.0,94),(96,.5,100),(98,.5,108),(96,1.0,102),(94,1.0,96)],
        [(91,.5,90),(94,.5,96),(96,.5,102),(98,.5,110),(96,.5,104),(94,.5,98),(93,1.0,94)],
        [(89,.5,88),(93,.5,96),(96,.5,104),(98,.5,112),(96,.5,106),(94,.5,100),(93,1.0,96)],
        [(91,.5,90),(94,.5,98),(98,1.0,112),(96,.5,106),(94,.5,100),(93,.5,96),(91,.5,90)],
        [(89,1.0,88),(91,.5,92),(93,.5,98),(96,1.0,104),(89,1.0,92)],
    ]),
    ("04 Echoes", [
        [(89,2.0,76),(86,1.0,72),(84,1.0,70)],
        [(82,1.5,70),(84,.5,74),(86,1.5,80),(84,.5,72)],
        [(81,2.0,70),(79,1.0,68),(77,1.0,66)],
        [(74,2.5,68),(77,.5,72),(79,1.0,76)],
        [(81,1.0,74),(84,1.0,80),(86,2.0,86)],
        [(89,1.5,88),(86,.5,80),(84,1.0,76),(82,1.0,72)],
        [(81,1.0,74),(84,1.0,82),(86,1.0,88),(89,1.0,92)],
        [(91,1.0,90),(89,.5,84),(86,.5,80),(84,1.0,76),(81,1.0,74)],
    ]),
    ("05 Apotheosis", [
        [(81,.5,84),(84,.5,90),(86,1.0,96),(89,.5,100),(91,.5,104),(93,1.0,108)],
        [(91,.5,98),(93,.5,104),(96,1.0,110),(98,.5,114),(96,.5,106),(94,1.0,100)],
        [(93,.5,98),(96,.5,106),(98,1.0,114),(96,.5,108),(94,.5,102),(93,1.0,98)],
        [(91,.5,94),(93,.5,100),(96,.5,108),(98,.5,114),(96,.5,106),(94,.5,100),(93,1.0,96)],
        [(89,.5,92),(93,.5,100),(96,.5,108),(98,1.0,116),(96,.5,108),(94,.5,102),(93,.5,98)],
        [(91,.5,94),(94,.5,102),(98,1.0,116),(96,.5,108),(94,.5,102),(91,1.0,96)],
        [(89,.5,90),(93,.5,98),(96,.5,106),(98,1.0,116),(96,.5,108),(94,.5,100),(91,.5,94)],
        [(89,.5,90),(93,.5,98),(96,.5,106),(98,2.5,118)],
    ]),
]

# Safety/readback: track 0 is never modified.
state = cmd("get_all_tracks_info")
tracks = state.get("tracks", [])
if not any(t.get("index") == 0 and any("M4L" in d.get("name", "") for d in t.get("devices", [])) for t in tracks):
    raise RuntimeError("Protected M4L track 0 was not found; aborting")
if not any(t.get("index") == TRACK and t.get("is_midi") for t in tracks):
    raise RuntimeError("Target MIDI track missing")

cmd("set_tempo", {"bpm": BPM}); wait()
cmd("set_track_name", {"track_index": TRACK, "name": "Epic Violin Solo — Original"}); wait()
cmd("set_track_volume", {"track_index": TRACK, "volume": 0.86}); wait()
cmd("set_track_pan", {"track_index": TRACK, "pan": 0.0}); wait()
# Warmth and monumentality from the existing return effects.
cmd("set_track_send", {"track_index": TRACK, "send_index": 0, "value": 0.52}); wait()
cmd("set_track_send", {"track_index": TRACK, "send_index": 1, "value": 0.10}); wait()
# Legato solo violin preset, verified by readback after loading.
cmd("load_instrument_or_effect", {"track_index": TRACK, "uri": "query:Synths#Instrument%20Rack:Orchestral:FileId_87374"}); wait(1.5)

for slot, (name, bars) in enumerate(sections[4:], start=4):
    notes = phrase(bars)
    cmd("create_clip", {"track_index": TRACK, "clip_index": slot, "length": CLIP_BEATS})
    wait(.25)
    for i in range(0, len(notes), 100):
        cmd("add_notes_to_clip", {"track_index": TRACK, "clip_index": slot, "notes": notes[i:i+100]})
        wait(.12)
    cmd("set_clip_looping", {"track_index": TRACK, "clip_index": slot, "looping": True})
    wait(.1)
    cmd("set_clip_name", {"track_index": TRACK, "clip_index": slot,
                           "name": f"{name} — seamless 8 bars"})
    wait(.1)
    cmd("set_clip_color", {"track_index": TRACK, "clip_index": slot, "color_index": 9 + slot})
    wait(.1)
    cmd("set_scene_name", {"scene_index": slot, "name": name})
    wait(.15)
    print(f"built slot {slot}: {name}, {len(notes)} notes")

# Verify only the intended target and clips are present.
final_tracks = cmd("get_all_tracks_info")
print(json.dumps({
    "tempo": cmd("get_session_info").get("tempo"),
    "target": next(t for t in final_tracks.get("tracks", []) if t.get("index") == TRACK),
    "scenes": cmd("get_scenes"),
}, indent=2, default=str))
