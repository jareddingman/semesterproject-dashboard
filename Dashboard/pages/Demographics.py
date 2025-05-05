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
uploadedFile = st.file_uploader("Choose file here:", type = ["csv", "xlsx"])
# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def load_original_data():
    if uploadedFile == None:
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

#Page2---------------------------------------------------
df['Insurance Type'] = df['Insurance Type'].replace((r'Uninsurred|Unisured'), value = "Uninsured", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'Unknown'), value = "", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'MEdicare|medicare'), value = "Medicare", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'Medicaid & Medicare'), value = "Medicare & Medicaid", regex = True)
df['Insurance Type'] = df['Insurance Type'].replace((r'medicaid'), value = "Medicaid", regex = True)

df['Gender'] = df['Gender'].replace((r'MAle|male'), value = "Male", regex = True)

df['Marital Status'] = df['Marital Status'].replace((r'married'), value = "Married", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'single|SIngle'), value = "Single", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'Seperated|separated'), value = "Separated", regex = True)
df['Marital Status'] = df['Marital Status'].replace((r'MIssing'), value = "", regex = True)

df['Language'] = df['Language'].replace((r'English '), value = "English", regex = True)
df['Language'] = df['Language'].replace((r'English, Spanish'), value = "", regex = True)
df['Language'] = df['Language'].replace((r'Karen'), value = "", regex = True)
df['Language'] = df['Language'].replace((r'somali'), value = "Somali", regex = True)



#---------------------------------------------------------

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
#page2 goal: to collate amounts with demo info
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
dfDemo = df.drop(columns=["Age", "App Year", "Pt State", "Pt Zip", "DOB", "Hispanic/Latino", "Grant Req Date"])
#note to Jared: the hispanic/latino column is not clean AT ALL. some responses were "yes", "hispanic/latino", "Hispanic", etc.
index_to_drop = dfDemo[dfDemo['Request Status'] == 'Pending'].index
dfDemo = dfDemo.drop(index_to_drop)


demoOptions = ["Distance", "Gender", "Race", "Insurance Type", "Age Bracket", "Marital Status", "Household Size", "Language"]
selectedDemo = st.multiselect("Group by:", demoOptions)


dfDemo["Amount"] = dfDemo["Amount"].astype(str).str.replace(r"[\$,]", "", regex = True)
dfDemo["Amount"] = pd.to_numeric(dfDemo["Amount"], errors = "coerce")


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

