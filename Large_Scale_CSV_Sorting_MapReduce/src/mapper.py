#!/usr/bin/env python3
"""Hadoop Streaming mapper: emit sortable key and original CSV row."""
import csv
import os
import sys

COLUMN = int(os.environ.get("SORT_COLUMN", "0"))
SORT_TYPE = os.environ.get("SORT_TYPE", "text").lower()

def sortable_key(value):
    value = value.strip()
    if SORT_TYPE == "number":
        # Offset signed values and encode to fixed width for lexical Hadoop sorting.
        number = float(value)
        scaled = int(round(number * 1000))
        shifted = scaled + 10**18
        if shifted < 0 or shifted >= 2 * 10**18:
            raise ValueError("Numeric value outside supported range")
        return f"{shifted:019d}"
    return value.casefold()

writer = csv.writer(sys.stdout, lineterminator="")
for raw in sys.stdin:
    raw = raw.rstrip("\n")
    try:
        row = next(csv.reader([raw]))
        if COLUMN >= len(row):
            print(f"Skipping row: column {COLUMN} missing", file=sys.stderr)
            continue
        key = sortable_key(row[COLUMN])
        # Base64-like escaping is unnecessary for tabs only if row is encoded.
        # CSV rows can contain tabs, so encode the original UTF-8 bytes as hex.
        encoded = raw.encode("utf-8").hex()
        print(f"{key}\t{encoded}")
    except Exception as exc:
        print(f"Skipping malformed row: {exc}", file=sys.stderr)
