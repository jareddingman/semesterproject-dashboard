import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np

# Set the title and file uploader
st.set_page_config(page_title='Semester Project')
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
#upload git data
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
#-------------------------------------------------
#make some measures/clean data

df = df_initial.drop(columns=["Referred By:", "Reason - Pending/No", "Sexual Orientation", "Referred By:", "Patient Letter Notified? (Directly/Indirectly through rep)", "Application Signed?", "Notes", "Payable to:"])
print(df.columns)

df = df.replace(regex=r'(M|m)issing', value="")
df = df.replace(regex=r'N/A', value = "")
print(df)
#made all Missing or missing becaome nan, 0s will be used for dummy variables like hispanic/not

df['Payment Method'] = df['Payment Method'].replace((r'((Ck|CK|ck) \d+)|((Ck|CK|ck)\d+)|ck|Ck|CK|check|Check'), value = "CK", regex = True)
df['Payment Method'] = df['Payment Method'].replace((r'Cc|cc|CC'), value = "CC", regex = True)
df['Payment Method'] = df['Payment Method'].replace((r'(PFA GC)|GC|gc|Gc'), value = "GC", regex = True)
#Payment Method cleaning, only cleaned for CK CC and GC bc these were the only described data in the description doc

df['Distance roundtrip/Tx'] = df['Distance roundtrip/Tx'].replace((r'[a-zA-Z]+'), value = "", regex = True)
#makes all distances numbers (might still need to convert to int or float)

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

df['Age'] = df['DOB'].apply(findage)
#make an Age column with ages for each recipient (in today's terms)


PendingRows = df[df['Request Status'] == "Pending"]
PendingRows = df.groupby("Paitent ID#")
GrantReq = PendingRows[['Patient ID#', 'Grant Req Date']]
#makes the rows into a df in case we need more information about the pending recipients
#GrantReq isolates the df into patient ID and when they applied for assistance

AllUsers = df['Patient ID#'].to_list()
PendingUsers = PendingRows['Patient ID#'].to_list()
FirstTenPending = PendingUsers[:10]


# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :thought_balloon: Ready to Review Applicants

'''

''
''
'''
This is an interactive table that (when pressed with the 'ready to review' button) shows the applicants that are 'pending' review. Note that graph shows the first 10 applicants needing review by default.
'''

with st.container(border = True):
    users = st.multiselect("Users", AllUsers, default=FirstTenPending)
    ReadyForReview = st.toggle("Ready for Review")
if ReadyForReview:
    df = PendingRows

tab1, = st.tabs(["Dataframe"])
with tab1:
    st.dataframe(df, height=250, use_container_width=True)

'''
To look at a specific applicant, type in the Patient ID# in the field above.
'''
