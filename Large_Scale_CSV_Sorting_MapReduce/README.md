# Large-Scale CSV Sorting using MapReduce

A Hadoop MapReduce project that sorts a large CSV file by a selected column using **Hadoop Streaming + Python**. The mapper extracts the sort key, Hadoop performs the distributed shuffle/sort, and the reducer writes the sorted CSV rows.

## Features
- Sort CSV rows by any zero-based column index
- Supports text (lexicographic) and numeric sorting
- Preserves the CSV header at the top
- Includes a small sample dataset and a local test mode
- Designed for Hadoop Streaming on a Hadoop installation

## Project structure
```text
Large_Scale_CSV_Sorting_MapReduce/
├── src/
│   ├── mapper.py
│   └── reducer.py
├── data/
│   └── employees.csv
├── output/                 # created when you run the project
├── run_local.py
├── run_hadoop.sh
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements
- Python 3.8+
- For distributed execution: Hadoop 3.x and the Hadoop Streaming JAR
- No third-party Python packages are required

## 1. Run locally (no Hadoop required)
From the project root:

```bash
python run_local.py --input data/employees.csv --output output/sorted_employees.csv --column 2 --type text
```

For numeric sorting (for example, salary or age):

```bash
python run_local.py --input data/employees.csv --output output/sorted_by_salary.csv --column 3 --type number
```

`--column` is a zero-based column index: 0 = first column, 1 = second column, etc. The first CSV row is treated as the header and is not sorted.

## 2. Run on Hadoop (distributed MapReduce)
Ensure Hadoop is configured and running, and locate your Hadoop Streaming JAR. Then:

```bash
chmod +x run_hadoop.sh
./run_hadoop.sh data/employees.csv /user/$USER/csv-sort-input /user/$USER/csv-sort-output 2 text /path/to/hadoop-streaming.jar
```

Arguments:
1. Local input CSV path
2. HDFS input directory
3. HDFS output directory (must not already exist)
4. Sort column index (zero-based)
5. Sort type: `text` or `number`
6. Path to Hadoop Streaming JAR

The script saves the header separately, uploads only data rows to HDFS, runs the MapReduce job, downloads the sorted part file, and restores the header.

### Important notes
- Hadoop's default key sort is lexicographic. Numeric mode converts numeric values to a fixed-width sortable key, so values such as 2, 10, and 100 sort numerically.
- Rows with a missing selected column are skipped and reported to stderr.
- CSV values containing commas inside quoted fields are supported by Python's CSV parser.
- For very large datasets, use HDFS input and allow Hadoop to distribute the mapper/reducer work across the cluster.
- The included sample is small for demonstration; replace it with your own large CSV file.

## How it works
1. **Input:** CSV records are read from HDFS.
2. **Mapper:** Parses each CSV row and emits `sort_key<TAB>original_row`.
3. **Shuffle and sort:** Hadoop groups and sorts mapper output by key across the cluster.
4. **Reducer:** Receives sorted records and writes the original CSV rows.
5. **Output:** Sorted CSV file, with the original header restored.

## Example
Input sorted by Salary (column index 3):
```csv
EmployeeID,Name,Department,Salary
104,Meena,HR,28000
102,Ravi,IT,45000
101,Anu,IT,52000
103,Kiran,Sales,61000
```

## GitHub upload
1. Extract this ZIP file.
2. Open the extracted project folder in VS Code.
3. Open Terminal in that folder and run:
   ```bash
   git init
   git add .
   git commit -m "Add CSV sorting MapReduce project"
   ```
4. Create an empty repository on GitHub.
5. Connect and push (replace the URL with your repository URL):
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/Large-Scale-CSV-Sorting-MapReduce.git
   git push -u origin main
   ```

Do not upload Hadoop output folders, virtual environments, or private credentials.
