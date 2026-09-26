"""Tests for the Remote Script protected-track guard and playback fix.

The Live API (_Framework) is not importable outside Ableton, so it is stubbed.
"""
import importlib
import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture(scope="module")
def rs():
    if "_Framework.ControlSurface" not in sys.modules:
        fw = types.ModuleType("_Framework")
        cs = types.ModuleType("_Framework.ControlSurface")

        class ControlSurface(object):
            pass

        cs.ControlSurface = ControlSurface
        sys.modules["_Framework"] = fw
        sys.modules["_Framework.ControlSurface"] = cs
    # Other tests register a stub package under "AbletonBridge_Remote_Script";
    # load the real package under a private name so both can coexist.
    import importlib.util
    import pathlib
    pkg_dir = pathlib.Path(__file__).resolve().parents[1] / "AbletonBridge_Remote_Script"
    name = "_abletonbridge_rs_real"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, pkg_dir / "__init__.py", submodule_search_locations=[str(pkg_dir)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _song(n=4, bridge_at=0):
    song = MagicMock()
    tracks = []
    for i in range(n):
        t = MagicMock()
        dev = MagicMock()
        dev.name = "AbletonBridge_M4L" if i == bridge_at else "Wavetable"
        t.devices = [dev]
        tracks.append(t)
    song.tracks = tracks
    return song


@pytest.mark.parametrize("cmd,params", [
    ("set_track_name", {"track_index": 0, "name": "x"}),
    ("set_track_name", {"name": "x"}),                     # missing index -> default 0
    ("delete_track", {"track_index": 0}),
    ("create_clip", {"track_index": 0, "clip_index": 1}),
    ("set_device_parameter", {"track_index": 0, "parameter_name": "Drive", "value": 1}),
    ("group_tracks", {"track_indices": [0, 2]}),
    ("move_device", {"track_index": 2, "dest_track_index": 0}),
    ("create_midi_track", {"index": 0}),
])
def test_track0_blocked(rs, cmd, params):
    with pytest.raises(PermissionError):
        rs.guard_protected_track(_song(), cmd, params)


@pytest.mark.parametrize("cmd,params", [
    ("set_track_name", {"track_index": 2, "name": "Bass"}),
    ("create_clip", {"track_index": 3, "clip_index": 0}),
    ("set_track_name", {"track_index": 0, "track_type": "return", "name": "A"}),
    ("create_midi_track", {"index": -1}),
    ("set_tempo", {"tempo": 140}),
])
def test_other_targets_allowed(rs, cmd, params):
    rs.guard_protected_track(_song(), cmd, params)


def test_bridge_device_on_other_index_blocked(rs):
    with pytest.raises(PermissionError):
        rs.guard_protected_track(_song(bridge_at=2), "set_track_name", {"track_index": 2})


def test_guard_covers_all_track_index_commands(rs):
    assert "set_track_name" in rs._TRACK_INDEX_COMMANDS
    assert "delete_track" in rs._TRACK_INDEX_COMMANDS
    assert len(rs._TRACK_INDEX_COMMANDS) > 100


def test_duplicate_to_arrangement_requires_time(rs):
    with pytest.raises(ValueError):
        rs._required_time({"track_index": 2, "clip_index": 0})
    assert rs._required_time({"time": 16}) == 16.0
    assert rs._required_time({"destination_time": 8}) == 8.0


def test_start_playback_resumes_at_playhead(rs):
    song = MagicMock()
    song.current_song_time = 64.0
    song.is_playing = True
    res = rs.handlers.session.start_playback(song)
    song.continue_playing.assert_called_once()
    song.start_playing.assert_not_called()
    assert res["position"] == 64.0
