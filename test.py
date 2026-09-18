#!/usr/bin/env python
"""
Aerixis ShopNow — Automated Test Suite Runner

Usage:
    python test.py                  # Run all tests across the project
    python test.py accounts         # Run tests for accounts app
    python test.py store            # Run tests for store app
    python test.py dashboard        # Run tests for dashboard app
    python test.py accounts.tests.SecurityHardeningTest  # Run specific test case
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopnow.settings")
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)

    test_labels = sys.argv[1:] if len(sys.argv) > 1 else ["accounts", "store", "dashboard"]

    print("=" * 70)
    print("  Aerixis ShopNow — Running Test Suite")
    print(f"  Target: {', '.join(test_labels)}")
    print("=" * 70)

    failures = test_runner.run_tests(test_labels)

    if failures:
        print("\n[FAIL] Some tests failed. Please review the output above.")
        sys.exit(bool(failures))
    else:
        print("\n[OK] All test suites passed successfully.")
        sys.exit(0)


if __name__ == "__main__":
    run_tests()
