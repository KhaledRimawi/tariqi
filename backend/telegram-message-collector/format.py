# format.py
import os
import subprocess
import sys

TARGET = "."


def run(cmd):
    print(f"➤ Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    run(f"python -m black {TARGET} --line-length 120")
    run(f"python -m isort {TARGET}")
    print("✅ Formatting complete.")
