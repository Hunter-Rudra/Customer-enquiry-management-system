import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date

from database import (
    initialize_database,
    add_lead,
    get_leads,
    update_lead,
    delete_lead
)

st.set_page_config(
    page_title="InstituteFlow CRM",
    page_icon="🎓",
    layout="wide"
)

initialize_database()

st.title("🎓 InstitueteFlow CRM")
st.caption("Student enquiry and follow-up management")


raw_leads = get_leads()

columns = [
    "ID", "Name", "Phone", "Course", "Source",
    "Status", "Follow-up", "Notes", "Created At"
]

df = pd.DataFrame(raw_leads, columns=columns)

# Slidebar navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Enquiry",
        "Manage Enquiries",
        "Reports"
    ]
)

if page == "Dashboard":
    
    st.subheader("Business Overview")
    
    total = len(df)
    
    converted = (
        df["Status"] == "Converted"
    ).sum() if total else 0
    
    
    pending = (
        df["Status"].isin(["New", "Interested", "Follow-up"])
    ).sum() if total else 0
    
    
    conversion = (
        converted / total * 100
    ) if total else 0
    
    c1, c2 , c3, c4 = st.columns(4)
    
    c1.metric("Total Enquriries", total)
    c2.metric("Admissiions", int(converted))
    c3.metric("Pending Leads", int(pending))
    c4.metric("Conversion Rate", f"{conversion:.1f}%")
    
    if total:
        status_counts = (
            df["Status"]
            .value_counts()
            .reset_index()
        )
        
        status_counts.columns = ["Status", "Count"]
        
        fig = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="Enquiry Pipeline"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Recent Enquiries")
        st.dataframe(
            df[["Name", "Course", "Status", "Follow-up"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No enquiries yet. Add your first student.")
        
elif page == "Add Enquiry":
    
    st.subheader("Register New Student Enquiry")
    
    with st.form("new_lead"):
        
        name = st.text_input("Student Name")
        phone = st.text_input("Phone Number")
        course = st.selectbox(
            "Course",
            [
                "Python",
                "Data Science",
                "Machine Learning",
                "Statistics",
                "Other"
            ]
        )
        
        source = st.selectbox(
            "Enquiry Source",
            [
                "Walk-in",
                "Website",
                "Instagram",
                "WhatsApp",
                "Referral"
            ]
        )
        
        follow_up = st.date_input(
            "Next Follow-up",
            value=date.today()
        )
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button(
            "Save Enquiry"
        )
        
        if submitted:
            
            if not name.strip() or not phone.strip():
                st.error("Name and phone are required.")
                
            elif not phone.strip().replace("+", "").replace(" ", "").isdigit():
                st.error("Enter a valid phone number.")
                
            else:
                add_lead(
                    name,
                    phone,
                    course,
                    source,
                    str(follow_up),
                    notes
                )
                
                st.success("Enquiry saved successfully!")
                st.rerun()
                
elif page == "Manage Enquiries":
    
    st.subheader("Manage Student Enquiries")
    
    if not df.empty:
        
        search = st.text_input("Search by name or phone")
        
        filtered = df[
            df["Name"].str.contains(search, case=False, na=False)
            | df["Phone"].str.contains(search, na=False)
        ]
        
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )
        
        lead_ids = filtered["ID"].tolist()
        
        if lead_ids:
            
            selected_id = st.selectbox(
                "Select enquiry ID",
                lead_ids
            )
            
            selected = df[df["ID"] == selected_id].iloc[0]
            st.write("Stored status:", repr(selected["Status"]))
            
            with st.form("update_lead"):
                
                new_status = st.selectbox(
                    "Update Status",
                    [
                        "New",
                        "Interested",
                        "Follow-up",
                        "Converted",
                        "Lost"
                    ],
                    index = [
                        "New",
                        "Interested",
                        "Follow-up",
                        "Converted",
                        "Lost"
                    ].index(selected["Status"])
                )
                
                new_date = st.date_input(
                    "Follow-up Date",
                    value=(
                        date.fromisoformat(selected["Follow-up"])
                        if pd.notna(selected["Follow-up"])
                        else date.today()
                    )
                )
                
                new_notes = st.text_area(
                    "Notes",
                    value=selected["Notes"] or ""
                )
                
                save = st.form_submit_button("Update")
                
                if save:
                    update_lead(
                        int(selected_id),
                        new_status,
                        str(new_date),
                        new_notes
                    )
                    st.success("Enquiry updated!")
                    st.rerun()
                    
            if st.button("Delete Selected Enquiry"):
                delete_lead(int(selected-id))
                st.success("Enquiry deleted.")
                st.rerun()
                
    else:
        st.info("No enquiries available.")
        
elif page == "Reports":
    
    st.subheader("Enquiry Reports")
    
    if not df.empty:
        
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="institute_leads.csv",
            mime="text/csv"
        )
        
        st.write("Enquiry records:", len(df))
        
    else:
        st.info("No data available for reports.")