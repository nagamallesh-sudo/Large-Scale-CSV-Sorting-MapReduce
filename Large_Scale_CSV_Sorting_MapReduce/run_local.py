#!/usr/bin/env python3
"""Run the same CSV sorting logic locally for demonstration/testing."""
import argparse
import csv
from pathlib import Path

def key_for(value, kind):
    value = value.strip()
    return float(value) if kind == "number" else value.casefold()

def main():
    parser = argparse.ArgumentParser(description="Sort a CSV file by one column.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--column", type=int, default=0, help="Zero-based column index")
    parser.add_argument("--type", choices=["text", "number"], default="text")
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        rows = []
        for line_no, row in enumerate(reader, start=2):
            if args.column < 0 or args.column >= len(row):
                print(f"Skipping line {line_no}: selected column missing")
                continue
            try:
                rows.append((key_for(row[args.column], args.type), row))
            except ValueError:
                print(f"Skipping line {line_no}: value is not numeric")
    rows.sort(key=lambda item: item[0])

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header is not None:
            writer.writerow(header)
        writer.writerows(row for _, row in rows)
    print(f"Sorted {len(rows)} records. Output: {output}")

if __name__ == "__main__":
    main()
