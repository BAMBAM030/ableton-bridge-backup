"""Regression tests for compressor sidechain behavior."""

import importlib
import sys
import types
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
REMOTE_ROOT = ROOT / "AbletonBridge_Remote_Script"
HANDLERS_ROOT = REMOTE_ROOT / "handlers"

# The Remote Script package imports Ableton's private _Framework in its package
# __init__.py. Unit tests run outside Live, so install lightweight package
# stubs and import the handler module directly from its package path.
pkg = types.ModuleType("AbletonBridge_Remote_Script")
pkg.__path__ = [str(REMOTE_ROOT)]
handlers_pkg = types.ModuleType("AbletonBridge_Remote_Script.handlers")
handlers_pkg.__path__ = [str(HANDLERS_ROOT)]
sys.modules.setdefault("AbletonBridge_Remote_Script", pkg)
sys.modules.setdefault("AbletonBridge_Remote_Script.handlers", handlers_pkg)

devices = importlib.import_module("AbletonBridge_Remote_Script.handlers.devices")


class Routing:
    def __init__(self, name):
        self.display_name = name


class SidechainIO:
    def __init__(self):
        self.available_routing_types = [Routing("No Input"), Routing("Kick")]
        self.available_routing_channels = [Routing("Pre FX"), Routing("Post FX")]
        self.routing_type = self.available_routing_types[0]
        self.routing_channel = self.available_routing_channels[0]


class Param:
    def __init__(self, name, value=0):
        self.name = name
        self.value = value


def make_song():
    sidechain = SidechainIO()
    sc_on = Param("S/C On", 0)
    compressor = SimpleNamespace(
        name="Compressor",
        class_name="Compressor",
        input_routings=[sidechain],
        parameters=[sc_on],
    )
    bass = SimpleNamespace(name="Bass", devices=[compressor])
    kick = SimpleNamespace(name="Kick", devices=[])
    song = SimpleNamespace(tracks=[bass, kick], return_tracks=[])
    return song, compressor, sidechain, sc_on


def make_song_without_deviceio():
    routings = [Routing("No Input"), Routing("Kick")]
    channels = [Routing(""), Routing("Post FX")]
    sc_on = Param("S/C On", 0)
    compressor = SimpleNamespace(
        name="Compressor",
        class_name="Compressor",
        input_routing_type=routings[0],
        input_routing_channel=channels[0],
        available_input_routing_types=routings,
        available_input_routing_channels=channels,
        parameters=[sc_on],
    )
    bass = SimpleNamespace(name="Bass", devices=[compressor])
    kick = SimpleNamespace(name="Kick", devices=[])
    song = SimpleNamespace(tracks=[bass, kick], return_tracks=[])
    return song, compressor, sc_on


def test_set_compressor_sidechain_enables_toggle():
    song, compressor, sidechain, sc_on = make_song()

    result = devices.set_compressor_sidechain(
        song, 0, 0, input_type="Kick", input_channel="Post FX"
    )

    assert result["input_routing_type"] == "Kick"
    assert result["input_routing_channel"] == "Post FX"
    assert result["sidechain_enabled"] is True
    assert sidechain.routing_type.display_name == "Kick"
    assert sidechain.routing_channel.display_name == "Post FX"
    assert sc_on.value == 1


def test_set_sidechain_by_name_enables_toggle():
    song, compressor, sidechain, sc_on = make_song()

    result = devices.set_sidechain_by_name(song, 0, 0, "Kick")

    assert result["success"] is True
    assert result["sidechain_enabled"] is True
    assert result["routing_via"] == "DeviceIO"
    assert sc_on.value == 1


def test_set_compressor_sidechain_falls_back_to_compressor_device_routing():
    song, compressor, sc_on = make_song_without_deviceio()

    result = devices.set_compressor_sidechain(
        song, 0, 0, input_type="Kick", input_channel="Post FX"
    )

    assert result["input_routing_type"] == "Kick"
    assert result["input_routing_channel"] == "Post FX"
    assert result["routing_via"] == "CompressorDevice"
    assert result["sidechain_enabled"] is True
    assert compressor.input_routing_type.display_name == "Kick"
    assert compressor.input_routing_channel.display_name == "Post FX"
    assert sc_on.value == 1


def test_set_sidechain_by_name_falls_back_to_compressor_device_routing():
    song, compressor, sc_on = make_song_without_deviceio()

    result = devices.set_sidechain_by_name(song, 0, 0, "Kick")

    assert result["success"] is True
    assert result["routing_via"] == "CompressorDevice"
    assert result["sidechain_enabled"] is True
    assert compressor.input_routing_type.display_name == "Kick"
    assert sc_on.value == 1
