import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------- CONFIGURATION ----------
DATA_FILE = "data/members.xlsx"

if not os.path.exists("data"):
    os.makedirs("data")

# Initialize the Excel file if missing
if not os.path.exists(DATA_FILE):
    with pd.ExcelWriter(DATA_FILE) as writer:
        pd.DataFrame(columns=[
            'MemberID', 'Full Name', 'Initial', 'Father Name', 'City',
            'UAE Address', 'Home Address', 'Contact Number', 
            'Other Contacts', 'Email', 'Remarks'
        ]).to_excel(writer, index=False, sheet_name='Members')
        
        pd.DataFrame(columns=[
            'PaymentID', 'MemberID', 'Payment Date', 'Paid Months', 'Amount', 'Remarks'
        ]).to_excel(writer, index=False, sheet_name='Payments')

# ---------- UTILS ----------
def load_data():
    members = pd.read_excel(DATA_FILE, sheet_name='Members')
    payments = pd.read_excel(DATA_FILE, sheet_name='Payments')
    return members, payments

def save_data(members, payments):
    with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
        members.to_excel(writer, index=False, sheet_name='Members')
        payments.to_excel(writer, index=False, sheet_name='Payments')

def add_member(data):
    members, payments = load_data()
    new_id = members['MemberID'].max() + 1 if not members.empty else 1
    data['MemberID'] = new_id
    members = pd.concat([members, pd.DataFrame([data])], ignore_index=True)
    save_data(members, payments)
    return new_id

def add_payment(data):
    members, payments = load_data()
    new_id = payments['PaymentID'].max() + 1 if not payments.empty else 1
    data['PaymentID'] = new_id
    payments = pd.concat([payments, pd.DataFrame([data])], ignore_index=True)
    save_data(members, payments)

def get_member_payments(member_id):
    _, payments = load_data()
    return payments[payments['MemberID'] == member_id]

# ---------- AUTHENTICATION ----------
if not os.path.exists("config.yaml"):
    config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'email': 'admin@example.com',
                    'name': 'Admin User',
                    'password': stauth.Hasher(['admin123']).generate()[0]
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'pmj_cookie',
            'name': 'pmj_login'
        },
        'preauthorized': []
    }
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', 'main')

# ---------- MAIN APP ----------
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Logged in as {name}")

    st.title("📋 PMJ Membership Management System")
    st.caption("Excel-backed, persistent system. Works even after refresh!")

    tabs = st.tabs(["➕ Add Member", "💰 Record Payment", "📈 Dashboard", "📜 Members List"])

    # --- TAB 1: ADD MEMBER ---
    with tabs[0]:
        st.subheader("Add New Member")
        with st.form("add_member_form"):
            full_name = st.text_input("Full Name")
            initial = st.text_input("Initial")
            father_name = st.text_input("Father Name")
            city = st.selectbox("City", ["Dubai", "Sharjah", "Ajman", "Abu Dhabi", "Alain", "Northern Emirates"])
            uae_address = st.text_input("UAE Address")
            home_address = st.text_input("Home Address")
            contact_number = st.text_input("Contact Number")
            other_contacts = st.text_area("Other Relative Contacts (one per line)")
            email = st.text_input("Email")
            remarks = st.text_area("Remarks")

            submitted = st.form_submit_button("Add Member")
            if submitted:
                data = {
                    'Full Name': full_name,
                    'Initial': initial,
                    'Father Name': father_name,
                    'City': city,
                    'UAE Address': uae_address,
                    'Home Address': home_address,
                    'Contact Number': contact_number,
                    'Other Contacts': other_contacts,
                    'Email': email,
                    'Remarks': remarks
                }
                new_id = add_member(data)
                st.success(f"✅ Member added with ID: {new_id}")

    # --- TAB 2: RECORD PAYMENT ---
    with tabs[1]:
        st.subheader("Record Payment")
        members, _ = load_data()
        if members.empty:
            st.warning("No members found. Add members first!")
        else:
            member = st.selectbox("Select Member", members['Full Name'] + " - ID:" + members['MemberID'].astype(str))
            member_id = int(member.split("ID:")[1])

            with st.form("payment_form"):
                paid_months = st.text_input("Paid Months (e.g. 2025-01,2025-02)")
                amount = st.number_input("Amount (AED)", min_value=10, step=10)
                payment_date = st.date_input("Payment Date", datetime.today())
                payment_remarks = st.text_area("Remarks")

                submitted = st.form_submit_button("Record Payment")
                if submitted:
                    payment_data = {
                        'MemberID': member_id,
                        'Payment Date': payment_date,
                        'Paid Months': paid_months,
                        'Amount': amount,
                        'Remarks': payment_remarks
                    }
                    add_payment(payment_data)
                    st.success("✅ Payment recorded successfully.")

    # --- TAB 3: DASHBOARD ---
    with tabs[2]:
        st.subheader("Dashboard & Reports")
        members, payments = load_data()

        if members.empty or payments.empty:
            st.info("Add members and payments to see dashboard data.")
        else:
            st.metric("Total Members", len(members))
            st.metric("Total Payments", len(payments))
            st.metric("Total Revenue (AED)", payments['Amount'].sum())

            city_revenue = payments.merge(members[['MemberID', 'City']], on='MemberID')
            city_group = city_revenue.groupby('City')['Amount'].sum().reset_index()

            st.bar_chart(city_group, x='City', y='Amount')

            month_data = payments.copy()
            month_data['Month'] = month_data['Paid Months'].str.split(',').explode().str.strip().str[:7]
            month_group = month_data.groupby('Month')['Amount'].sum().reset_index().sort_values('Month')

            st.line_chart(month_group, x='Month', y='Amount')

    # --- TAB 4: MEMBERS LIST ---
    with tabs[3]:
        st.subheader("All Members")
        members, payments = load_data()

        if members.empty:
            st.info("No members yet.")
        else:
            df_display = members.copy()
            df_display['Total Paid'] = df_display['MemberID'].apply(
                lambda mid: payments.loc[payments['MemberID'] == mid, 'Amount'].sum()
            )
            st.dataframe(df_display, use_container_width=True)

            st.download_button("Download Members as CSV", df_display.to_csv(index=False), "members.csv")

else:
    if authentication_status is False:
        st.error("Invalid username or password")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
