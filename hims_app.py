import streamlit as st
import database as db
from patient import Patient
from department import Department
from doctor import Doctor
from prescription import Prescription
from medical_test import Medical_Test
import config
import sqlite3 as sql

# Authentication Functions
def authenticate(password, access_code=None):
    """Authenticates the user based on password and optional access code."""
    if password == config.password:
        st.sidebar.success("Password Verified")
        return True
    else:
        st.sidebar.error("Invalid Password")
        return False

def authenticate_edit_mode():
    """Authenticates for edit mode."""
    edit_mode_password = st.sidebar.text_input("Edit Mode Password", type="password")
    if edit_mode_password == config.edit_mode_password:
        st.sidebar.success("Edit Mode Verified")
        return True
    elif edit_mode_password:  # Only show error if something was entered
        st.sidebar.error("Invalid Edit Mode Password")
    return False

def authenticate_dr_mls():
    """Authenticates for doctor/MLS access."""
    access_code = st.sidebar.text_input("Dr/MLS Access Code", type="password")
    if access_code == config.dr_mls_access_code:
        st.sidebar.success("Dr/MLS Access Verified")
        return True
    elif access_code:  # Only show error if something was entered
        st.sidebar.error("Invalid Dr/MLS Access Code")
    return False


# Module Functions
def module_operations(module_name, option_list, module_object, access_check=None):
    """Handles common operations for modules (Patient, Doctor, Department, etc.)."""
    st.header(module_name.upper())  # Use module name for header
    option = st.sidebar.selectbox("Select Function", option_list)

    if option and option_list.index(option) <= 3 and access_check and not access_check(): # Check edit mode
        st.warning("Edit mode requires authentication.") #warn and exit before executing any function if edit authentication fails
        return

    if option == option_list[1]: # Add
        st.subheader(f"Add {module_name}")
        module_object.add_record() #use add_record for more generic names in module object
    elif option == option_list[2]: # Update
        st.subheader(f"Update {module_name}")
        module_object.update_record()
    elif option == option_list[3]: # Delete
        st.subheader(f"Delete {module_name}")
        try:
            module_object.delete_record()
        except sql.IntegrityError:  # Handle foreign key constraint failure
            st.error("This entry cannot be deleted as other records are using it.")
    elif option == option_list[4]: # Show All
        st.subheader(f"Complete {module_name} Record")
        module_object.show_all_records()
    elif option == option_list[5] and len(option_list) > 5: # Search (check list length to avoid errors)
        st.subheader(f"Search {module_name}")
        module_object.search_record()
    elif option == option_list[6] and len(option_list) > 6: # Additional Functionality (e.g., list doctors in department)
        st.subheader(option.upper())
        module_object.additional_functionality()

#Simplified calls for each class
def patients():
    patient_option_list = ["", "Add patient", "Update patient", "Delete patient", "Show complete patient record", "Search patient"]
    p = Patient()
    module_operations("Patient", patient_option_list, p, access_check = authenticate_edit_mode)

def doctors():
    doctor_option_list = ["", "Add doctor", "Update doctor", "Delete doctor", "Show complete doctor record", "Search doctor"]
    dr = Doctor()
    module_operations("Doctor", doctor_option_list, dr, access_check = authenticate_edit_mode)

def prescriptions():
    prescription_option_list = ["", "Add prescription", "Update prescription", "Delete prescription", "Show prescriptions of a particular patient"]
    m = Prescription()
    module_operations("Prescription", prescription_option_list, m, access_check = authenticate_dr_mls)

def medical_tests():
    medical_test_option_list = ["", "Add medical test", "Update medical test", "Delete medical test", "Show medical tests of a particular patient"]
    t = Medical_Test()
    module_operations("Medical Test", medical_test_option_list, t, access_check = authenticate_dr_mls)

def departments():
    department_option_list = ["", "Add department", "Update department", "Delete department", "Show complete department record", "Search department", "Show doctors of a particular department"]
    d = Department()
    #The additional functionality has been incorporated into the generic module operation's 'additional functionality'
    d.additional_functionality = d.list_dept_doctors
    module_operations("Department", department_option_list, d, access_check = authenticate_edit_mode)


# Main Application
st.title("HEALTHCARE INFORMATION MANAGEMENT SYSTEM")
password = st.sidebar.text_input("Enter Password", type="password")

if authenticate(password):
    db.db_init()  # Establish database connection and create tables

    module = st.sidebar.selectbox("Select Module", ["", "Patients", "Doctors", "Prescriptions", "Medical Tests", "Departments"])

    if module == "Patients":
        patients()
    elif module == "Doctors":
        doctors()
    elif module == "Prescriptions":
        prescriptions()
    elif module == "Medical Tests":
        medical_tests()
    elif module == "Departments":
        departments()