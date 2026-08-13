#!/usr/bin/env python3
"""
Build V1 (Forward Pulse) only.
"""
import json, socket, time, sys
sys.path.insert(0, '/Users/martin/ableton-bridge')
from dnb_variations import build_v1_melody, build_v1_arp, build_v1_bass, build_v1_pad, build_v1_vibes, build_v1_piano

HOST = "127.0.0.1"
PORT = 9877

def cmd(t, p={}):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)
    s.connect((HOST, PORT))
    s.sendall((json.dumps({'type':t,'params':p})+'\n').encode())
    buf = b''
    while True:
        c = s.recv(8192)
        if not c: break
        buf += c
        if b'\n' in buf: break
    s.close()
    return json.loads(buf.split(b'\n')[0].decode())

# Get track map
r = cmd('get_all_tracks_info')
track_map = {}
for t in r['result']['tracks']:
    if t.get('is_midi'):
        track_map[t['name']] = t['index']

builders = [
    ('01-Melody-Lead', build_v1_melody),
    ('02-Arpeggio-Harp', build_v1_arp),
    ('03-Bass-Foundation', build_v1_bass),
    ('04-Harmony-Pad', build_v1_pad),
    ('05-Countermelody', build_v1_vibes),
    ('06-Piano-Backbone', build_v1_piano),
]

for track_name, builder in builders:
    track_idx = track_map[track_name]
    notes = builder()
    clip_name = f'DnB-Forward-Pulse ({track_name[3:].lower().split("-")[0]})'

    # Delete first
    cmd('delete_clip', {'track_index': track_idx, 'clip_index': 2})
    time.sleep(0.3)

    # Create
    t = time.time()
    r = cmd('create_clip', {'track_index': track_idx, 'clip_index': 2, 'length': 16.0})
    print(f'[{track_idx}] {track_name}: create {r.get("status")} ({time.time()-t:.2f}s)', flush=True)
    time.sleep(0.3)

    # Add notes
    t = time.time()
    for batch_start in range(0, len(notes), 500):
        batch = notes[batch_start:batch_start+500]
        cmd('add_notes_to_clip', {'track_index': track_idx, 'clip_index': 2, 'notes': batch})
    print(f'  -> notes: {len(notes)} added ({time.time()-t:.2f}s)', flush=True)
    time.sleep(0.3)

    # Configure
    cmd('set_clip_looping', {'track_index': track_idx, 'clip_index': 2, 'looping': True})
    cmd('set_clip_name', {'track_index': track_idx, 'clip_index': 2, 'name': clip_name})
    cmd('set_clip_color', {'track_index': track_idx, 'clip_index': 2, 'color_index': 8})
    time.sleep(0.2)
    print(f'  ✅ {track_name} done', flush=True)
