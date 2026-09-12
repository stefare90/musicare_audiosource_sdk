import sys
import os
import subprocess
import importlib
from .models import Track, AudioQuality


def run_player(
    artist: str = "The Beatles",
    title: str = "Come Together",
    quality: str = "high",
    plugin_module_path: str = "src.main",
):
    # Ensure the 'src' directory is in sys.path to simulate host runtime environment
    cwd = os.getcwd()
    src_path = os.path.join(cwd, "src")
    
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)
    elif cwd not in sys.path:
        # Fallback if run directly inside the src directory
        sys.path.insert(0, cwd)

    # 1. Load the local plugin using the standard factory
    try:
        try:
            main_mod = importlib.import_module(plugin_module_path)
        except ImportError:
            main_mod = importlib.import_module("main")
        plugin = main_mod.get_plugin()
    except Exception as e:
        print(f"❌ Error loading plugin from '{plugin_module_path}': {e}")
        return

    print(f"\n🎧 [MusicAre Test Player] Testing plugin: '{plugin.name}' (v{plugin.version})")
    print(f"🔍 Resolving stream for: {artist} - {title} (Quality: {quality})...\n")

    track = Track(name=title, artists=[artist] if artist else [], duration_ms=0)
    target_quality = AudioQuality.from_string(quality)

    try:
        candidates = plugin.search_candidates(track)
    except Exception as e:
        print(f"❌ Candidate search failed: {e}")
        return

    if not candidates:
        print("⚠️ No audio stream candidates returned by the plugin.")
        return

    print(f"✅ Found {len(candidates)} candidate(s):\n")
    for idx, c in enumerate(candidates, start=1):
        dur = f"{c.duration_ms//1000//60:02d}:{c.duration_ms//1000%60:02d}" if c.duration_ms else "--:--"
        print(f"--- [Candidate #{idx}] {c.title} (by {c.artist or 'Unknown'}) [{dur}] - ID: {c.id} ---")

    primary_candidate = candidates[0]
    print(f"\n⚡ Resolving stream for primary candidate: '{primary_candidate.title}'...")

    try:
        primary_source = plugin.resolve_stream(primary_candidate.id, target_quality)
    except Exception as e:
        print(f"❌ Stream resolution failed: {e}")
        return

    bitrate_kbps = round((primary_source.bitrate or 0) / 1000)
    print(f"Codec:   {primary_source.codec}")
    print(f"Bitrate: {primary_source.bitrate} bps (~{bitrate_kbps} kbps)")
    print(f"Expires: {primary_source.expires_at}")
    print(f"URL:     {primary_source.url}\n")

    # 2. Launch media player for Candidate #1
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
