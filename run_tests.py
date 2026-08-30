#!/usr/bin/env python3
import os
import sys
import unittest
import time

# Ensure tests run headless
os.environ["QT_QPA_PLATFORM"] = "offscreen"

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import tempfile
from pathlib import Path
import persistence.storage as storage

# Double-guard test isolation: globally sandbox persistence storage
_GLOBAL_TEST_TMP = tempfile.TemporaryDirectory()
storage.DATA_DIR = Path(_GLOBAL_TEST_TMP.name)
storage.DATA_FILE = storage.DATA_DIR / "notes.json"

def run_suite():
    print("=" * 60)
    print(" Gnomish Note — Automated Test Suite")
    print("=" * 60)

    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("-" * 60)
    print(f" Ran {result.testsRun} tests in {elapsed:.3f}s")
    if result.wasSuccessful():
        print(f" \033[92m✔ ALL TESTS PASSED SUCCESSFULLY!\033[0m")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f" \033[91m✘ FAILURES: {len(result.failures)} | ERRORS: {len(result.errors)}\033[0m")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
