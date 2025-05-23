import streamlit as st

st.set_page_config(
    page_title="Semester Project",
    page_icon=":leaves:")

st.title("Semester Project: Main Page :leaves:")
st.sidebar.success("Select a page above.")

'''
Welcome to my semester project for Tools for Quantitative Analysis. This app analyzes and simplifies data from the NCS HOPE foundation. 
'''
''
''
st.image("https://ncshopefoundation.org/wp-content/uploads/2023/05/footer-logo.webp")
'''
Please see the tabs located on the left of this page for:
- Ready-to-review applicants
- Donations and Demographics
- Patient application speeds
- Patient fund usage
- Executive summaries
'''
''
''
'''
IMPORTANT TO NOTE: This app uses data from an associated GitHub Repository. To see it, press the rocket emoji below:
'''
st.link_button("🚀", "https://github.com/jareddingman/semesterproject-dashboard/tree/main")
'''
This app also allows direct file uploading for easy setup. Please note that this method is more prone to errors made by spelling/data entry issues.
'''
