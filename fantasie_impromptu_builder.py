#!/usr/bin/env python3
"""
Chopin – Fantaisie-Impromptu, Op. 66
Atmospheric Cinematic Reinterpretation
Key: E-flat minor | Tempo: 76 bpm (half note) = 152 bpm quarter
"""

import json
import socket
import time
import sys

HOST = "127.0.0.1"
PORT = 9877

# ─── TCP Helpers ────────────────────────────────────────────────────────────

def send_command(cmd_type, params=None):
    """Send a JSON command to Ableton Bridge on TCP 9877."""
    if params is None:
        params = {}
    payload = json.dumps({"type": cmd_type, "params": params}) + "\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30.0)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(payload.encode("utf-8"))
        # Read response
        buf = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in buf:
                line, _ = buf.split(b"\n", 1)
                try:
                    result = json.loads(line.decode("utf-8").strip())
                    status = result.get("status", "")
                    if status == "error":
                        print(f"  ⚠ ERROR: {result.get('message', 'unknown')}", file=sys.stderr)
                    return result
                except json.JSONDecodeError:
                    pass
    except socket.timeout:
        print(f"  ⏱ Timeout on {cmd_type}", file=sys.stderr)
    except Exception as e:
        print(f"  💥 Error on {cmd_type}: {e}", file=sys.stderr)
    finally:
        sock.close()
    return None

def brief_wait(secs=0.15):
    """Small delay between modifying commands for stability."""
    time.sleep(secs)


# ─── Musical Definitions ────────────────────────────────────────────────────
# Key: E-flat minor (transposed from C# minor, +4 semitones)
# Tempo: 76 bpm (half note) → 152 bpm quarter

BPM = 76
# Note length helpers (in beats at quarter-note level, but we think in half-notes)
# At 76 bpm half-note = quarter-note = 60/152 = 0.395 sec
# In session view, clips use beats at the denominator of time signature
# 2/2 time (cut time) → beat = half note
# For clip creation, length is in beats. If time signature is 2/2, 1 beat = 1 half note.
# For simplicity, we use 4/4 time with the tempo representing quarter notes.

# Section A: Fast triplet arpeggios with melody in dotted notes
# Right hand: 16th-note triplet arpeggios (12 notes per half-note beat)
# Left hand: quarter-note bass + chord rhythm
# Melody: dotted 8th + 16th pattern (hemiola effect against triplets)

# We'll encode the full piece as note data per instrument
# Section A is 16 bars + Section B is 20 bars + Section A reprise + Coda

# ─── Helper: Build melody notes for Section A ──────────────────────────────

# The Fantaisie-Impromptu theme: C# minor → E-flat minor (+4 semitones)
# Original right hand: melody in dotted 8th+16th against LH triplets
# Original left hand: 6-note triplet arpeggios per half-note beat

# For our reinterpretation, we split the texture across instruments

def build_section_a_bars(num_bars=8, offset=0.0):
    """
    Generate note data for Section A.
    Returns dict of lists: melody_notes, triplet_notes, bass_notes, harmony_notes
    The harmonic structure in E-flat minor:
    Bar 1-2: Ebm (i) - Ebm/Gb - Ebm/Bb
    Bar 3-4: Abm (iv) - Bb7 (V7)  
    Bar 5-6: Ebm (i) - ...
    Bar 7-8: Bb7 (V7) - Ebm (i)
    """
    notes = {
        "melody": [],
        "triplets": [],
        "bass": [],
        "harmony": [],
        "counter": [],
    }
    
    # Harmonic progression for Section A (E-flat minor)
    # Chord roots and qualities
    chords_a = [
        ("Ebm",  [52, 55, 59, 64]),   # Ebm: Eb3, Gb3, Bb3, Eb4
        ("Ebm",  [52, 55, 59, 64]),
        ("Abm",  [56, 59, 63, 68]),   # Abm: Ab3, Cb4, Eb4, Ab4
        ("Bb7",  [58, 62, 65, 69]),   # Bb7: Bb3, D4, F4, Ab4
        ("Ebm",  [52, 55, 59, 64]),
        ("CbM7", [56, 60, 63, 67]),   # CbM7: Cb4, Fb4... enharmonic Bmaj7? Let's use: Cb=71
        ("Fm7b5",[53, 56, 59, 63]),   # Fm7b5
        ("Bb7",  [58, 62, 65, 69]),
    ]
    
    # Actually, in E-flat minor (6 flats):
    # Ebm = Eb Gb Bb (i)
    # Abm = Ab Cb Eb (iv) 
    # Bb7 = Bb D F Ab (V7)
    # CbM7 = Cb Eb Gb Bb (bVIM7)
    # Fm7b5 = F Ab Cb Eb (iiø7)
    
    # Melodic notes (the right-hand dotted-rhythm melody)
    melody_pitches_a = [
        # Bar 1 - melodic phrase (dotted 8th + 16th pattern)
        [64, 67, 71, 76, 79, 76, 71, 67, 64, 67, 71, 76],  # Eb4, Gb4, Bb4, Eb5...
        # Bar 2
        [79, 76, 71, 67, 64, 67, 71, 76, 79, 76, 71, 76],
        # Bar 3
        [68, 71, 75, 80, 83, 80, 75, 71, 68, 71, 75, 80],
        # Bar 4
        [82, 79, 75, 71, 68, 71, 75, 80, 82, 79, 75, 71],
        # Bar 5
        [64, 67, 71, 76, 79, 76, 71, 67, 64, 67, 71, 76],
        # Bar 6
        [79, 76, 71, 67, 64, 67, 71, 76, 79, 83, 79, 76],
        # Bar 7 - building tension
        [70, 73, 77, 82, 85, 82, 77, 73, 70, 73, 77, 82],
        # Bar 8 - resolution
        [85, 82, 77, 73, 70, 73, 77, 82, 85, 82, 77, 82],
    ]

    # Triplet arpeggios (original right hand, now separated)
    # 12 notes per bar (triplets in 2/2 = 6 groups of 2, or 3 groups of 4)
    # In 4/4: 3 groups of 4 16th-note triplets per beat = 12 per bar
    triplet_pitches_a = [
        # Each list = 12 pitch values per bar
        [52, 55, 59, 64, 59, 55, 52, 55, 59, 64, 59, 55],  # Ebm
        [52, 55, 59, 64, 59, 55, 52, 55, 59, 64, 59, 55],
        [56, 59, 63, 68, 63, 59, 56, 59, 63, 68, 63, 59],  # Abm
        [58, 62, 65, 69, 65, 62, 58, 62, 65, 69, 65, 62],  # Bb7
        [52, 55, 59, 64, 59, 55, 52, 55, 59, 64, 59, 55],  # Ebm
        [56, 60, 63, 67, 63, 60, 56, 60, 63, 67, 63, 60],  # CbM7
        [53, 56, 59, 63, 59, 56, 53, 56, 59, 63, 59, 56],  # Fm7b5
        [58, 62, 65, 69, 65, 62, 58, 62, 65, 69, 65, 62],  # Bb7
    ]

    # Bass notes (quarter notes = 4 per bar in 4/4, or half notes)
    bass_a = [
        [52], [52, 55], [56], [58], [52], [56], [53], [58],
    ]
    
    # Harmony chord (sustained pad)
    harmony_a = [
        [52, 55, 59],  # Ebm
        [52, 55, 59],
        [56, 59, 63],  # Abm
        [58, 62, 65],  # Bb7
        [52, 55, 59],
        [56, 60, 63],  # CbM7
        [53, 56, 59],  # Fm7b5
        [58, 62, 65],  # Bb7
    ]

    # Scale run countermelody
    counter_a = [
        [59, 55, 52], [64, 59, 55], [63, 59, 56], [65, 62, 58],
        [59, 55, 52], [63, 60, 56], [59, 56, 53], [65, 62, 58],
    ]

    for bar in range(min(num_bars, len(melody_pitches_a))):
        bar_start = offset + bar * 4.0  # 4 beats per bar (4/4)
        
        # Melody: dotted 8th+16th rhythm (12 notes per bar, grouped as 4 groups of 3)
        # Pattern: dotted 8th (0.75) + 16th (0.25) + 8th (0.5)+ 8th (0.5) ...
        # Actually let's use a simpler pattern: 3 beats of triplet feel
        for i, pitch in enumerate(melody_pitches_a[bar]):
            note_time = bar_start + i * (4.0 / 12)
            dur = 4.0 / 18  # shorter
            notes["melody"].append({
                "pitch": pitch,
                "start_time": round(note_time, 3),
                "duration": round(dur, 3),
                "velocity": 80 + (i % 3) * 5
            })
        
        # Triplets: 12 notes per bar evenly spaced
        for i, pitch in enumerate(triplet_pitches_a[bar]):
            note_time = bar_start + i * (4.0 / 12)
            dur = 4.0 / 20  # short, staccato-like
            velocity = 55 + (i % 4) * 8
            notes["triplets"].append({
                "pitch": pitch,
                "start_time": round(note_time, 3),
                "duration": round(dur, 3),
                "velocity": velocity
            })
        
        # Bass: held notes (half notes or whole notes)
        for i, pitch in enumerate(bass_a[bar]):
            if len(bass_a[bar]) == 1:
                # Whole note
                notes["bass"].append({
                    "pitch": pitch,
                    "start_time": bar_start,
                    "duration": 4.0,
                    "velocity": 65
                })
            elif len(bass_a[bar]) > 1:
                # Two half notes
                notes["bass"].append({
                    "pitch": bass_a[bar][i],
                    "start_time": bar_start + i * 2.0,
                    "duration": 2.0,
                    "velocity": 60 + i * 5
                })
        
        # Harmony: sustained chords (whole notes)
        for pitch in harmony_a[bar]:
            notes["harmony"].append({
                "pitch": pitch,
                "start_time": bar_start,
                "duration": 4.0,
                "velocity": 45 + (pitch % 5) * 3
            })
        
        # Countermelody: short accents
        for i, pitch in enumerate(counter_a[bar]):
            notes["counter"].append({
                "pitch": pitch,
                "start_time": bar_start + i * 1.33,
                "duration": 0.5,
                "velocity": 60
            })

    return notes


def build_section_b_bars(num_bars=10, offset=0.0, section_a_notes=None):
    """
    Section B - Lyrical Moderato cantabile
    In original: D-flat major. In our key: the relative major of Ebm is Gb major
    So Section B is in G-flat major (enharmonic F# major)
    """
    notes = {
        "melody": [],
        "triplets": [],
        "bass": [],
        "harmony": [],
        "counter": [],
    }
    
    # G-flat major chords
    chords_b = [
        ("GbM7",  [55, 59, 63, 66]),  # GbM7: Gb3, Bb3, Db4, F4
        ("Abm7",  [57, 60, 64, 68]),  # Abm7
        ("Dbm7",  [61, 64, 68, 72]),  # Dbm7
        ("GbM7",  [55, 59, 63, 66]),
        ("CbM7",  [56, 60, 63, 67]),  # equivalent to Bmaj7
        ("Abm7",  [57, 60, 64, 68]),
        ("Dbm7",  [61, 64, 68, 72]),
        ("GbM7",  [55, 59, 63, 66]),
        ("Ebm7",  [52, 55, 59, 62]),  # back toward Ebm
        ("Bb7sus4",[58, 61, 65, 68]), # dominant preparation
    ]
    
    # Melody for Section B (sustained, lyrical)
    melody_b = [
        [66, 71, 75, 78, 75, 71, 66, 59],
        [68, 71, 75, 80, 75, 71, 68, 64],
        [72, 75, 78, 83, 78, 75, 72, 68],
        [66, 71, 75, 78, 75, 71, 66, 59],
        [67, 71, 75, 78, 75, 71, 67, 63],
        [68, 71, 75, 80, 80, 75, 71, 68],
        [72, 75, 78, 83, 83, 78, 75, 72],
        [66, 71, 75, 78, 75, 71, 66, 59],
        [64, 67, 71, 74, 71, 67, 64, 59],
        [70, 73, 77, 82, 77, 73, 70, 65],
    ]
    
    # Arpeggiated accompaniment for Section B (broken chords)
    arpeggios_b = [
        [55, 59, 63, 66, 63, 59, 55, 59],
        [57, 60, 64, 68, 64, 60, 57, 60],
        [61, 64, 68, 72, 68, 64, 61, 64],
        [55, 59, 63, 66, 63, 59, 55, 59],
        [56, 60, 63, 67, 63, 60, 56, 60],
        [57, 60, 64, 68, 64, 60, 57, 60],
        [61, 64, 68, 72, 68, 64, 61, 64],
        [55, 59, 63, 66, 63, 59, 55, 59],
        [52, 55, 59, 62, 59, 55, 52, 55],
        [58, 61, 65, 68, 65, 61, 58, 61],
    ]
    
    # Bass notes for Section B
    bass_b = [
        [55], [57], [61], [55], [56], [57], [61], [55], [52], [58]
    ]
    
    # Harmony pads
    harmony_b = [
        [55, 59, 63],  # GbM7
        [57, 60, 64],  # Abm7
        [61, 64, 68],  # Dbm7  
        [55, 59, 63],
        [56, 60, 63],
        [57, 60, 64],
        [61, 64, 68],
        [55, 59, 63],
        [52, 55, 59],
        [58, 61, 65],
    ]
    
    # Countermelody (flute/vibes)
    counter_b = [
        [63, 66, 71],
        [64, 68, 71],
        [68, 72, 75],
        [63, 66, 71],
        [63, 67, 71],
        [64, 68, 71],
        [68, 72, 78],
        [63, 66, 71],
        [59, 62, 67],
        [65, 68, 73],
    ]

    for bar in range(min(num_bars, len(melody_b))):
        bar_start = offset + bar * 4.0

        # Melody: 8 notes per bar, more spaced
        for i, pitch in enumerate(melody_b[bar]):
            note_time = bar_start + i * 0.5
            dur = 0.3 + (0.2 if pitch > 75 else 0.3)
            notes["melody"].append({
                "pitch": pitch,
                "start_time": round(note_time, 3),
                "duration": round(dur, 3),
                "velocity": 75 + (i % 4) * 6
            })

        # Arpeggios: 8 notes per bar, flowing
        for i, pitch in enumerate(arpeggios_b[bar]):
            note_time = bar_start + i * 0.5
            dur = 0.25
            velocity = 50 + (i % 4) * 10
            notes["triplets"].append({
                "pitch": pitch,
                "start_time": round(note_time, 3),
                "duration": round(dur, 3),
                "velocity": velocity
            })

        # Bass
        for i, pitch in enumerate(bass_b[bar]):
            dur = 4.0
            notes["bass"].append({
                "pitch": pitch,
                "start_time": bar_start,
                "duration": dur,
                "velocity": 60
            })

        # Harmony
        for pitch in harmony_b[bar]:
            notes["harmony"].append({
                "pitch": pitch,
                "start_time": bar_start,
                "duration": 4.0,
                "velocity": 38 + (pitch % 3) * 4
            })

        # Counter
        for i, pitch in enumerate(counter_b[bar]):
            notes["counter"].append({
                "pitch": pitch,
                "start_time": bar_start + i * 1.33,
                "duration": 0.4,
                "velocity": 55
            })

    return notes


# ─── Generate All Note Data ────────────────────────────────────────────────

print("🎵 Generating Fantaisie-Impromptu note data...")

# Section A (8 bars)
sec_a = build_section_a_bars(8, offset=0.0)
# Section B (10 bars)
sec_b = build_section_b_bars(10, offset=32.0)
# Section A reprise (8 bars) - same as A but offset
sec_a2 = build_section_a_bars(8, offset=72.0)

# Coda (4 bars) - simplified coda
bass_coda = []
harmony_coda = []
coda_start = 104.0
coda_chords = [
    ([52], [52, 55, 59]),    # Ebm
    ([53], [53, 56, 59]),    # Fm7b5
    ([58], [58, 62, 65]),    # Bb7
    ([52], [52, 55, 64, 67]), # Ebm (final)
]
for bar_i, (bass_p, harm_p) in enumerate(coda_chords):
    bar_off = coda_start + bar_i * 4.0
    for p in bass_p:
        sec_a2["bass"].append({"pitch": p, "start_time": bar_off, "duration": 4.0, "velocity": 70})
    for p in harm_p:
        sec_a2["harmony"].append({"pitch": p, "start_time": bar_off, "duration": 4.0, "velocity": 50})
    # Final chord arpeggio
    sec_a2["triplets"].append({"pitch": 52, "start_time": bar_off, "duration": 0.5, "velocity": 60})
    if bar_i == 3:
        # Final flourish
        for i, p in enumerate([64, 67, 71, 76, 79, 83, 88]):
            sec_a2["melody"].append({
                "pitch": p,
                "start_time": bar_off + 2.0 + i * 0.25,
                "duration": 1.5 if i == 6 else 0.2,
                "velocity": 90 + i * 3
            })

# Merge sections
all_notes = {
    "melody": sec_a["melody"] + sec_b["melody"] + sec_a2["melody"],
    "triplets": sec_a["triplets"] + sec_b["triplets"] + sec_a2["triplets"],
    "bass": sec_a["bass"] + sec_b["bass"] + sec_a2["bass"],
    "harmony": sec_a["harmony"] + sec_b["harmony"] + sec_a2["harmony"],
    "counter": sec_a["counter"] + sec_b["counter"] + sec_a2["counter"],
}

print(f"  Generated {len(all_notes['melody'])} melody notes")
print(f"  Generated {len(all_notes['triplets'])} arpeggio/triplet notes")
print(f"  Generated {len(all_notes['bass'])} bass notes")
print(f"  Generated {len(all_notes['harmony'])} harmony notes")
print(f"  Generated {len(all_notes['counter'])} countermelody notes")

TOTAL_LENGTH = 112.0  # beats at 152 bpm = ~44 seconds


# ─── Build the Ableton Project ─────────────────────────────────────────────

print("\n🎛  Building Ableton Live project...")

# Step 0: Set tempo (152 bpm quarter = 76 bpm half)
print("\n1️⃣  Setting tempo and transport...")
r = send_command("set_tempo", {"tempo": BPM})
print(f"  Tempo: {BPM} bpm")
brief_wait()

# Set time signature to 4/4
r = send_command("set_song_loop", {
    "enabled": True,
    "start": 0.0,
    "length": TOTAL_LENGTH
})
brief_wait()

# ─── Create Return Tracks ──────────────────────────────────────────────────
print("\n2️⃣  Creating return tracks (Reverb + Delay)...")
r = send_command("create_return_track")
brief_wait(0.3)
r = send_command("create_return_track")
brief_wait(0.3)
# Name the return tracks (they're at indices 0 and 1 of return tracks)
r = send_command("set_track_name", {"track_index": 0, "name": "Reverb", "track_type": "return"})
brief_wait(0.2)
r = send_command("set_track_name", {"track_index": 1, "name": "Delay", "track_type": "return"})
brief_wait(0.2)

# ─── Instrument Track Definitions ──────────────────────────────────────────

# We'll create tracks and load instruments manually
instruments = [
    # (track_name, channel_type, clip_index)
    ("01-Melody-Lead",  "Synth"),
    ("02-Arpeggio-Harp", "Harp"),
    ("03-Bass-Foundation", "Bass"),
    ("04-Harmony-Pad", "Pad"),
    ("05-Countermelody", "Synth"),
    ("06-Piano-Backbone", "Piano"),
]

print("\n3️⃣  Creating tracks...")
track_indices = []
for name, instr_type in instruments:
    r = send_command("create_midi_track", {"index": -1})
    if r and "index" in r:
        idx = r["index"]
    else:
        # Try to get track info to find newly created track
        pass
    # Actually, create_midi_track returns {"index": idx, "name": "..."}
    idx = len(track_indices)  # fallback
    track_indices.append(idx)
    brief_wait(0.2)
    # Name the track
    send_command("set_track_name", {"track_index": idx, "name": name})
    brief_wait(0.1)
    print(f"  Created track {idx}: {name}")

# Use `get_all_tracks_info` to find actual indices
r = send_command("get_all_tracks_info")
if r:
    tracks_data = r
    print(f"  Current tracks: {r}")
else:
    tracks_data = None
    # Fallback: assume sequential indices
    # The return tracks take indices 0, 1, so our tracks start at 2
    # Group track might also exist
    print("  (fallback track indices)")

brief_wait(0.3)

# ─── Create Clips and Add Notes ──────────────────────────────────────────

# Map: voice_name -> track_index offset (after return tracks)
# We need to know which index each track actually got
# Let's use get_all_tracks_info to figure this out

# First let's see what tracks we have
print("\n4️⃣  Checking track layout...")
r = send_command("get_all_tracks_info")
if r and isinstance(r, dict) and "tracks" in r:
    tracks_info = r["tracks"]
    print(f"  Found {len(tracks_info)} tracks")
    for t in tracks_info:
        print(f"    [{t.get('index')}] {t.get('name', 'unnamed')}")
elif r and isinstance(r, dict):
    print(f"  Track info: {r}")
else:
    print(f"  Raw response: {r}")

# Let's get the current session info to understand the state
r = send_command("get_session_info")
print(f"  Session: {r}")
brief_wait(0.3)

print("\n Creating instruments and clips...")

# Now let's load instruments and create clips by actually finding the tracks
# Since we're building this blind, let me first get all tracks
r = send_command("get_all_tracks_info")
print(f"  ALL TRACKS: {json.dumps(r, indent=2)[:2000]}")