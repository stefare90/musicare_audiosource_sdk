import os
import sys
import json
import shutil
import subprocess
import zipfile
from typing import List


class PluginBuildError(Exception):
    """Raised when plugin packaging or compatibility audit fails."""
    pass


def validate_manifest(manifest_path: str) -> dict:
    """
    Validates the structure and mandatory fields of plugin.json.
    """
    if not os.path.exists(manifest_path):
        raise PluginBuildError(f"Missing manifest file: '{manifest_path}' not found in project root.")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise PluginBuildError(f"Invalid JSON syntax in '{manifest_path}': {e}")

    required_fields = ["id", "packageId", "type", "name", "version", "pluginSdkVersion"]
    missing = [field for field in required_fields if field not in data or not str(data[field]).strip()]
    if missing:
        raise PluginBuildError(f"Manifest '{manifest_path}' is missing mandatory fields: {missing}")

    if data.get("type") != "audioSource":
        raise PluginBuildError(
            f"Invalid plugin type '{data.get('type')}'. Expected 'audioSource' for this SDK."
        )

    return data


def audit_pure_python(directory: str) -> None:
    """
    Scans the bundle for compiled native binaries (.so, .pyd, .dylib, .dll).
    Raises PluginBuildError if non-pure dependencies are detected.
    """
    forbidden_extensions = ('.so', '.pyd', '.dylib', '.dll')
    detected_binaries: List[str] = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(forbidden_extensions):
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                detected_binaries.append(rel_path)

    if detected_binaries:
        print("\n❌ [COMPATIBILITY AUDIT FAILED] Non-portable native binaries detected:")
        for binary in detected_binaries[:10]:
            print(f"   ⛔ {binary}")
        if len(detected_binaries) > 10:
            print(f"   ... and {len(detected_binaries) - 10} more native binary files.")

        raise PluginBuildError(
            "\nMobile platforms (Android & iOS) strictly prohibit loading unsigned native C/C++ extensions at runtime.\n"
            "All dependencies in requirements.txt must be 100% Pure-Python."
        )


def clean_bytecode(directory: str) -> int:
    """
    Removes bytecode files and __pycache__ directories.
    """
    removed = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))
                removed += 1
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
                removed += 1
    return removed


def build_plugin(
    source_dir: str = "src",
    manifest_file: str = "plugin.json",
    requirements_file: str = "requirements.txt",
    output_zip: str = "plugin.zip",
) -> None:
    """
    Compiles, audits, and packages a MusicAre audio source plugin into a distribution zip.
    """
    build_dir = "build_plugin_temp"

    print("==================================================")
    print("🎵 MusicAre Audio Source Plugin Builder")
    print("==================================================")

    # 1. Validate manifest
    print("🔍 1. Validating manifest (plugin.json)...")
    manifest = validate_manifest(manifest_file)
    print(f"   ✅ Plugin: '{manifest['name']}' (v{manifest['version']}) [ID: {manifest['id']}]")

    # 2. Check source directory and main.py entry point
    print(f"🔍 2. Checking source directory ('{source_dir}/')...")
    if not os.path.exists(source_dir):
        raise PluginBuildError(f"Source directory '{source_dir}/' does not exist.")

    main_entry = os.path.join(source_dir, "main.py")
    if not os.path.exists(main_entry):
        raise PluginBuildError(f"Missing required entry point: '{main_entry}' not found.")

    with open(main_entry, "r", encoding="utf-8") as f:
        content = f.read()
        if "def get_plugin" not in content:
            raise PluginBuildError(
                f"Entry point '{main_entry}' must define a factory function 'def get_plugin() -> BaseAudioSourcePlugin:'"
            )
    print("   ✅ Entry point 'main.py' and 'get_plugin()' factory validated.")

    # 3. Clean temporary staging area
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    try:
        # 4. Install dependencies from requirements.txt
        if os.path.exists(requirements_file):
            print(f"📥 3. Installing dependencies from '{requirements_file}'...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "-r", requirements_file,
                "--target", build_dir,
                "--no-compile"
            ], check=True)
            print("   ✅ Dependencies installed successfully.")
        else:
            print("ℹ️ 3. No requirements.txt found, skipping dependency installation.")

        # 5. Copy source files into bundle root
        print("📄 4. Staging plugin sources...")
        for item in os.listdir(source_dir):
            src_path = os.path.join(source_dir, item)
            dst_path = os.path.join(build_dir, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)

        # 6. Copy manifest to bundle root
        shutil.copy(manifest_file, build_dir)
        print("   ✅ Sources and manifest staged.")

        # 7. Audit Pure-Python compliance
        print("🛡️ 5. Running Pure-Python mobile compatibility audit...")
        audit_pure_python(build_dir)
        print("   ✅ Audit passed: 100% Pure-Python dependencies detected.")

        # 8. Clean leftover bytecode
        cleaned = clean_bytecode(build_dir)
        if cleaned > 0:
            print(f"   🧹 Removed {cleaned} cache/bytecode files.")

        # 9. Create final ZIP package
        print(f"📦 6. Compressing package into '{output_zip}'...")
        total_files = 0
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(build_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, build_dir)
                    zipf.write(full_path, rel_path)
                    total_files += 1

        size_kb = os.path.getsize(output_zip) / 1024
        print("==================================================")
        print(f"🎉 Build Succeeded! '{output_zip}' ({size_kb:.2f} KB, {total_files} files)")
        print("==================================================")

    finally:
        # Cleanup temporary staging folder
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)


def main():
    try:
        build_plugin()
    except PluginBuildError as e:
        print(f"\n❌ Build Failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()