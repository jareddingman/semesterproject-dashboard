import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np
import plotly.express as px

#be sure to also import the requirements.txt in your terminal
#I have new appreciation for proper data descriptions

#Create a page showing how many patients did not use their full grant amount in a given application year. 
#What are the average amounts given by assistance type? This would help us in terms of budgeting and determining future programming needs.

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(page_title='Semester Project')
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
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


df_initial = loadData()
st.write(f"Loaded {len(df)} rows from {uploadedFile.name if uploadedFile else 'GitHub data folder'}.")
#-----------------------------------------------------------------------------

df = df_initial.replace(regex=r'(M|m)issing', value="")
df = df_initial.replace(regex=r'N/A', value = "")


print(df.columns)

columnNames = ['App Year', 'Patient ID#', 'Remaining Balance', 'Request Status', 'Amount', 'Type of Assistance (CLASS)']
dfGrant = df[columnNames]

index_to_drop_pending = dfGrant[dfGrant['Request Status'] == 'Pending'].index
dfGrant = dfGrant.drop(index_to_drop_pending)
index_to_drop_denied = dfGrant[dfGrant['Request Status'] == 'Denied'].index
dfGrant = dfGrant.drop(index_to_drop_denied)

dfGrant['Type of Assistance (CLASS)'] = dfGrant['Type of Assistance (CLASS)'].astype(str).str.strip()
dfGrant = dfGrant.replace(regex=r'Utilities |utilities|utilities | Utilities| utilities', value = "Utilities")
dfGrant = dfGrant.replace(regex=r'Phone/internet', value = "Phone/Internet")
dfGrant = dfGrant.replace(regex=r'Food/groceries', value = "Food/Groceries")


dfGrant["Amount"] = dfGrant["Amount"].astype(str).str.replace(r"[\$,]", "", regex = True)
dfGrant["Amount"] = pd.to_numeric(dfGrant["Amount"], errors = "coerce")

#Okay realized something abt the data. There are MULTIPLE INSTANCES of each patient taking out a transaction... So:
    #Will need to do the following:
        #Make a new column consolidating each patient ID's Amounts (which is apparently the expenses)
            #this also means I need to go back to edit the demographics page with this new column instead of the "Amount" column used :(
        #In the new df w the new column, I need to subtract (not sure if function or not):
            #Remaining Balance - sum("Amount")


amountSum = dfGrant.groupby('Patient ID#')['Amount'].sum().reset_index()
newBalance = dfGrant.groupby('Patient ID#')['Remaining Balance'].first().reset_index()
together = pd.merge(newBalance, amountSum, on = 'Patient ID#')

together['Total Balance'] = together['Remaining Balance'] - together['Amount']

together = together[['Patient ID#', 'Total Balance']]
dfGrant = pd.merge(dfGrant, together, on = 'Patient ID#', how = 'left')

#writing the app------------------------------------------------

st.title("Grant Use Metrics")
st.write("Note that these metrics are NOT perfect. For better/more accurate results, the Excel/csv needs to have consistent 'Amount' and 'Remaining Balance' columns that are properly kept track of by Patient ID#.")

'''
The metric 'Total Balance' specifically refers to the amount given to a unique Patient ID# minus the TOTAL of all 'Amount' instances by that same Patient ID#.
'''

st.subheader("Summary Statistics")
st.write(together['Total Balance'].describe())
st.subheader("Bar Chart")
barChart = px.bar(dfGrant.groupby('Type of Assistance (CLASS)')['Total Balance'].mean().reset_index(), x = 'Type of Assistance (CLASS)', y = 'Total Balance', title = 'Grant rates by CLASS(avgs)', labels = {'Type of Assistance (CLASS)': 'Type of Assistance', 'Total Balance': 'Current Balance'})
st.plotly_chart(barChart)

st.subheader("Payment Distributions")

st.markdown("### Fitler Options")
appYears = sorted(dfGrant['App Year'].dropna().unique())
selectedApp = st.multiselect("Select App Year(s):", appYears, default = appYears)

assistance = sorted(dfGrant['Type of Assistance (CLASS)'].dropna().unique())
selectedAssist = st.multiselect("Select Assistance Type(s):", assistance, default = assistance)

filteredDf = dfGrant[dfGrant['App Year'].isin(selectedApp) & dfGrant['Type of Assistance (CLASS)'].isin(selectedAssist)]



colsGraph = ['Amount', 'Total Balance', 'Remaining Balance']
selectedCols = []
for col in colsGraph:
    if st.checkbox(f"Show Distribution for: {col}"):
        selectedCols.append(col)
for col in selectedCols:
    dist = px.histogram(filteredDf, x = col, nbins = 20, histnorm = 'probability density', title = f'Distribution of {col}', marginal = 'rug')
    st.plotly_chart(dist, use_container_width = True)

st.write("TO DO for Jared: Edit Deomgraphics page in order to reflect 'together' total and not 'Amount', Finish this page and 5th page, Make sure autoflows work")
