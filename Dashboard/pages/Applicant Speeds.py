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
st.title("Application Response Speed")
'''
These data were pulled from 'Payment Submitted?' and 'Grant Req Date' columns in the csv/Excel file.
Only observations with dates included in BOTH these columns are analyzed.
'''

st.subheader("Histogram of Application Speed")
histogram = px.histogram(df, x = 'Response Time', nbins = 20, labels = {'Response Time': 'Response Time (days)', 'count': 'Count'}, title = "Application Speed")
st.plotly_chart(histogram)
'''
Hover over the graph with your mouse to see more information!
'''
                         

st.write("This is still under construction! :building_construction:")
