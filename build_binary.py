#!/usr/bin/env python3
"""
Build script to compile Gnomish Note into a standalone Linux binary using PyInstaller.
"""
import os
import sys
import shutil
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("============================================================")
    print(" Gnomish Note — Standalone Linux Binary Builder")
    print("============================================================")
    
    # Locate or create PyInstaller environment
    pyinstaller_bin = shutil.which("pyinstaller")
    venv_pyinstaller = os.path.join(ROOT_DIR, ".build-venv", "bin", "pyinstaller")
    
    # Verify if system pyinstaller works (it might be broken or wrong python version)
    system_pyinstaller_works = False
    if pyinstaller_bin:
        try:
            res = subprocess.run([pyinstaller_bin, "--version"], capture_output=True, text=True)
            if res.returncode == 0:
                system_pyinstaller_works = True
        except Exception:
            pass

    if os.path.exists(venv_pyinstaller):
        pyinstaller_bin = venv_pyinstaller
    elif not system_pyinstaller_works:
        print("Configuring build virtualenv with PyInstaller...")
        venv_dir = os.path.join(ROOT_DIR, ".build-venv")
        subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", venv_dir], check=True)
        pip_bin = os.path.join(venv_dir, "bin", "pip")
        subprocess.run([pip_bin, "install", "pyinstaller"], check=True)
        pyinstaller_bin = os.path.join(venv_dir, "bin", "pyinstaller")

    spec_file = os.path.join(ROOT_DIR, "gnomish-note.spec")
    if os.path.exists(spec_file):
        cmd = [pyinstaller_bin, "--clean", "--noconfirm", spec_file]
    else:
        cmd = [
            pyinstaller_bin,
            "--name", "gnomish-note",
            "--onefile",
            "--windowed",
            "--paths", "src",
            "--add-data", "icons:icons",
            "--clean",
            "--noconfirm",
            "main.py"
        ]
    
    print(f"Compiling binary via PyInstaller...")
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)
    
    dist_bin = os.path.join(ROOT_DIR, "dist", "gnomish-note")
    if os.path.exists(dist_bin):
        size_mb = os.path.getsize(dist_bin) / (1024 * 1024)
        print("============================================================")
        print(f" ✔ Standalone binary ready: {dist_bin} ({size_mb:.1f} MB)")
        print(" Run it directly with: ./dist/gnomish-note")
        print("============================================================")

if __name__ == "__main__":
    build()
