import streamlit as st
import sqlite3
import pandas as pd

# Connect to your SQLite database (change name if needed)
DB_NAME = "registration_form.db3" 

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

st.set_page_config(page_title="School Registration System", layout="wide")
st.title("🏫 School Registration Form System")

st.sidebar.header("Options")
option = st.sidebar.selectbox("Choose action", ["View Students", "Add New Student", "Edit/Delete Student"])

if option == "View Students":
    st.header("All Registered Students")
    df = pd.read_sql_query("SELECT * FROM Student", conn)
    st.dataframe(df, use_container_width=True)

elif option == "Add New Student":
    st.header("Register New Student")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
            dob = st.date_input("Date of Birth *")
        with col2:
            sex = st.selectbox("Gender *", ["Male", "Female", "Other"])
            phone = st.text_input("Phone Number")
            address = st.text_area("Address")
        
        submitted = st.form_submit_button("Register Student")
        if submitted:
            if name and email and password and dob and sex:
                try:
                    cursor.execute("""
                        INSERT INTO Student (Name, Email, Password, DOB, Sex, Phone, Address)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, email, password, dob, sex, phone, address))
                    conn.commit()
                    st.success("Student registered successfully! 🎉")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill all required fields (*)")

elif option == "Edit/Delete Student":
    st.header("Manage Existing Students")
    cursor.execute("SELECT Student_ID, Name, Email FROM Student")
    students = cursor.fetchall()
    student_dict = {f"{name} ({email}) - ID: {id}": id for id, name, email in students}
    
    selected = st.selectbox("Select student to edit/delete", options=[""] + list(student_dict.keys()))
    
    if selected:
        student_id = student_dict[selected]
        cursor.execute("SELECT * FROM Student WHERE Student_ID = ?", (student_id,))
        student = cursor.fetchone()
        cols = [desc[0] for desc in cursor.description]
        data = dict(zip(cols, student))
        
        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=data["Name"])
                new_email = st.text_input("Email", value=data["Email"])
                new_password = st.text_input("Password", type="password", value=data["Password"])
                new_dob = st.date_input("Date of Birth", value=pd.to_datetime(data["DOB"]))
            with col2:
                new_sex = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(data["Sex"]))
                new_phone = st.text_input("Phone Number", value=data["Phone"] or "")
                new_address = st.text_area("Address", value=data["Address"] or "")
            
            col_update, col_delete = st.columns(2)
            update = col_update.form_submit_button("Update Student")
            delete = col_delete.form_submit_button("Delete Student")
            
            if update:
                cursor.execute("""
                    UPDATE Student SET Name=?, Email=?, Password=?, DOB=?, Sex=?, Phone=?, Address=?
                    WHERE Student_ID=?
                """, (new_name, new_email, new_password, new_dob, new_sex, new_phone, new_address, student_id))
                conn.commit()
                st.success("Student updated!")
            
            if delete:
                if st.checkbox("I confirm I want to delete this student"):
                    cursor.execute("DELETE FROM Student WHERE Student_ID=?", (student_id,))
                    conn.commit()
                    st.success("Student deleted!")
                    st.rerun()

st.sidebar.info("Database: registration_form.db")
st.sidebar.caption("Simple GUI for your school registration system")

conn.close()
