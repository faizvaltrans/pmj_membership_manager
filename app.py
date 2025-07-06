import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import yaml
import os

# --- Load config.yaml ---
with open('config.yaml') as file:
    config = yaml.safe_load(file)

# --- Authenticator ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# --- Login Widget (FIX: use keyword) ---
name, authentication_status, username = authenticator.login('Login', location='main')

if authentication_status == False:
    st.error('Username/password is incorrect')

if authentication_status == None:
    st.warning('Please enter your username and password')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f'Welcome {name}!')

    st.title('PMJ Membership Manager')

    # --- Load or create Excel ---
    if not os.path.exists('members.xlsx'):
        df = pd.DataFrame(columns=[
            'ID', 'Full Name', 'Initial', 'Father Name', 'City',
            'UAE Address', 'Home Address', 'Contact Number',
            'Other Contacts', 'Email', 'Remarks', 'Payment History'
        ])
        df.to_excel('members.xlsx', index=False)
    else:
        df = pd.read_excel('members.xlsx')

    # --- Sidebar: Add New Member ---
    st.sidebar.header('Add New Member')
    with st.sidebar.form('new_member_form'):
        full_name = st.text_input('Full Name')
        initial = st.text_input('Initial')
        father_name = st.text_input('Father Name')
        city = st.selectbox('City', ['Dubai', 'Sharjah', 'Ajman', 'Abu Dhabi', 'Alain', 'Northern Emirates'])
        uae_address = st.text_input('UAE Address')
        home_address = st.text_input('Home Address')
        contact_number = st.text_input('Contact Number')
        other_contacts = st.text_area('Other Relative Contacts')
        email = st.text_input('Email')
        remarks = st.text_area('Remarks')
        submitted = st.form_submit_button('Add Member')

        if submitted and full_name:
            new_id = 1 if df.empty else df['ID'].max() + 1
            new_row = {
                'ID': new_id,
                'Full Name': full_name,
                'Initial': initial,
                'Father Name': father_name,
                'City': city,
                'UAE Address': uae_address,
                'Home Address': home_address,
                'Contact Number': contact_number,
                'Other Contacts': other_contacts,
                'Email': email,
                'Remarks': remarks,
                'Payment History': ''
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel('members.xlsx', index=False)
            st.sidebar.success(f'Member {full_name} added!')

    # --- Main Dashboard ---
    st.header('All Members')
    st.dataframe(df)

    # --- Export Option ---
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download members as CSV",
        data=csv,
        file_name='members.csv',
        mime='text/csv'
    )
