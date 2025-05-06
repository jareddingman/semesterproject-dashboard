import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np
import plotly.express as px

#be sure to also import the requirements.txt in your terminal

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(page_title='Semester Project')
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
#gotta finally connect the data folder to analysis
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


df = loadData()
loadSource = uploadedFile.name if uploadedFile and uploadedFile.name else 'Github data folder'
st.write(f"Loaded {len(df)} rows from {loadSource}.")

#st.write(f"Loaded {len(df)} rows from {uploadedFile.name if uploadedFile else 'GitHub data folder'}.")


df = df.replace(regex=r'(M|m)issing', value="")
df = df.replace(regex=r'N/A', value = "")

st.title("Executive Summary :briefcase:")
''
''
st.write("This summary captures some key points that may be important to NCS HOPE. At the bottom of this page, there is are data recommendations that might be useful to NCS HOPE.")

#Thinking we say how many applicants we have had, and how many we have fulfilled
    #say that this is growing, which is exciting
    #but also we need better data as it grows

uniquePats = df.drop_duplicates(subset = "Patient ID#")
uniCount = (uniquePats['Request Status'].str.strip().str.lower() == 'approved').sum()

uniquePats["Amount"] = pd.to_numeric(uniquePats["Amount"], errors = "coerce")
uniquePats["Remaining Balance"] = pd.to_numeric(uniquePats["Remaining Balance"], errors = "coerce")

avgGrant = (uniquePats['Remaining Balance'].mean())
avgExpense = (uniquePats['Amount'].mean())
            
avgGrant = round(avgGrant, 2)
avgExpense = round(avgExpense, 2)


#average grant, average expense, patients helped

col1, col2, col3 = st.columns(3)
col1.metric("Temperature", avgGrant, "1.2 °F")
col2.metric("Wind", avgExpense, "-8%")
col3.metric("Patients Helped", uniCount)

st.subheader("Patient Request Growth")

#note that this will be for unique req dates, not unique patients

fig = px.histogram(df, x="Grant Req Date")
fig.update_layout(bargap=0.2)
st.plotly_chart(fig)
st.write("Note that this is technically counting the number of patient requests, not new patients.")

st.subheader("Recommendations")
st.write("After Handling these data to create this app, I have a few suggestions for NCS HOPE:")
''
''
'''
Create a fixed-choice format for entering data. 
- Many of the recorded instances had to be thrown out or manually changed (not all spelling errors were fixed).
- For example, this app makes any "Missing", "missing", "MIssing" into a blank space. By having a fixed-choice format, NCS HOPE would not have to rely on the robustness of this code.
- This would also help with the 'Request Status' column which shows Approved/Pending/Denied AND dates
'''
'''
Refine column descriptions.
- More accurately describing each column and HOW data is entered would be extremely useful to those analyzing data.
'''
'''
Separate monetary information into a separate file.
- The file given to us had multiple instances of 'Remaining Balance' for the same Patient ID number. In these multiple instances, the "Amount" tab had varying expenses used. Making these transactions in a separate (probably accounting) document would help give more accurate answers in data analysis.
'''
