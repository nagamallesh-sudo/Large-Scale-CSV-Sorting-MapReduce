#!/usr/bin/env bash
# Usage: ./run_hadoop.sh LOCAL_CSV HDFS_INPUT HDFS_OUTPUT COLUMN text|number STREAMING_JAR
set -euo pipefail

if [ "$#" -ne 6 ]; then
  echo "Usage: $0 LOCAL_CSV HDFS_INPUT HDFS_OUTPUT COLUMN text|number STREAMING_JAR" >&2
  exit 1
fi

LOCAL_CSV="$1"
HDFS_INPUT="$2"
HDFS_OUTPUT="$3"
COLUMN="$4"
SORT_TYPE="$5"
STREAMING_JAR="$6"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

if [ ! -f "$LOCAL_CSV" ]; then echo "Input CSV not found: $LOCAL_CSV" >&2; exit 1; fi
if [ ! -f "$STREAMING_JAR" ]; then echo "Streaming JAR not found: $STREAMING_JAR" >&2; exit 1; fi

# Keep header locally and stage data rows separately.
python3 - "$LOCAL_CSV" "$WORK_DIR/data.csv" "$WORK_DIR/header.txt" <<'PY'
import csv, sys
source, data_path, header_path = sys.argv[1:]
with open(source, newline="", encoding="utf-8-sig") as src:
    reader = csv.reader(src)
    header = next(reader, [])
    with open(header_path, "w", encoding="utf-8") as h:
        h.write(",".join(header) + "\n")
    with open(data_path, "w", encoding="utf-8", newline="") as out:
        for row in reader:
            out.write(",".join(row) + "\n")
PY

hdfs dfs -rm -r -f "$HDFS_INPUT" "$HDFS_OUTPUT" >/dev/null 2>&1 || true
hdfs dfs -mkdir -p "$HDFS_INPUT"
hdfs dfs -put "$WORK_DIR/data.csv" "$HDFS_INPUT/data.csv"

hadoop jar "$STREAMING_JAR" \
  -D mapreduce.job.reduces=1 \
  -files src/mapper.py,src/reducer.py \
  -cmdenv SORT_COLUMN="$COLUMN" \
  -cmdenv SORT_TYPE="$SORT_TYPE" \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input "$HDFS_INPUT" \
  -output "$HDFS_OUTPUT"

mkdir -p output
hdfs dfs -getmerge "$HDFS_OUTPUT" "$WORK_DIR/sorted.csv"
cat "$WORK_DIR/header.txt" "$WORK_DIR/sorted.csv" > output/sorted.csv
echo "Completed. Sorted CSV: output/sorted.csv"
