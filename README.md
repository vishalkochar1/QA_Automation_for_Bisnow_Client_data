# Database Connection and QA Testing Guide

This guide will help you connect to the PostgreSQL database and perform QA testing on the `bn_200` table.

## 📋 Prerequisites

1. **Python 3.7+** installed on your system
2. **DBeaver** (Database GUI tool) - Download from https://dbeaver.io/
3. **Internet connection** to access the remote database

## 🚀 Quick Start

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Python Script

```bash
python database_connection.py
```

This will:
- Connect to the PostgreSQL database
- Explore the `bn_200` table structure
- Show sample data
- Perform basic QA checks

## 🗄️ Database Connection Details

- **Host**: forage-dev-db.cod4levdfbtz.ap-south-1.rds.amazonaws.com
- **Port**: 5432
- **Database**: Kapow
- **Username**: kapow
- **Password**: kapow123
- **Table**: bn_200

## 🛠️ Setting Up DBeaver

### Step 1: Download and Install DBeaver
1. Go to https://dbeaver.io/
2. Download the Community Edition
3. Install DBeaver on your system

### Step 2: Create New Connection
1. Open DBeaver
2. Click "New Database Connection" (plug icon)
3. Select "PostgreSQL" from the list
4. Fill in the connection details:
   - **Server Host**: forage-dev-db.cod4levdfbtz.ap-south-1.rds.amazonaws.com
   - **Port**: 5432
   - **Database**: Kapow
   - **Username**: kapow
   - **Password**: kapow123
5. Click "Test Connection" to verify
6. Click "Finish" to save the connection

### Step 3: Explore the Database
1. Expand the connection in the left panel
2. Navigate to: Kapow → Schemas → public → Tables
3. Find the `bn_200` table
4. Right-click and select "View Data" to see the table contents

## 🔍 QA Testing Steps

### 1. Basic Data Validation
```sql
-- Check total number of records
SELECT COUNT(*) as total_records FROM bn_200;

-- Check for duplicate records
SELECT COUNT(*) as total_records,
       COUNT(DISTINCT *) as unique_records
FROM bn_200;
```

### 2. Data Quality Checks
```sql
-- Check for null values in each column
SELECT 
    column_name,
    COUNT(*) as total_rows,
    COUNT(*) FILTER (WHERE column_value IS NULL) as null_count,
    ROUND(COUNT(*) FILTER (WHERE column_value IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
FROM (
    SELECT * FROM bn_200
) t
CROSS JOIN LATERAL (
    VALUES 
        ('column1', column1),
        ('column2', column2)
        -- Add all your columns here
) AS cols(column_name, column_value)
GROUP BY column_name;
```

### 3. Data Type Validation
```sql
-- Check data types of all columns
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'bn_200'
ORDER BY ordinal_position;
```

### 4. Sample Data Analysis
```sql
-- Get sample data for inspection
SELECT * FROM bn_200 LIMIT 10;

-- Check for any obvious data issues
SELECT DISTINCT column_name, COUNT(*) as count
FROM bn_200
GROUP BY column_name
ORDER BY count DESC;
```

## 📊 Common QA Checks

### Data Completeness
- [ ] All required columns are present
- [ ] No unexpected null values in critical columns
- [ ] Data types match expected schema

### Data Accuracy
- [ ] Values are within expected ranges
- [ ] No obvious data entry errors
- [ ] Date formats are consistent
- [ ] Numeric values are reasonable

### Data Consistency
- [ ] No duplicate records
- [ ] Referential integrity (if applicable)
- [ ] Business rules are followed

### Performance
- [ ] Queries execute within reasonable time
- [ ] No missing indexes on frequently queried columns

## 🐛 Troubleshooting

### Connection Issues
- **Error**: "Connection refused"
  - **Solution**: Check if the database server is accessible from your network
  - **Solution**: Verify firewall settings

- **Error**: "Authentication failed"
  - **Solution**: Double-check username and password
  - **Solution**: Ensure the user has proper permissions

### Query Issues
- **Error**: "Table does not exist"
  - **Solution**: Check table name spelling
  - **Solution**: Verify you're connected to the correct database

- **Error**: "Permission denied"
  - **Solution**: Check if your user has SELECT permissions on the table

## 📝 Custom Queries

You can modify the `database_connection.py` script to add your own custom queries:

```python
# Add your custom query here
custom_query = """
SELECT 
    column1,
    column2,
    COUNT(*) as count
FROM bn_200 
WHERE condition = 'value'
GROUP BY column1, column2
ORDER BY count DESC;
"""

df_custom = fetch_result(custom_query, conn)
if df_custom is not None:
    print("Custom query results:")
    print(df_custom.to_string(index=False))
```

## 🔒 Security Notes

- Never commit database credentials to version control
- Use environment variables for sensitive information in production
- Consider using connection pooling for multiple queries
- Always close database connections when done

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify your network connection
3. Ensure all dependencies are installed correctly
4. Check the database server status 

## 🚀 Quick Start

### Step 1: Install Python Dependencies

```bash
pip install pandas openpyxl xlsxwriter
```

### Step 2: Run the Python Script

```bash
python database_connection.py
```

This will:
- Connect to the PostgreSQL database
- Explore the `bn_200` table structure
- Show sample data
- Perform basic QA checks 

## 1. **Connect to the Database in Python**

You already have the connection code in `database_connection.py`.  
We'll use that connection to run the QA logic.

## 2. **Adapt the QA Steps to Work on the Database Table**

Instead of reading from a CSV, you'll:
- Use `pandas.read_sql_query()` to fetch data from the `bn_200` table.
- Run the same QA checks (Tasks 1–8) on this DataFrame.

## 3. **Step-by-Step Plan**

### **A. Fetch Data from the Database**

```python
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    database="Kapow",
    user="kapow",
    password="kapow123",
    host="forage-dev-db.cod4levdfbtz.ap-south-1.rds.amazonaws.com",
    port="5432"
)

# Fetch all data from bn_200
df = pd.read_sql_query("SELECT * FROM bn_200", conn)
```

### **B. Run the QA Checks on the DataFrame**

You can now use the same logic as in your file-based QA script, but on `df` loaded from the database.

- **Task 1:** Find `company_linkedin_url` mapped to multiple `forage_company_id`
- **Task 2:** Find cleaned `company_website` mapped to multiple `forage_company_id`
- **Tasks 3–8:** Name parsing checks (as in your script)

### **C. Output Results**

- Print results to the console.
- Optionally, write to Excel (as in your script).

## 4. **What You Need to Do**

1. **Create a new script** (e.g., `db_qa_checks.py`).
2. **Copy the connection code** and fetch the data from `bn_200`.
3. **Copy/adapt the QA logic** from your file-based script, replacing column names as needed (make sure they match the database column names, which are likely lowercase and use underscores).
4. **Run the script** and review the output.

## 5. **Example: Task 1 and Task 2 on the Database**

```python
# Task 1: Forage_Company_IDs mapped to the same Company_LinkedIn_URL
dups = df.groupby('company_linkedin_url')['forage_company_id'].nunique()
dups = dups[dups > 1]
print(dups)

# Task 2: Cleaned Company_Website mapped to multiple Forage_Company_IDs
df['cleaned_company_website'] = (
    df['company_website'].astype(str)
      .str.lower()
      .str.replace(r'^https?://(www\.)?', '', regex=True)
      .str.rstrip('/')
)
dups2 = df.groupby('cleaned_company_website')['forage_company_id'].nunique()
dups2 = dups2[dups2 > 1]
print(dups2)
```

## 6. **Summary**

- **You do NOT need to use a CSV or ZIP.**
- **You DO need to connect to the database and run the QA logic on the `bn_200` table.**
- **You can reuse almost all your QA logic, just change the data source to the database.**

## 7. **Ready-to-Use Template**

Would you like me to generate a full script (`db_qa_checks.py`) that:
- Connects to the database,
- Runs all the QA steps (Tasks 1–8) on `bn_200`,
- Outputs results to Excel?

**If yes, just say "yes" and I'll generate the code for you!**  
If you want only specific tasks, let me know which ones.

# Database QA Checks Script

## Overview
This script (`db_qa_checks_all_rows.py`) is designed to perform automated data quality (QA) checks on company and contact data stored in a PostgreSQL database. It is especially useful for identifying issues in LinkedIn URLs, company websites, and name parsing fields.

## Features
- Connects to a PostgreSQL database and fetches all relevant data in chunks.
- Runs 8 comprehensive QA checks on the data, including duplicate mappings, name parsing issues, and more.
- Outputs only the QA results (not the raw/fetched data) to an Excel file.
- Each QA result sheet includes a clear, colored description box explaining the check.
- No raw data is saved in the output file—only the QA findings.

## How It Works
1. The script connects to the specified PostgreSQL database using provided credentials.
2. It fetches all rows from the target table (e.g., `bn_200`) with the required columns.
3. It runs 8 QA checks:
   - Duplicate company LinkedIn URL mappings
   - Duplicate company website mappings
   - Name parsing issues (various checks)
4. For each QA check, a result sheet is created in the output Excel file, with a description box at the top right.
5. Only the QA result sheets are saved—no raw data sheets are included.

## How to Use
1. **Install requirements:**
   - Python 3.7+
   - `pandas`, `psycopg2`, `xlsxwriter`
   - Install with: `pip install pandas psycopg2-binary xlsxwriter`
2. **Edit the script:**
   - Update the database connection parameters at the top of the script to match your database.
   - Ensure your table has the required columns: `company_linkedin_url`, `forage_company_id`, `company_website`, `personal_linkedin_url`, `name`, `first_name`, `middle_name`, `last_name`, `designation`, `suffix`.
3. **Run the script:**
   - `python db_qa_checks_all_rows.py`
4. **Check the output:**
   - The output Excel file (`db_qa_checks_all_rows_output.xlsx`) will contain 8 sheets, one for each QA task, with a description box in each.

## Requirements
- Python 3.7 or higher
- PostgreSQL database with the required table and columns
- Python packages: pandas, psycopg2-binary, xlsxwriter

## Output Description
- The output Excel file contains only the QA results for each task (Task 1 to Task 8).
- Each sheet has a colored, merged cell at the top right with a brief description of the QA check.
- No raw/fetched data is included in the output file.

## Customization
- To use a different database or table, update the connection parameters and column names as needed.
- To add or modify QA checks, edit the relevant sections in the script.

---
For any questions or further customization, please contact the script maintainer or your data engineering team.