import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def main():
    print("Building MyChatBot application for Linux...")

    app_name = "MyChatBot"
    entry_point = "main.py"
    output_dir = "build/linux"
    dist_path = os.path.join(output_dir, "dist")
    work_path = os.path.join(output_dir, "build")

    data_files = [
        ("backend/*", "backend"),
        (".env", "."),
        ("frontend/components/*", "frontend/components"),
        ("frontend/controllers/*", "frontend/controllers"),
        ("frontend/views/*", "frontend/views")
    ]

    hidden_imports = [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "markdown",
        "mistralai",
        "python-dotenv",
        "sqlite3"
    ]

    excluded_modules = [
        "PySide6.QtNetwork",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngine",
        "PySide6.QtWebEngineWidgets"
    ]

    # Clean previous build dirs
    if os.path.exists(output_dir):
        print(f"Cleaning previous build directory {output_dir}...")
        shutil.rmtree(output_dir)

    env = os.environ.copy()
    env['PYTHONOPTIMIZE'] = '1'

    separator = ":"
    icon = None  # no icon for Linux here, or add path if available

    cmd = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--onedir",  # Linux onedir
        f"--name={app_name}",
        f"--distpath={dist_path}",
        f"--workpath={work_path}",
        "--strip",
    ]

    if icon:
        cmd.append(f"--icon={icon}")

    # Add data files
    for src, dest in data_files:
        if "*" in src:
            base_dir = src.split("*")[0]
            for file in Path(base_dir).glob("*"):
                if file.is_file():
                    cmd.append(f"--add-data={file}{separator}{dest}")
        else:
            cmd.append(f"--add-data={src}{separator}{dest}")

    # Add hidden imports
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")

    # Add excluded modules
    for mod in excluded_modules:
        cmd.append(f"--exclude-module={mod}")

    cmd.append(entry_point)

    cmd = [arg for arg in cmd if arg]

    print("Running PyInstaller with command:", ' '.join(cmd))

    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        print("\nBuild completed successfully!")
        print(f"Executable can be found in: {os.path.abspath(dist_path)}")

        print("\nFor Linux:")
        print("Consider creating a .deb or .rpm package for distribution")
        return 0
    else:
        print("\nBuild failed with error code:", result.returncode)
        return 1

if __name__ == "__main__":
    sys.exit(main())
