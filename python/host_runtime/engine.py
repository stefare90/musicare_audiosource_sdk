import sys
import importlib
import traceback
from typing import Optional
from flask import Flask, request, jsonify

from musicare_plugin_sdk import Track, BaseAudioSourcePlugin


def create_app() -> Flask:
    """
    Creates and configures the Flask host RPC daemon application.
    """
    app = Flask(__name__)
    active_plugin: Optional[BaseAudioSourcePlugin] = None

    @app.route('/ping', methods=['GET'])
    def ping():
        """
        Health-check endpoint returning the daemon state and active plugin metadata.
        """
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
        Dynamically loads an unzipped plugin directory into memory by executing get_plugin().
        """
        nonlocal active_plugin
        try:
            data = request.get_json(force=True)
            plugin_dir = data.get('plugin_dir')
            module_name = data.get('module_name', 'main')

            if not plugin_dir:
                return jsonify({"error": "Missing required 'plugin_dir' parameter"}), 400

            # 1. Add the extracted plugin directory to the head of sys.path
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            # 2. Dynamically import the entry-point module (defaults to 'main.py')
            plugin_module = importlib.import_module(module_name)

            # 3. Invoke the standard factory function: get_plugin()
            if not hasattr(plugin_module, 'get_plugin'):
                raise AttributeError(
                    f"Entry-point module '{module_name}' must expose a factory function 'get_plugin()'."
                )

            instance = plugin_module.get_plugin()

            # 4. Strict contract verification against the SDK base class
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
        """
        Resolves track metadata into an ordered list of playable audio stream sources.
        """
        nonlocal active_plugin
        if not active_plugin:
            return jsonify({"error": "No plugin currently loaded. Call /load_plugin first."}), 400

        try:
            data = request.get_json(force=True)
            track_dict = data.get('track', {})
            quality = data.get('quality', 'high')

            # Parse track payload into SDK domain model
            track = Track.from_dict(track_dict)

            # Execute plugin stream resolution
            sources = active_plugin.get_stream(track, quality)

            return jsonify([s.to_dict() for s in sources]), 200

        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({"error": str(e), "traceback": tb}), 500

    return app


def start_daemon(port: int = 9765) -> None:
    """
    Starts the blocking Flask server daemon on all interfaces.
    """
    print(f"🐍 [HOST] Starting fixed audio source daemon on 0.0.0.0:{port}...", flush=True)
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)