#!/usr/bin/env python3
"""
Tap Ball Game APK Builder
Automated script to build Android APK
"""

import subprocess
import sys
import os

def run_cmd(command):
    try:
        print(f"▶️ {command}")
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Command failed")
        return False

def main():
    print("🤖 TAP BALL GAME - APK BUILDER")
    print("="*40)

    # Check files
    required_files = ['main.py', 'buildozer.spec']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Missing: {file}")
            return
        print(f"✅ Found: {file}")

    # Install dependencies
    print("\n📦 Installing dependencies...")
    deps = ["pip install buildozer", "pip install kivy", "pip install cython"]
    for dep in deps:
        run_cmd(dep)

    # Build APK
    print("\n🏗️ Building APK...")
    if run_cmd("buildozer android debug"):
        print("\n🎉 APK BUILD SUCCESS!")
        print("📱 Check bin/ folder for your APK file")
    else:
        print("\n❌ Build failed - check errors above")

if __name__ == "__main__":
    main()
