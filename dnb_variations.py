#!/usr/bin/env python3
"""
Three D&B / Jungle Variations of Fantaisie-Impromptu
=====================================================
"""

import json
import socket
import time
import sys

HOST = "127.0.0.1"
PORT = 9877


def cmd(cmd_type, params=None, retries=2):
    """Send command with fresh connection each time. Auto-retry on timeout."""
    if params is None:
        params = {}
    for attempt in range(retries):
        payload = json.dumps({"type": cmd_type, "params": params}) + "\n"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(20.0)
        try:
            sock.connect((HOST, PORT))
            sock.sendall(payload.encode("utf-8"))
            buf = b""
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                buf += chunk
                if b"\n" in buf:
                    line, _ = buf.split(b"\n", 1)
                    try:
                        r = json.loads(line.decode("utf-8").strip())
                        return r
                    except json.JSONDecodeError:
                        pass
        except socket.timeout:
            print(f"  ⏱ Timeout ({cmd_type}), attempt {attempt+1}", file=sys.stderr)
            time.sleep(0.5)
        except Exception as e:
            print(f"  💥 Error ({cmd_type}): {e}", file=sys.stderr)
            time.sleep(0.5)
        finally:
            try:
                sock.close()
            except:
                pass
    return {"status": "error", "message": "timeout"}


# ─── Musical constants ──────────────────────────────────────────────────────

CLIP_LENGTH = 16.0
BAR = 4.0

HARMONY_A = [
    [52, 55, 59, 64], [52, 55, 59, 64],
    [56, 59, 63, 68], [58, 62, 65, 69],
]

ORIGINAL_BASS_BARS = [[42], [42, 45], [44], [46]]
ORIGINAL_PAD_BARS = [[52, 55, 59], [52, 55, 59], [56, 59, 63], [58, 62, 65]]
ORIGINAL_ARP_BARS = [
    [52, 55, 59, 64, 59, 55, 52, 55, 59, 64, 59, 55],
    [52, 55, 59, 64, 59, 55, 56, 59, 64, 67, 64, 59],
    [56, 59, 63, 68, 63, 59, 56, 59, 63, 68, 63, 59],
    [58, 62, 65, 69, 69, 65, 62, 58, 62, 65, 69, 65],
]


# ─── Variation 1: "Forward Pulse" — rhythmic drive ─────────────────────────

def build_v1_melody():
    notes = []
    motifs = [
        [64, 70, 67, 70],
        [64, 67, 71, 64, 70, 67],
        [68, 73, 71, 74, 75],
        [70, 74, 73, 70, 67],
    ]
    for bar_i, motif in enumerate(motifs):
        start = bar_i * BAR
        for i, p in enumerate(motif):
            t = start + i * 0.5
            vel = 95 if i % 2 == 0 else 70
            if i % 2 == 1:
                t += 0.04
            notes.append({
                "pitch": p, "start_time": round(t, 3),
                "duration": 0.2, "velocity": vel
            })
        if bar_i == 3:
            notes.append({
                "pitch": 64, "start_time": start + 3.5,
                "duration": 0.1, "velocity": 50
            })
    return notes


def build_v1_arp():
    notes = []
    for bar_i, arp in enumerate(ORIGINAL_ARP_BARS):
        start = bar_i * BAR
        for i in range(16):
            pitch = arp[i % len(arp)]
            if i % 4 == 3 and bar_i % 2 == 1:
                continue
            t = start + i * 0.25
            t += 0.02 if i % 2 == 1 else 0
            vel = 75 if i % 4 == 0 else (60 if i % 2 == 0 else 45)
            notes.append({
                "pitch": pitch, "start_time": round(t, 3),
                "duration": 0.18, "velocity": vel
            })
    return notes


def build_v1_bass():
    notes = []
    for bar_i in range(4):
        start = bar_i * BAR
        notes.append({
            "pitch": 40, "start_time": start,
            "duration": 0.4, "velocity": 100
        })
        notes.append({
            "pitch": 40, "start_time": start + 2.5,
            "duration": 0.2, "velocity": 65
        })
        if bar_i < 3:
            current = ORIGINAL_BASS_BARS[bar_i][0]
            next_root = ORIGINAL_BASS_BARS[(bar_i + 1) % 4][0]
            walk_notes = []
            step = 1 if next_root > current else -1
            pos = current + step
            while abs(pos - next_root) > 0:
                walk_notes.append(pos)
                pos += step
            walk_notes.append(next_root)
            for i, p in enumerate(walk_notes):
                notes.append({
                    "pitch": p, "start_time": start + 3.0 + i * 0.25,
                    "duration": 0.2, "velocity": 70
                })
    return notes


def build_v1_pad():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        for p in chord:
            notes.append({
                "pitch": p + 12, "start_time": start,
                "duration": BAR, "velocity": 35
            })
        for p in chord:
            notes.append({
                "pitch": p + 24, "start_time": start + 1.0,
                "duration": 0.15, "velocity": 75
            })
        for p in chord:
            notes.append({
                "pitch": p + 24, "start_time": start + 3.0,
                "duration": 0.15, "velocity": 70
            })
    return notes


def build_v1_vibes():
    notes = []
    for bar_i in range(4):
        start = bar_i * BAR
        for beat in [0.5, 1.5, 2.5, 3.5]:
            notes.append({
                "pitch": 79 + bar_i, "start_time": start + beat,
                "duration": 0.1, "velocity": 55
            })
    return notes


def build_v1_piano():
    notes = []
    piano_pattern = HARMONY_A
    for bar_i, chord in enumerate(piano_pattern):
        start = bar_i * BAR
        for beat in [0.5, 1.5, 2.5, 3.5]:
            for p in chord:
                notes.append({
                    "pitch": p, "start_time": start + beat,
                    "duration": 0.12, "velocity": 65
                })
        for p in chord[:2]:
            notes.append({
                "pitch": p - 12, "start_time": start,
                "duration": 0.15, "velocity": 45
            })
    return notes


# ─── Variation 2: "Liquid Flow" — lyrical, smooth ──────────────────────────

def build_v2_melody():
    notes = []
    motifs = [
        [64, 71, 76, 79, 76, 71, 67, 64],
        [67, 71, 76, 79, 76, 71, 64, 67],
        [68, 75, 80, 83, 80, 75, 71, 68],
        [70, 74, 82, 79, 70, 67, 64, 67],
    ]
    for bar_i, motif in enumerate(motifs):
        start = bar_i * BAR
        for i, p in enumerate(motif):
            t = start + i * 0.5
            vel = 60 + (i * 4)
            notes.append({
                "pitch": p, "start_time": round(t, 3),
                "duration": 0.4, "velocity": min(vel, 95)
            })
        if bar_i in [1, 2]:
            grace_p = motifs[bar_i][0] - 2
            notes.append({
                "pitch": grace_p, "start_time": start - 0.08,
                "duration": 0.08, "velocity": 50
            })
    return notes


def build_v2_arp():
    notes = []
    for bar_i, arp in enumerate(ORIGINAL_ARP_BARS):
        start = bar_i * BAR
        for i in range(8):
            pitch = arp[i % len(arp)]
            t = start + i * 0.5
            notes.append({
                "pitch": pitch, "start_time": round(t, 3),
                "duration": 0.35, "velocity": 55
            })
        for sub in [1.5, 5.5]:
            pitch = arp[(int(sub * 2)) % len(arp)] + 12
            notes.append({
                "pitch": pitch, "start_time": start + sub,
                "duration": 0.1, "velocity": 70
            })
    return notes


def build_v2_bass():
    notes = []
    for bar_i in range(4):
        start = bar_i * BAR
        bass_root = ORIGINAL_BASS_BARS[bar_i][0]
        notes.append({
            "pitch": bass_root, "start_time": start,
            "duration": BAR - 0.1, "velocity": 78
        })
        notes.append({
            "pitch": bass_root + 7, "start_time": start + 2.5,
            "duration": 0.4, "velocity": 60
        })
    return notes


def build_v2_pad():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        for p in chord:
            for offset in [0, 12, 24]:
                vel = [28, 30, 25][offset // 12] if offset > 0 else 25
                notes.append({
                    "pitch": p + offset, "start_time": start,
                    "duration": BAR, "velocity": vel
                })
    return notes


def build_v2_vibes():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        notes.append({
            "pitch": chord[0] + 24, "start_time": start,
            "duration": 1.0, "velocity": 50
        })
        notes.append({
            "pitch": chord[1] + 24, "start_time": start + 2.0,
            "duration": 0.8, "velocity": 35
        })
    return notes


def build_v2_piano():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        for p in chord:
            notes.append({
                "pitch": p, "start_time": start,
                "duration": BAR - 0.2, "velocity": 50
            })
            notes.append({
                "pitch": p + 12, "start_time": start,
                "duration": BAR - 0.2, "velocity": 45
            })
    return notes


# ─── Variation 3: "Dark Jungle" — chopped, tense ───────────────────────────

def build_v3_melody():
    notes = []
    phrases = [
        [64, 71, 76, 79],
        [79, 76, 71],
        [68, 75, 80],
        [82, 79, 75, 70],
    ]
    for bar_i, phrase in enumerate(phrases):
        start = bar_i * BAR
        offsets = [0.0, 0.5, 1.5, 2.5, 3.5]
        for i, p in enumerate(phrase):
            t = start + offsets[i]
            vel = 95 - (i * 5)
            notes.append({
                "pitch": p, "start_time": round(t, 3),
                "duration": 0.15, "velocity": vel
            })
        ghost_pos = (bar_i * 0.7 + 2.2) % 4.0
        notes.append({
            "pitch": phrases[bar_i][0] - 12,
            "start_time": round(start + ghost_pos, 3),
            "duration": 0.08, "velocity": 35
        })
    sweep = [76, 71, 67, 64, 60, 56]
    for i, p in enumerate(sweep):
        notes.append({
            "pitch": p, "start_time": round(14.0 + i * 0.25, 3),
            "duration": 0.15, "velocity": 80 - i * 5
        })
    return notes


def build_v3_arp():
    notes = []
    for bar_i, arp in enumerate(ORIGINAL_ARP_BARS):
        start = bar_i * BAR
        positions = [0.0, 1.25, 2.5, 3.0]
        for i, pos in enumerate(positions):
            pitch = arp[i % len(arp)]
            vel = 80 if i % 2 == 0 else 55
            notes.append({
                "pitch": pitch, "start_time": round(start + pos, 3),
                "duration": 0.12, "velocity": vel
            })
        notes.append({
            "pitch": arp[0] + 12, "start_time": round(start + 3.75, 3),
            "duration": 0.08, "velocity": 40
        })
    return notes


def build_v3_bass():
    notes = []
    for bar_i in range(4):
        start = bar_i * BAR
        notes.append({
            "pitch": 40, "start_time": start,
            "duration": 0.5, "velocity": 105
        })
        for pos in [0.75, 1.75, 2.75, 3.75]:
            notes.append({
                "pitch": 40, "start_time": start + pos,
                "duration": 0.15, "velocity": 75
            })
        notes.append({
            "pitch": 52, "start_time": start + 2.0,
            "duration": 0.3, "velocity": 90
        })
    return notes


def build_v3_pad():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        root = chord[0]
        fifth = chord[0] + 7
        for p in [root, fifth]:
            notes.append({
                "pitch": p + 12, "start_time": start,
                "duration": BAR, "velocity": 30
            })
        for p in chord[1:3]:
            notes.append({
                "pitch": p + 12, "start_time": start + 2.0,
                "duration": 0.4, "velocity": 50
            })
    return notes


def build_v3_vibes():
    notes = []
    for bar_i in range(4):
        start = bar_i * BAR
        positions = [0.5, 1.7, 3.3]
        for pos in positions:
            notes.append({
                "pitch": 76 + bar_i * 2, "start_time": round(start + pos, 3),
                "duration": 0.1, "velocity": 60
            })
    return notes


def build_v3_piano():
    notes = []
    for bar_i, chord in enumerate(ORIGINAL_PAD_BARS):
        start = bar_i * BAR
        for beat in [0.75, 2.25, 3.5]:
            for p in chord:
                notes.append({
                    "pitch": p, "start_time": start + beat,
                    "duration": 0.08, "velocity": 70
                })
        notes.append({
            "pitch": chord[0] - 12, "start_time": start,
            "duration": 0.1, "velocity": 40
        })
    return notes


# ─── Variation definitions ─────────────────────────────────────────────────

VARIATIONS = [
    {
        "name": "DnB-Forward-Pulse", "focus": "rhythmic",
        "clip_index": 2, "color": 8,
        "builders": {
            "melody": build_v1_melody, "arp": build_v1_arp, "bass": build_v1_bass,
            "pad": build_v1_pad, "vibes": build_v1_vibes, "piano": build_v1_piano,
        },
    },
    {
        "name": "DnB-Liquid-Flow", "focus": "melodic",
        "clip_index": 3, "color": 10,
        "builders": {
            "melody": build_v2_melody, "arp": build_v2_arp, "bass": build_v2_bass,
            "pad": build_v2_pad, "vibes": build_v2_vibes, "piano": build_v2_piano,
        },
    },
    {
        "name": "DnB-Dark-Jungle", "focus": "dynamic",
        "clip_index": 4, "color": 14,
        "builders": {
            "melody": build_v3_melody, "arp": build_v3_arp, "bass": build_v3_bass,
            "pad": build_v3_pad, "vibes": build_v3_vibes, "piano": build_v3_piano,
        },
    },
]

VOICE_TO_TRACK = {
    "melody": "01-Melody-Lead",
    "arp": "02-Arpeggio-Harp",
    "bass": "03-Bass-Foundation",
    "pad": "04-Harmony-Pad",
    "vibes": "05-Countermelody",
    "piano": "06-Piano-Backbone",
}


def main():
    print("🥁 Building three D&B / Jungle variations of Fantaisie-Impromptu...")
    print("   Tempo: 174 BPM | Clip length: 4 bars (16 beats)")
    print()

    # Get track indices
    r = cmd("get_all_tracks_info")
    if not r or r.get("status") != "success":
        print("❌ Failed to get tracks")
        return
    track_map = {}
    for t in r.get("result", {}).get("tracks", []):
        if t.get("is_midi"):
            track_map[t["name"]] = t["index"]
    print(f"Track map: {track_map}")
    print()

    for var in VARIATIONS:
        print(f"━━━ Variation: {var['name']} (focus: {var['focus']}) ━━━")
        for voice, builder in var["builders"].items():
            track_name = VOICE_TO_TRACK[voice]
            track_idx = track_map.get(track_name)
            if track_idx is None:
                print(f"  ⚠  Track {track_name} not found")
                continue
            notes = builder()
            clip_idx = var["clip_index"]
            clip_name = f"{var['name']} ({voice})"

            # Delete existing clip first (cleanup)
            cmd("delete_clip", {"track_index": track_idx, "clip_index": clip_idx})

            # Create clip
            r = cmd("create_clip", {
                "track_index": track_idx, "clip_index": clip_idx, "length": CLIP_LENGTH
            })
            if r.get("status") != "success":
                print(f"  ❌ Create clip failed for {track_name}: {r}")
                continue

            # Add notes in batches
            for batch_start in range(0, len(notes), 500):
                batch = notes[batch_start:batch_start + 500]
                cmd("add_notes_to_clip", {
                    "track_index": track_idx, "clip_index": clip_idx, "notes": batch
                })

            # Configure clip
            cmd("set_clip_looping", {"track_index": track_idx, "clip_index": clip_idx, "looping": True})
            cmd("set_clip_name", {"track_index": track_idx, "clip_index": clip_idx, "name": clip_name})
            cmd("set_clip_color", {"track_index": track_idx, "clip_index": clip_idx, "color_index": var["color"]})
            print(f"  ✅ [{track_idx}] {track_name:25s} slot {clip_idx}: {len(notes)} notes")

        print()

    # Set tempo
    print("🎵 Setting tempo to 174 BPM...")
    cmd("set_tempo", {"tempo": 174})

    print()
    print("✨ Three D&B / Jungle variations built successfully!")
    print(f"   Tempo: 174 BPM | Clip length: {CLIP_LENGTH} beats (~{CLIP_LENGTH * 60 / 174:.1f}s)")
    print()
    print("Variation focus:")
    print("  • V1 'Forward Pulse' — rhythmic drive, syncopated stabs, walk-up bass")
    print("  • V2 'Liquid Flow'    — lyrical, long tones, ornaments, smooth bass")
    print("  • V3 'Dark Jungle'    — chopped, fragmented, ghost notes, reese-style bass")


if __name__ == "__main__":
    main()
