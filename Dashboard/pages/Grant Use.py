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
