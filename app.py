import streamlit as st
import yaml
import streamlit_authenticator as stauth
import pandas as pd
from yaml.loader import SafeLoader

# -----------------------------
# Load config
# -----------------------------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# -----------------------------
# Authenticator
# -----------------------------
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', location='main')

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
elif authentication_status:

    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome *{name}*")

    st.title("PMJ Membership Manager")

    # -----------------------------
    # Load or create member data
    # -----------------------------
    try:
        members_df = pd.read_excel('members.xlsx')
    except FileNotFoundError:
        members_df = pd.DataFrame(columns=[
            'Full Name', 'Initial', 'Father Name', 'City', 'UAE Address',
            'Home Address', 'Contact Number', 'Other Relatives',
            'Email', 'Remarks'
        ])
        members_df.to_excel('members.xlsx', index=False)

    # -----------------------------
    # Sidebar - Add New Member
    # -----------------------------
    st.sidebar.header('Add New Member')
    with st.sidebar.form('Add Member'):
        full_name = st.text_input('Full Name')
        initial = st.text_input('Initial')
        father_name = st.text_input('Father Name')
        city = st.selectbox('City', [
            'Dubai', 'Sharjah', 'Ajman', 'Abu Dhabi', 'Alain', 'Northern Emirates'
        ])
        uae_address = st.text_area('UAE Address')
        home_address = st.text_area('Home Address')
        contact_number = st.text_input('Contact Number')
        other_relatives = st.text_area('Other Relatives (comma-separated)')
        email = st.text_input('Email')
        remarks = st.text_area('Remarks')
        submit = st.form_submit_button('Add Member')

        if submit:
            new_row = {
                'Full Name': full_name,
                'Initial': initial,
                'Father Name': father_name,
                'City': city,
                'UAE Address': uae_address,
                'Home Address': home_address,
                'Contact Number': contact_number,
                'Other Relatives': other_relatives,
                'Email': email,
                'Remarks': remarks
            }
            members_df = pd.concat([members_df, pd.DataFrame([new_row])], ignore_index=True)
            members_df.to_excel('members.xlsx', index=False)
            st.sidebar.success('Member added successfully!')

    # -----------------------------
    # Main - View Members
    # -----------------------------
    st.subheader('All Members')
    st.dataframe(members_df)

    # -----------------------------
    # Export
    # -----------------------------
    csv = members_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download CSV",
        csv,
        "members.csv",
        "text/csv",
        key='download-csv'
    )
