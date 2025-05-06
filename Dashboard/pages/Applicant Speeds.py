import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np
import plotly.express as px

# set the title and allows file uploading
st.set_page_config(page_title='Semester Project')
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
#connects/finds data from github

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
#clean data/get useful measures

df = df_initial.drop(columns=["Patient ID#", "App Year", "Remaining Balance", "Request Status", "Pt City", "Pt State", "Pt Zip", "Language", "DOB", "Marital Status", "Gender", "Race", "Hispanic/Latino", "Insurance Type", "Household Size", "Total Household Gross Monthly Income", "Distance roundtrip/Tx", "Type of Assistance (CLASS)",  "Amount", "Payment Method", "Reason - Pending/No", "Sexual Orientation", "Referred By:", "Patient Letter Notified? (Directly/Indirectly through rep)", "Application Signed?", "Notes", "Payable to:"])
print(df.columns)
#drop everything except for Grant Req Date, and Payment Submitted

df = df.replace(regex=r'(M|m)issing', value="")
df = df.replace(regex=r'N/A', value = "")
print(df)
#made all Missing or missing becaome nan, 0s will be used for dummy variables like hispanic/not

df['Grant Req Date'] = pd.to_datetime(df['Grant Req Date'], errors = 'coerce')
df['Payment Submitted?'] = pd.to_datetime(df['Payment Submitted?'], errors = 'coerce')
df = df.dropna(subset = ['Grant Req Date', 'Payment Submitted?'])

df['Response Time'] = (df['Payment Submitted?'] - df['Grant Req Date']).dt.days

#------------------------------------------------------------------
#draw the page

st.title("Application Response Speed")
'''
These data were pulled from 'Payment Submitted?' and 'Grant Req Date' columns in the csv/Excel file.
Only observations with dates included in BOTH these columns are analyzed.
'''
st.subheader("Summary Statistics")
st.write(df['Response Time'].describe())

st.subheader("Histogram of Application Speed")
histogram = px.histogram(df, x = 'Response Time', nbins = 20, labels = {'Response Time': 'Response Time (days)', 'count': 'Count'}, title = "Application Speed")
st.plotly_chart(histogram)
'''
Hover over the graph with your mouse to see more information!
'''
st.subheader("Box Plot of Days to Payment")
fig_box = px.box(df, x='Response Time', title='Box Plot of Days to Payment')
st.plotly_chart(fig_box)                       
st.write("Hover over this graph too to see more information!")
