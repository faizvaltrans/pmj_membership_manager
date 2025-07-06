import streamlit as st
import pandas as pd
import yaml
import streamlit_authenticator as stauth
import json
import os

st.set_page_config(page_title="PMJ Membership Manager", layout="wide")

# Load config
with open('config.yaml') as file:
    config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == False:
    st.error('Username/password is incorrect')
if authentication_status == None:
    st.warning('Please enter your username and password')
if authentication_status:

    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome, {name}")

    st.title("🧾 PMJ Membership Manager")

    # Load Excel
    if os.path.exists('members.xlsx'):
        df = pd.read_excel('members.xlsx')
    else:
        df = pd.DataFrame(columns=[
            'Full Name', 'Initial', 'Father Name', 'City',
            'UAE Address', 'Home Address', 'Contact Number',
            'Other Contacts', 'Email', 'Remarks', 'Payments'
        ])
        df.to_excel('members.xlsx', index=False)

    menu = st.sidebar.radio("Menu", ['Dashboard', 'Add Member', 'Manage Payments'])

    if menu == 'Dashboard':
        st.subheader("📊 Dashboard")
        st.write(f"Total Members: {len(df)}")
        if not df.empty:
            st.dataframe(df.drop(columns=['Payments']))
            city_counts = df['City'].value_counts()
            st.bar_chart(city_counts)

    if menu == 'Add Member':
        st.subheader("➕ Add New Member")
        with st.form("add_form"):
            full_name = st.text_input("Full Name")
            initial = st.text_input("Initial")
            father_name = st.text_input("Father Name")
            city = st.selectbox("City", ['Dubai', 'Sharjah', 'Ajman', 'Abu Dhabi', 'Alain', 'Northern Emirates'])
            uae_address = st.text_area("UAE Address")
            home_address = st.text_area("Home Address")
            contact_number = st.text_input("Contact Number")
            other_contacts = st.text_area("Other Contacts (comma separated)")
            email = st.text_input("Email")
            remarks = st.text_area("Remarks")
            submitted = st.form_submit_button("Add Member")
            if submitted:
                new_data = {
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
                    'Payments': json.dumps({})
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_excel('members.xlsx', index=False)
                st.success("✅ Member added!")

    if menu == 'Manage Payments':
        st.subheader("💸 Manage Payments")
        if df.empty:
            st.info("No members found. Please add members first.")
        else:
            member_name = st.selectbox("Select Member", df['Full Name'])
            member_row = df[df['Full Name'] == member_name].iloc[0]
            st.write("**Details:**")
            st.write(member_row.drop(['Payments']))

            payments = json.loads(member_row['Payments']) if pd.notna(member_row['Payments']) else {}
            st.write("**Payment History:**")
            st.json(payments)

            st.write("✅ Mark New Payment")
            with st.form("pay_form"):
                year = st.selectbox("Year", [2025, 2026, 2027])
                month = st.selectbox("Month", [f"{i:02d}" for i in range(1, 13)])
                amount = st.number_input("Amount (AED)", 0, 500, 10)
                submit_payment = st.form_submit_button("Save Payment")
                if submit_payment:
                    key = f"{year}-{month}"
                    payments[key] = payments.get(key, 0) + amount
                    df.loc[df['Full Name'] == member_name, 'Payments'] = json.dumps(payments)
                    df.to_excel('members.xlsx', index=False)
                    st.success("✅ Payment updated!")

    # Revenue summary
    if st.sidebar.checkbox("Show Revenue Report"):
        st.subheader("📈 Revenue Report")
        total = 0
        city_totals = {}
        for idx, row in df.iterrows():
            p = json.loads(row['Payments']) if pd.notna(row['Payments']) else {}
            s = sum(p.values())
            total += s
            city = row['City']
            city_totals[city] = city_totals.get(city, 0) + s
            st.write(f"**{row['Full Name']}**: AED {s}")

        st.write("### 📌 Total Revenue: AED", total)
        st.bar_chart(pd.Series(city_totals))

