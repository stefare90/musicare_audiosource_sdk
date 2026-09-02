import os
import shutil
import subprocess
import sys
import zipfile


def sanitize_pure_python(directory: str) -> int:
    removed_count = 0
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            if file.endswith(('.so', '.pyd', '.dylib', '.dll', '.pyc')):
                os.remove(os.path.join(root, file))
                removed_count += 1
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))
                removed_count += 1
    return removed_count


def build_plugin(
    source_dir: str = "src",
    manifest_file: str = "plugin.json",
    requirements_file: str = "requirements.txt",
    output_zip: str = "plugin.zip",
):
    build_dir = "build_plugin_temp"

    print(f"🚀 Building distribution package: {output_zip}...")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # 1. Install runtime dependencies
    if os.path.exists(requirements_file):
        print("📥 Installing runtime dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", requirements_file,
            "--target", build_dir,
            "--no-compile"
        ], check=True)

    # 2. Copy source files to root of the bundle
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' not found!")

    print("📄 Copying plugin sources...")
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(build_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    # 3. Copy manifest
    if not os.path.exists(manifest_file):
        raise FileNotFoundError(f"Manifest '{manifest_file}' not found in project root!")
    shutil.copy(manifest_file, build_dir)

    # 4. Clean binaries
    print("🧹 Sanitizing binary files...")
    cleaned = sanitize_pure_python(build_dir)
    print(f"✨ Cleaned {cleaned} non-portable binary and cache files.")

    # 5. Create ZIP
    print(f"📦 Compressing into {output_zip}...")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, build_dir)
                zipf.write(full_path, rel_path)

    shutil.rmtree(build_dir)
    size_kb = os.path.getsize(output_zip) / 1024
    print(f"✅ Success! Generated {output_zip} ({size_kb:.2f} KB)")


if __name__ == '__main__':
    build_plugin()