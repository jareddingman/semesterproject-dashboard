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
#make an Age column with ages for each recipient (in today's terms)


#need to list all "pending" rows in a succinct way for HOPE, filter by needing to sign board members
PendingRows = df[df['Request Status'] == "Pending"]
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

# Add some spacing
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
