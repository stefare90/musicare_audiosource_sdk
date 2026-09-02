import sys
import os
import subprocess
import importlib
from .types import Track, Artist


def run_player(
    artist: str = "The Beatles",
    title: str = "Come Together",
    quality: str = "high",
    plugin_module_path: str = "src.main",
):
    # Ensure current working directory is in sys.path to find the local plugin
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    # 1. Load the local plugin using the standard factory
    try:
        main_mod = importlib.import_module(plugin_module_path)
        plugin = main_mod.get_plugin()
    except Exception as e:
        print(f"❌ Error loading plugin from '{plugin_module_path}': {e}")
        return

    print(f"\n🎧 [MusicAre Test Player] Testing plugin: '{plugin.name}' (v{plugin.version})")
    print(f"🔍 Resolving stream for: {artist} - {title} (Quality: {quality})...\n")

    track = Track(name=title, artists=[Artist(name=artist)], duration_ms=0)

    try:
        sources = plugin.get_stream(track, quality)
    except Exception as e:
        print(f"❌ Stream resolution failed: {e}")
        return

    if not sources:
        print("⚠️ No audio stream candidates returned by the plugin.")
        return

    print(f"✅ Found {len(sources)} candidate stream(s):\n")
    for idx, s in enumerate(sources, start=1):
        bitrate_kbps = round((s.bitrate or 0) / 1000)
        print(f"--- [Candidate #{idx}] ---")
        print(f"Codec:   {s.codec}")
        print(f"Bitrate: {s.bitrate} bps (~{bitrate_kbps} kbps)")
        print(f"Expires: {s.expires_at}")
        print(f"URL:     {s.url}\n")

    # 2. Launch media player for Candidate #1
    primary_source = sources[0]
    user_agent = (primary_source.headers or {}).get(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    )

    players = [
        ["mpv", f"--user-agent={user_agent}", primary_source.url],
        ["ffplay", "-nodisp", "-autoexit", "-user_agent", user_agent, primary_source.url],
        ["vlc", "--http-user-agent", user_agent, primary_source.url],
    ]

    for cmd in players:
        try:
            print(f"▶️ Launching playback with '{cmd[0]}' (Press Ctrl+C to stop)...")
            subprocess.run(cmd, check=True)
            return
        except FileNotFoundError:
            continue
        except KeyboardInterrupt:
            print("\n⏹ Playback stopped by user.")
            return

    print("⚠️ No local CLI player (mpv, ffplay, vlc) found on this system.")
    print("👉 You can paste the candidate URL above into VLC directly.")


def main():
    artist = sys.argv[1] if len(sys.argv) > 1 else "The Beatles"
    title = sys.argv[2] if len(sys.argv) > 2 else "Come Together"
    quality = sys.argv[3] if len(sys.argv) > 3 else "high"
    run_player(artist=artist, title=title, quality=quality)


if __name__ == '__main__':
    main()