import psycopg2
import pandas as pd
import re
from pandas import ExcelWriter
import xlsxwriter

# Database connection parameters
conn = psycopg2.connect(
    database="Kapow",
    user="kapow",
    password="kapow123",
    host="forage-dev-db.cod4levdfbtz.ap-south-1.rds.amazonaws.com",
    port="5432"
)

# Only fetch the required columns
columns = [
    "company_linkedin_url", "forage_company_id", "company_website",
    "personal_linkedin_url", "name", "first_name", "middle_name",
    "last_name", "designation", "suffix"
]
col_str = ', '.join(columns)

chunk_size = 50000
offset = 0
all_data = []

# Fetch all data in chunks
while True:
    query = f"SELECT {col_str} FROM bn_200 OFFSET {offset} LIMIT {chunk_size}"
    chunk = pd.read_sql_query(query, conn)
    if chunk.empty:
        break
    all_data.append(chunk)
    print(f"Loaded rows {offset} to {offset + len(chunk)}")
    offset += len(chunk)

df = pd.concat(all_data, ignore_index=True)
print(f"\n✅ Data loaded from bn_200: {len(df)} rows, {len(df.columns)} columns.")
print("Columns:", list(df.columns))

# Before saving, convert URL columns to plain text (not hyperlinks)
for col in ['company_linkedin_url', 'personal_linkedin_url', 'company_website']:
    df[col] = df[col].astype(str)
    # Remove hyperlink formatting by prepending a single quote (optional, for Excel)
    df[col] = df[col].apply(lambda x: "'" + x if not x.startswith("'") else x)

# --- QA Checks (same as original script) ---
# Task 1: Forage_Company_IDs mapped to the same Company_LinkedIn_URL
# ... existing code ...
dup1 = df.groupby('company_linkedin_url')['forage_company_id'].nunique()
dup1 = dup1[dup1 > 1]
if not dup1.empty:
    task1_records = []
    for url in dup1.index:
        ids = df.loc[df['company_linkedin_url'] == url, 'forage_company_id'].unique()
        task1_records.append({'company_linkedin_url': url, 'forage_company_ids': ', '.join(map(str, ids))})
    task1_df = pd.DataFrame(task1_records)
else:
    task1_df = pd.DataFrame(columns=['company_linkedin_url', 'forage_company_ids'])

# Task 2: Cleaned Company_Website mapped to multiple Forage_Company_IDs
df['cleaned_company_website'] = (
    df['company_website'].astype(str)
      .str.lower()
      .str.replace(r'^https?://(www\.)?', '', regex=True)
      .str.rstrip('/')
)
dup2 = df.groupby('cleaned_company_website')['forage_company_id'].nunique()
dup2 = dup2[dup2 > 1]
if not dup2.empty:
    task2_records = []
    for site in dup2.index:
        ids = df.loc[df['cleaned_company_website'] == site, 'forage_company_id'].unique()
        task2_records.append({'cleaned_company_website': site, 'forage_company_ids': ', '.join(map(str, ids))})
    task2_df = pd.DataFrame(task2_records)
else:
    task2_df = pd.DataFrame(columns=['cleaned_company_website', 'forage_company_ids'])

# --- Name Parsing QA Tasks ---
designation_list = ['CEO', 'Founder', 'Manager', 'PhD']
suffix_list = ['Jr', 'Sr', 'II', 'III']

main_cols = ['personal_linkedin_url', 'name', 'first_name', 'middle_name', 'last_name', 'designation', 'suffix']

def task_3(row):
    words = len(str(row['name']).split())
    parsed = [row[c] for c in ['first_name', 'middle_name', 'last_name', 'designation', 'suffix']]
    filled = sum(pd.notnull(x) and str(x).strip() != '' for x in parsed)
    return words > 1 and filled < 2
task3_df = df[df.apply(task_3, axis=1)].drop_duplicates(subset='personal_linkedin_url')

def task_4(row):
    if pd.isnull(row['name']) or str(row['name']).strip() == '':
        return False
    return all(pd.isnull(row[c]) or str(row[c]).strip() == '' for c in ['first_name', 'middle_name', 'last_name', 'designation', 'suffix'])
task4_df = df[df.apply(task_4, axis=1)].drop_duplicates(subset='personal_linkedin_url')

def value_not_in_name(row):
    for col in ['first_name', 'middle_name', 'last_name', 'designation', 'suffix']:
        val = str(row[col]).strip() if pd.notna(row[col]) else ''
        name = str(row['name']).strip()
        if val and val not in name:
            return True
    return False
task5_df = df[df.apply(value_not_in_name, axis=1)].drop_duplicates(subset='personal_linkedin_url')

def task_6(row):
    for c in ['first_name', 'middle_name', 'last_name']:
        val = str(row[c]).strip()
        if val in designation_list + suffix_list:
            return True
    if str(row['designation']).strip() in suffix_list or str(row['suffix']).strip() in designation_list:
        return True
    return False
task6_df = df[df.apply(task_6, axis=1)].drop_duplicates(subset='personal_linkedin_url')

def task_7(row):
    name = str(row['name'])
    nicknames = re.findall(r'\((.*?)\)|"(.*?)"|\'(.*?)\'', name)
    nicknames = [x for t in nicknames for x in t if x]
    for c in ['first_name', 'middle_name', 'last_name', 'designation', 'suffix']:
        val = str(row[c]).strip()
        if val in nicknames and val not in designation_list + suffix_list:
            return True
    return False
task7_df = df[df.apply(task_7, axis=1)].drop_duplicates(subset='personal_linkedin_url')

def task_8(row):
    if pd.isnull(row['name']) or pd.isnull(row['first_name']) or pd.isnull(row['last_name']):
        return False
    words = str(row['name']).split()
    if len(words) >= 2:
        return (row['first_name'].strip() == words[-1] and row['last_name'].strip() == words[0])
    return False
task8_df = df[df.apply(task_8, axis=1)].drop_duplicates(subset='personal_linkedin_url')

# Only keep the QA result DataFrames and their labels/descriptions
qa_dfs = [task1_df, task2_df, task3_df, task4_df, task5_df, task6_df, task7_df, task8_df]
qa_labels = [
    "Task 1 (CompanyLiUrl_Dups)",
    "Task 2 (CompanyWeb_Dups)",
    "Task 3 (Low Parse Count)",
    "Task 4 (All Parse Missing)",
    "Task 5 (Values Not in Name)",
    "Task 6 (Misplaced Titles)",
    "Task 7 (Nickname Issues)",
    "Task 8 (Name Swapped)"
]
qa_descriptions = [
    "Task 1: Shows company_linkedin_url values that are mapped to multiple forage_company_id values. Helps identify duplicate or inconsistent company LinkedIn URL mappings.",
    "Task 2: Shows cleaned company_website values that are mapped to multiple forage_company_id values. Helps identify duplicate or inconsistent company website mappings.",
    "Task 3: Rows where the name has more than one word, but fewer than two of the parsed fields (first, middle, last, designation, suffix) are filled. Indicates poor name parsing.",
    "Task 4: Rows where the name is present but all five parsed fields (first, middle, last, designation, suffix) are empty. Indicates failed name parsing.",
    "Task 5: Rows where any parsed value (first, middle, last, designation, suffix) is not present in the name string. Indicates possible parsing errors.",
    "Task 6: Rows where designation or suffix values are found in the wrong columns (e.g., in first/middle/last name). Indicates misplaced titles.",
    "Task 7: Rows where a nickname (in parentheses, quotes, etc.) appears in a parsed field where it shouldn't. Indicates nickname parsing issues.",
    "Task 8: Rows where first and last names are swapped compared to the order in the name field. Indicates swapped name parsing."
]

with pd.ExcelWriter('db_qa_checks_all_rows_output.xlsx', engine='xlsxwriter') as writer:
    for tdf, sheet_name, desc in zip(qa_dfs, qa_labels, qa_descriptions):
        # Write the DataFrame starting from row 2 (startrow=1)
        tdf.to_excel(writer, sheet_name=sheet_name, startrow=1, index=False)
        worksheet = writer.sheets[sheet_name]
        # Find the last column index
        last_col = len(tdf.columns)
        # Merge cells for description (row 0, columns last_col to last_col+3)
        worksheet.merge_range(0, last_col, 0, last_col+3, desc, writer.book.add_format({
            'bold': True, 'border': 1, 'align': 'left', 'valign': 'vcenter',
            'fg_color': '#FFF2CC', 'font_color': '#7F6000', 'text_wrap': True
        }))
        # Optionally, freeze the header row
        worksheet.freeze_panes(1, 0)
print("\n📤 Output file saved at: db_qa_checks_all_rows_output.xlsx")

# Close the database connection
conn.close() 