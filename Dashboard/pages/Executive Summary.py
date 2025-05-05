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












st.title("Executive Summary :briefcase:")
''
''
st.write("This summary captures some key points that may be important to NCS HOPE. At the bottom of this page, there is are data recommendations that might be useful to NCS HOPE.")

st.subheader("Recommendations")
st.write("After Handling this data to create this app, I have a few suggestions for NCS HOPE:")
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
