#!/usr/bin/env python3
"""Delete all test uploads in this impl folder. Run after every test run.
Retention default: test photos live only here, deleted after the test run."""
import os, shutil, sys
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
if os.path.isdir(d):
    for name in os.listdir(d):
        shutil.rmtree(os.path.join(d, name), ignore_errors=True)
print("test uploads deleted")
