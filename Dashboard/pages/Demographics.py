import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np


# set the title and file upload
st.set_page_config(page_title='Semester Project')
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
#get the data
@st.cache_data
def getGiturl(owner: str, repo: str, folder: str):
    contents_api = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}"
    resp = requests.get(contents_api)
    resp.raise_for_status()
    items = resp.json()

    latest_url = None
    latest_date = None

    for item in items:
        if not item["name"].lower().endswith((".csv", ".xlsx")):
            continue
        commits_api = (
            f"https://api.github.com/repos/{owner}/{repo}"
            f"/commits?path={item['path']}&per_page=1"
        )
        cr = requests.get(commits_api)
        cr.raise_for_status()
        commits = cr.json()
        if not commits:
            continue

        commit_date = datetime.fromisoformat(commits[0]["commit"]["committer"]["date"].replace("Z", ""))
        if latest_date is None or commit_date > latest_date:
            latest_date = commit_date
            latest_url = item["download_url"]

    if latest_url is None:
        raise RuntimeError(f"No csv/xlsx found in {owner}/{repo}/{folder}")
    return latest_url

@st.cache_data
def loadData():
    if uploadedFile is not None:
        return pd.read_excel(uploadedFile) if uploadedFile.name.lower().endswith("xlsx") \
            else pd.read_csv(uploadedFile)

    owner = "jareddingman"
    repo = "semesterproject-dashboard"
    folder = "data"

    download_url = getGiturl(owner, repo, folder)
    if download_url.lower().endswith("xlsx"):
        return pd.read_excel(download_url, engine = "openpyxl")
    else:
        return pd.read_csv(download_url)


df_initial = loadData()
st.write(f"Loaded {len(df_initial)} rows from {uploadedFile.name if uploadedFile else 'GitHub data folder'}.")
#-----------------------------------------------------------------------------
#clean lots of data

df = df_initial.drop(columns=["Referred By:", "Reason - Pending/No", "Sexual Orientation", "Referred By:", "Patient Letter Notified? (Directly/Indirectly through rep)", "Application Signed?", "Notes", "Payable to:"])
print(df.columns)

df["Race"] = df["Race"].astype(str).str.strip().str.normalize('NFKC')
#this specific line was done to avoid differences that Excel makes in 'General' and 'Number' type cells

df = df.replace(regex=r'(M|m)issing', value="")
df = df.replace(regex=r'N/A', value = "")
print(df)
#made all Missing or missing becaome nan, 0s will be used for dummy variables like hispanic/not

df['Payment Method'] = df['Payment Method'].replace((r'((Ck|CK|ck) \d+)|((Ck|CK|ck)\d+)|ck|Ck|CK|check|Check'), value = "CK", regex = True)
df['Payment Method'] = df['Payment Method'].replace((r'Cc|cc|CC'), value = "CC", regex = True)
df['Payment Method'] = df['Payment Method'].replace((r'(PFA GC)|GC|gc|Gc'), value = "GC", regex = True)
#Payment Method cleaning, only cleaned for CK CC and GC bc these were the only described data in the description doc

df['Insurance Type'] = df['Insurance Type'].replace((r'Uninsurred|Unisured'), value = "Uninsured", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'Unknown'), value = "", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'MEdicare|medicare'), value = "Medicare", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'Medicaid & Medicare'), value = "Medicare & Medicaid", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'medicaid'), value = "Medicaid", regex = True)

df['Gender'] = df['Gender'].replace((r'MAle|male'), value = "Male", regex = True)

df['Marital Status'] = df['Marital Status'].replace((r'married'), value = "Married", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'single|SIngle|Single '), value = "Single", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'Seperated|separated'), value = "Separated", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'MIssing'), value = "", regex = True)

df['Language'] = df['Language'].replace((r'English '), value = "English", regex = True)
df['Language'] = df['Language'].replace((r'English, Spanish'), value = "", regex = True)
df['Language'] = df['Language'].replace((r'Karen'), value = "", regex = True)
df['Language'] = df['Language'].replace((r'somali'), value = "Somali", regex = True)

df['Race'] = df['Race'].replace((r'Whiate'), value = "White", regex = True)
df['Race'] = df['Race'].replace((r'American Indian or Alaska Native|American Indian or Alaksa Native'), value = "American Indian or Alaskan Native", regex = True)

df['Distance roundtrip/Tx'] = df['Distance roundtrip/Tx'].replace((r'[a-zA-Z]+'), value = "", regex = True)
#makes all distances numbers (might still need to convert to int or float)
#---------------------------------------------------------

df['DOB'] = df['DOB'].replace((r'[a-zA-Z]+'), value = "", regex = True)
#make sure all DOB rows are dates


def findage(birthyear):
    if pd.isna(birthyear): #just in case I missed some weird cells
        return np.nan
    if isinstance(birthyear, str):
        if birthyear.strip() == "":
            return np.nan
        try:
            borndate = datetime.strptime(birthyear, "%m/%d/%Y").date()
        except ValueError:
            return np.nan #the ValueError is useful for this
    elif isinstance(birthyear, datetime):
        borndate = birthyear.date()
    else:
        return np.nan

    today = datetime.now().date()
    return today.year - borndate.year - ((today.month, today.day) < (borndate.month, borndate.day))

def ageBrack(age):
    if age in range(0, 18):
        return "0-18"
    if age in range(19, 28):
        return "19-28"
    if age in range(29, 39):
        return "29-39"
    if age in range(40, 55):
        return "40-55"
    if age in range(56, 61):
        return "56-61"
    if age in range(62, 67):
        return "62-67"
    if age in range(68, 73):
        return "68-73"
    if age in range(74, 79):
        return "74-79"
    if age in range(80, 85):
        return "80-85"
    if age in range(86, 150):
        return "86+"
def txBrack(dist):
    if dist in range (0, 10):
        return "0-10"
    if dist in range (11, 25):
        return "11-25"
    if dist in range (26, 50):
        return "26-50"
    if dist in range (51, 1000):
        return "51+"


df['Age'] = df['DOB'].apply(findage)
df['Age Bracket'] = df['Age'].apply(ageBrack)
df['Distance'] = df['Distance roundtrip/Tx'].apply(txBrack)

#-------------------------------------------------------------------------
#draw the page
'''
# Demographic Information
'''
''
''
'''
Below is a dataframe tool which separates amounts that have been donated by NCS HOPE by various demographic factors. There are a few things to note:
'''
'''
- The "Count" column is the raw number of observations for a given metric.
'''
'''
- The "Total" and "Average" columns are with respect to amounts donated.
'''
#make new df with wanted demographics--------------

dfDemo = df.drop(columns=["Age", "App Year", "Pt State", "Pt Zip", "DOB", "Hispanic/Latino", "Grant Req Date"])
#note to Jared: the hispanic/latino column is not clean AT ALL. some responses were "yes", "hispanic/latino", "Hispanic", etc.
index_to_drop = dfDemo[dfDemo['Request Status'] == 'Pending'].index
dfDemo = dfDemo.drop(index_to_drop)


demoOptions = ["Distance", "Gender", "Race", "Insurance Type", "Age Bracket", "Marital Status", "Household Size", "Language"]
selectedDemo = st.multiselect("Group by:", demoOptions)


dfDemo["Amount"] = dfDemo["Amount"].astype(str).str.replace(r"[\$,]", "", regex = True)
dfDemo["Amount"] = pd.to_numeric(dfDemo["Amount"], errors = "coerce")
#------------------------------------------------------

if selectedDemo:
    result_rows = []
    for groupVals, groupDf in dfDemo.groupby(selectedDemo):
        if not isinstance(groupVals, tuple):
            groupVals = (groupVals,)
        count = np.count_nonzero(~np.isnan(groupDf["Amount"]))
        sum = np.sum(groupDf["Amount"])
        mean = np.mean(groupDf["Amount"])
        result_rows.append(groupVals + (count, sum, mean))
    result_columns = selectedDemo + ["Count", "Total", "Average"]
    result_df = pd.DataFrame(result_rows, columns = result_columns)
    st.dataframe(data = result_df, use_container_width=True)
else:
    st.info("Please select at least one demographic.")

