import streamlit as st

st.title("Executive Summary :breifcase:")
''
''
st.write("This summary captures some key points that may be important to NCS HOPE. At the bottom of this page, there is are data recommendations that might be useful to NCS HOPE.")
st.subheading("Recommendations")
st.write("After Handling this data to create this app, I have a few suggestions for NCS HOPE:")
''
''
'''
Create a fixed-choice format for entering data. 
- Many of the recorded instances had to be thrown out or manually changed (not all spelling errors were fixed).
- For example, this app makes any "Missing", "missing", "MIssing" into a blank space. By having a fixed-choice format, NCS HOPE would not have to rely on the robustness of this code.
- This would also help with the 'Request Status' column which shows Approved/Pending/Denied AND dates
Refine column descriptions.
- More accurately describing each column and HOW data is entered would be extremely useful to those analyzing data.
Separate monetary information into a separate file.
- The file given to us had multiple instances of 'Remaining Balance' for the same Patient ID number. In these multiple instances, the "Amount" tab had varying expenses used. Making these transactions in a separate (probably accounting) document would help give more accurate answers in data analysis.
'''
