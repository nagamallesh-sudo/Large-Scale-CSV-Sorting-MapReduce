#!/usr/bin/env python3
"""Hadoop Streaming reducer: output original rows in Hadoop-sorted key order."""
import sys

for line in sys.stdin:
    line = line.rstrip("\n")
    try:
        _key, encoded = line.split("\t", 1)
        print(bytes.fromhex(encoded).decode("utf-8"))
    except Exception as exc:
        print(f"Skipping malformed mapper output: {exc}", file=sys.stderr)
