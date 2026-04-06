#!/usr/bin/env python3
"""Sample test script for 鸣镝"""

import time
import sys

print("Script started...")
sys.stdout.flush()

for i in range(5):
    print(f"Progress: {i+1}/5")
    sys.stdout.flush()
    time.sleep(1)

print("Script completed successfully!")
sys.stdout.flush()
