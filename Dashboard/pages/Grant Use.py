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

df = df_initial.replace(regex=r'(M|m)issing', value="")
df = df_initial.replace(regex=r'N/A', value = "")

print(df.columns)

columnNames = ['Patient ID#', 'Remaining Balance', 'Request Status', 'Amount', 'Type of Assistance (CLASS)']
dfGrant = df[columnNames]

index_to_drop_pending = dfGrant[dfGrant['Request Status'] == 'Pending'].index
dfGrant = dfGrant.drop(index_to_drop_pending)
index_to_drop_denied = dfGrant[dfGrant['Request Status'] == 'Denied'].index
dfGrant = dfGrant.drop(index_to_drop_denied)

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

st.subheader("Summary Statistics")
st.write(together['Total Balance'].describe())

st.subheader("Bar Chart")
barChart = px.bar(dfGrant.groupby('Type of Assistance (CLASS)')['Total Balance'].mean().reset_index(), x = 'Type of Assistance (CLASS)', y = 'Total Balance', title = 'Grant rates by CLASS', labels = {'Type of Assistance (CLASS)': 'Type of Assistance', 'Total Balance': 'Current Balance'})
st.plotly_chart('barChart')

st.subheader("Line Chart")
st.write("TO DO for Jared: Edit Deomgraphics page in order to reflect 'together' total and not 'Amount', Finish this page and 5th page, Make sure autoflows work")
