import importlib.util
import os
import sys
import traceback
from typing import Optional

from flask import Flask, jsonify, request
from musicare_plugin_sdk import (
    BaseAudioSourcePlugin,
    LoadPluginRequest,
    ResolveStreamRequest,
    ResolveTrackRequest,
    ResolvedTrackPlayback,
)

app = Flask(__name__)

_active_plugin: Optional[BaseAudioSourcePlugin] = None


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "plugin_loaded": _active_plugin is not None,
        "loaded": getattr(_active_plugin, "name", None),
    }), 200


@app.route("/load_plugin", methods=["POST"])
def load_plugin():
    global _active_plugin
    try:
        data = request.get_json(force=True) or {}
        req = LoadPluginRequest.from_dict(data)

        if not os.path.exists(req.plugin_dir):
            return jsonify({"success": False, "error": f"Plugin directory does not exist: {req.plugin_dir}"}), 400

        if req.plugin_dir not in sys.path:
            sys.path.insert(0, req.plugin_dir)
        src_dir = os.path.join(req.plugin_dir, "src")
        if os.path.isdir(src_dir) and src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        entry_path = os.path.join(src_dir, f"{req.module_name}.py")
        if not os.path.exists(entry_path):
            entry_path = os.path.join(req.plugin_dir, f"{req.module_name}.py")

        if not os.path.exists(entry_path):
            return jsonify({"success": False, "error": f"Entry point not found: {entry_path}"}), 400

        spec = importlib.util.spec_from_file_location(req.module_name, entry_path)
        if spec is None or spec.loader is None:
            return jsonify({"success": False, "error": f"Cannot create module spec for {entry_path}"}), 400

        module = importlib.util.module_from_spec(spec)
        sys.modules[req.module_name] = module
        spec.loader.exec_module(module)

        if not hasattr(module, "get_plugin"):
            return jsonify({"success": False, "error": "Entry point is missing get_plugin() factory"}), 400

        plugin = module.get_plugin()
        _active_plugin = plugin

        return jsonify({
            "success": True,
            "loaded": getattr(plugin, "name", "Unknown Plugin"),
            "id": getattr(plugin, "id", "unknown"),
            "version": getattr(plugin, "version", "1.0.0"),
        }), 200
    except ValueError as ve:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/resolve_track", methods=["POST"])
def resolve_track():
    global _active_plugin
    if _active_plugin is None:
        return jsonify({"error": "No audio source plugin loaded in host engine"}), 500

    try:
        data = request.get_json(force=True) or {}
        req = ResolveTrackRequest.from_dict(data)

        candidates = _active_plugin.search_candidates(req.track)
        if not candidates:
            return jsonify({"error": f"No playable stream candidates found for '{req.track.name}'"}), 404

        primary_candidate = candidates[0]
        stream = _active_plugin.resolve_stream(primary_candidate.id, req.quality)

        playback = ResolvedTrackPlayback(
            stream=stream,
            candidates=candidates,
            active_candidate_id=primary_candidate.id,
        )

        return jsonify(playback.to_dict()), 200
    except ValueError as ve:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"error": str(e)}), 500


@app.route("/resolve_stream", methods=["POST"])
def resolve_stream():
    global _active_plugin
    if _active_plugin is None:
        return jsonify({"error": "No audio source plugin loaded in host engine"}), 500

    try:
        data = request.get_json(force=True) or {}
        req = ResolveStreamRequest.from_dict(data)
        stream = _active_plugin.resolve_stream(req.candidate_id, req.quality)
        return jsonify(stream.to_dict()), 200
    except ValueError as ve:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({"error": str(e)}), 500


def start_daemon(port: Optional[int] = None, host: str = "127.0.0.1"):
    """Start the Flask host daemon on the assigned port."""
    if port is None:
        port = int(os.environ.get("PORT", "8765"))
    app.run(host=host, port=int(port), debug=False)
