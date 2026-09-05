import sys
import os
import importlib.util
import traceback
from typing import Optional
from flask import Flask, request, jsonify

from musicare_plugin_sdk import Track, BaseAudioSourcePlugin


def create_app() -> Flask:
    app = Flask(__name__)
    active_plugin: Optional[BaseAudioSourcePlugin] = None

    @app.route('/ping', methods=['GET'])
    def ping():
        nonlocal active_plugin
        return jsonify({
            "status": "ready",
            "server_type": "FIXED_HOST",
            "plugin_loaded": active_plugin is not None,
            "id": active_plugin.id if active_plugin else None,
            "name": active_plugin.name if active_plugin else None,
            "version": active_plugin.version if active_plugin else None,
        }), 200

    @app.route('/load_plugin', methods=['POST'])
    def load_plugin():
        """
        Dynamically loads an unzipped plugin directory by loading its entrypoint
        via explicit file location to avoid namespace collisions with host's main.py.
        """
        nonlocal active_plugin
        try:
            data = request.get_json(force=True)
            plugin_dir = data.get('plugin_dir')

            if not plugin_dir or not os.path.isdir(plugin_dir):
                return jsonify({"error": f"Invalid or missing plugin_dir: {plugin_dir}"}), 400

            # 1. Add the plugin directory to sys.path so it can import its local files (plugin.py, extractor.py)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            # 2. Locate the plugin's entry point file
            entry_file = os.path.join(plugin_dir, "main.py")
            if not os.path.exists(entry_file):
                entry_file = os.path.join(plugin_dir, "plugin.py")
            if not os.path.exists(entry_file):
                raise FileNotFoundError(f"Neither main.py nor plugin.py found in '{plugin_dir}'")

            # 3. Load the entrypoint explicitly without colliding with host_runtime/main.py!
            spec = importlib.util.spec_from_file_location("dynamic_plugin_entry", entry_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for '{entry_file}'")

            plugin_module = importlib.util.module_from_spec(spec)
            sys.modules["dynamic_plugin_entry"] = plugin_module
            spec.loader.exec_module(plugin_module)

            # 4. Invoke the factory function: get_plugin()
            if not hasattr(plugin_module, 'get_plugin'):
                raise AttributeError(
                    f"Entry-point '{entry_file}' must expose a factory function 'get_plugin()'."
                )

            instance = plugin_module.get_plugin()

            # 5. Contract verification
            if not isinstance(instance, BaseAudioSourcePlugin):
                raise TypeError(
                    f"Plugin instance '{type(instance).__name__}' does not inherit from BaseAudioSourcePlugin."
                )

            active_plugin = instance

            return jsonify({
                "success": True,
                "loaded": active_plugin.name,
                "id": active_plugin.id,
                "version": active_plugin.version,
            }), 200

        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": tb}), 500

    @app.route('/get_stream', methods=['POST'])
    def get_stream():
        nonlocal active_plugin
        if not active_plugin:
            return jsonify({"error": "No plugin currently loaded. Call /load_plugin first."}), 400

        try:
            data = request.get_json(force=True)
            track_dict = data.get('track', {})
            quality = data.get('quality', 'high')

            track = Track.from_dict(track_dict)
            sources = active_plugin.get_stream(track, quality)

            return jsonify([s.to_dict() for s in sources]), 200

        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": tb}), 500

    return app


def start_daemon(port: int = 9765) -> None:
    print(f"🐍 [HOST] Starting fixed audio source daemon on 0.0.0.0:{port}...", flush=True)
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)