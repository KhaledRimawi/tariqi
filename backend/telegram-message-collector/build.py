# build.py
import os
import subprocess
import sys

TARGET = "."


def run(cmd):
    print(f"➤ Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    run(f"python -m flake8 {TARGET}")
    run(f"python -m compileall {TARGET}")
    print("✅ Build checks passed.")
