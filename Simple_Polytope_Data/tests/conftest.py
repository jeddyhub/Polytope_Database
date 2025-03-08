import sys

def pytest_runtest_logreport(report):
    # Only print the marker after the "call" phase of a test, and for passed/failed/skipped tests.
    if report.when == 'call' and report.outcome in ('passed', 'failed', 'skipped'):
        print("[PROGRESS]")
        sys.stdout.flush()
