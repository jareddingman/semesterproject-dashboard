import streamlit as st
import pandas as pd
import openpyxl
from datetime import datetime
import re
import requests
import numpy as np

#be sure to also import the requirements.txt in your terminal

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(page_title='Semester Project')

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def load_original_data():
    url = 'https://raw.githubusercontent.com/jareddingman/semesterproject-dashboard/main/data/UNO%20Service%20Learning%20Data%20Sheet%20De-Identified%20Version(1).xlsx'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_excel(url, engine = "openpyxl")
    else:
        st.error("Failed to load data from GitHub.")
        return None
#-----------------------------------------------------------------------------
df_initial = load_original_data()

#my addition from positron (not template)
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

#-------------------------------------------------------------------------
#page2 goal: to collate amounts with demo info

dfDemo = df.drop(columns=["App Year", "Pt State", "Pt Zip", "DOB", "Hispanic/Latino", "Grant Req Date"])
#note to Jared: the hispanic/latino column is not clean AT ALL. some responses were "yes", "hispanic/latino", "Hispanic", etc.
index_to_drop = dfDemo[dfDemo['Request Status'] == 'Pending'].index
dfDemo = dfDemo.drop(index_to_drop)


demoOptions = ["Distance/tx", "Gender", "Race", "Income", "Insurance Type", "Age", "Marital Status", "Household Size"]
selectedDemo = st.multiselect("Group by:", demoOptions)


dfDemo["Amount"] = dfDemo["Amount"].astype(str).str.replace(r"[\$,]", "", regex = True)
dfDemo["Amount"] = pd.to_numeric(dfDemo["Amount"], errors = "coerce")


if selectedDemo:
    grouped = dfDemo.groupby(selectedDemo).agg(['count', 'mean', 'sum'])["Amount"]
    st.dataframe(data = grouped, use_container_width=True)
else:
    st.info("Please select at least one demographic.")

