import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd

# --- Utility Functions ---
def verify_id_exists(table_name, id_value):
    """Verifies if an ID exists in a given table."""
    conn, c = db.connection()
    c.execute(f"SELECT id FROM {table_name} WHERE id = ?", (id_value,))
    result = c.fetchone()
    conn.close()
    return result is not None

def show_details(list_of_records, titles):
    """Displays details in a Streamlit DataFrame."""
    if not list_of_records:
        st.warning('No data to show')
        return

    data = [list(record) for record in list_of_records]
    df = pd.DataFrame(data, columns=titles)
    st.write(df)

def generate_id(date_str, time_str, prefix='P'):
    """Generates a unique ID."""
    id_1 = ''.join(time_str.split(':')[::-1])
    id_2 = ''.join(date_str.split('-')[::-1])[2:]
    return f'{prefix}-{id_1}-{id_2}'

def calculate_age(dob):
    """Calculates age from a date of birth."""
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


# --- Patient Class ---
class Patient:

    def __init__(self):
        self.name = ""
        self.id = ""
        self.gender = ""
        self.age = 0
        self.contact_number_1 = ""
        self.contact_number_2 = ""
        self.date_of_birth = ""
        self.blood_group = ""
        self.date_of_registration = ""
        self.time_of_registration = ""
        self.email_id = ""
        self.aadhar_or_voter_id = ""
        self.height = 0
        self.weight = 0
        self.next_of_kin_name = ""
        self.next_of_kin_relation_to_patient = ""
        self.next_of_kin_contact_number = ""
        self.address = ""
        self.city = ""
        self.state = ""
        self.pin_code = ""

    def patient_form(self, patient_id = None):
        """Unified form for adding/updating patients."""
        is_update = patient_id is not None

        if is_update:
            st.write("Updating patient details:")
            self.id = patient_id
        else:
            st.write("Enter patient details:")
            self.date_of_registration = datetime.now().strftime('%d-%m-%Y')
            self.time_of_registration = datetime.now().strftime('%H:%M:%S')
            self.id = generate_id(self.date_of_registration, self.time_of_registration)
            st.write(f"New Patient ID: {self.id}")

        self.name = st.text_input("Full name")
        self.gender = st.radio("Gender", ["Female", "Male", "Other"])
        if self.gender == "Other":
            self.gender = st.text_input("Please specify")
        dob = st.date_input("Date of birth (YYYY/MM/DD)")
        self.date_of_birth = dob.strftime("%d-%m-%Y")
        self.age = calculate_age(dob)
        self.blood_group = st.text_input("Blood group")
        self.contact_number_1 = st.text_input("Contact number")
        self.contact_number_2 = st.text_input("Alternate contact number (optional)", value="")
        self.aadhar_or_voter_id = st.text_input("Aadhar ID / Voter ID")
        self.weight = st.number_input("Weight (in kg)", value=0, min_value=0, max_value=400)
        self.height = st.number_input("Height (in cm)", value=0, min_value=0, max_value=275)
        self.address = st.text_area("Address")
        self.city = st.text_input("City")
        self.state = st.text_input("State")
        self.pin_code = st.text_input("PIN code")
        self.next_of_kin_name = st.text_input("Next of kin's name")
        self.next_of_kin_relation_to_patient = st.text_input("Next of kin's relation to patient")
        self.next_of_kin_contact_number = st.text_input("Next of kin's contact number")
        self.email_id = st.text_input("Email ID (optional)", value="")

        return st.button("Save")

    def add_patient(self):
        """Adds a new patient record to the database."""
        if self.patient_form():
            if not all([self.name, self.gender, self.date_of_birth, self.blood_group, self.contact_number_1, self.aadhar_or_voter_id, self.next_of_kin_name, self.next_of_kin_relation_to_patient, self.next_of_kin_contact_number, self.address, self.city, self.state, self.pin_code]):
                st.error("Please fill in all the required fields.")
                return

            conn, c = db.connection()
            try:
                c.execute(
                    """
                    INSERT INTO patient_record (
                        id, name, age, gender, date_of_birth, blood_group,
                        contact_number_1, contact_number_2, aadhar_or_voter_id,
                        weight, height, address, city, state, pin_code,
                        next_of_kin_name, next_of_kin_relation_to_patient,
                        next_of_kin_contact_number, email_id,
                        date_of_registration, time_of_registration
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.id, self.name, self.age, self.gender, self.date_of_birth,
                        self.blood_group, self.contact_number_1, self.contact_number_2,
                        self.aadhar_or_voter_id, self.weight, self.height, self.address,
                        self.city, self.state, self.pin_code, self.next_of_kin_name,
                        self.next_of_kin_relation_to_patient, self.next_of_kin_contact_number,
                        self.email_id, self.date_of_registration, self.time_of_registration
                    )
                )
                conn.commit()
                st.success("Patient details saved successfully.")
                st.write(f"Your Patient ID is: {self.id}")

            except Exception as e:
                 st.error(f"Error saving patient: {e}")
            finally:
                conn.close()

    def update_patient(self):
        """Updates an existing patient record."""
        patient_id = st.text_input("Enter Patient ID to update")
        if not patient_id:
            return

        if not verify_id_exists("patient_record", patient_id):
            st.error("Invalid Patient ID")
            return

        st.success("Patient ID Verified")

        if self.patient_form(patient_id):
            conn, c = db.connection()
            try:
                #Recalculate age.
                c.execute("SELECT date_of_birth FROM patient_record WHERE id = ?", (patient_id,))
                dob_str = c.fetchone()[0]

                dob = datetime.strptime(dob_str, "%d-%m-%Y").date()
                self.age = calculate_age(dob)

                c.execute(
                    """
                    UPDATE patient_record
                    SET age = ?, contact_number_1 = ?, contact_number_2 = ?,
                        weight = ?, height = ?, address = ?, city = ?,
                        state = ?, pin_code = ?, next_of_kin_name = ?,
                        next_of_kin_relation_to_patient = ?,
                        next_of_kin_contact_number = ?, email_id = ?
                    WHERE id = ?
                    """,
                    (
                        self.age, self.contact_number_1, self.contact_number_2,
                        self.weight, self.height, self.address, self.city,
                        self.state, self.pin_code, self.next_of_kin_name,
                        self.next_of_kin_relation_to_patient,
                        self.next_of_kin_contact_number, self.email_id,
                        patient_id
                    )
                )
                conn.commit()
                st.success("Patient details updated successfully.")
            except Exception as e:
                st.error(f"Error updating patient: {e}")
            finally:
                conn.close()

    def delete_patient(self):
        """Deletes an existing patient record."""
        patient_id = st.text_input("Enter Patient ID to delete")
        if not patient_id:
            return

        if not verify_id_exists("patient_record", patient_id):
            st.error("Invalid Patient ID")
            return

        st.success("Patient ID Verified")

        conn, c = db.connection()
        try:
            # Show the current details before deletion
            c.execute("SELECT * FROM patient_record WHERE id = ?", (patient_id,))
            details = c.fetchall()
            show_patient_details(details)

            confirm_delete = st.checkbox("Confirm Deletion")
            if confirm_delete:
                delete = st.button("Delete")
                if delete:
                    c.execute("DELETE FROM patient_record WHERE id = ?", (patient_id,))
                    conn.commit()
                    st.success("Patient details deleted successfully.")
        except Exception as e:
            st.error(f"Error deleting patient: {e}")
        finally:
            conn.close()

    def show_all_patients(self):
        """Shows all patient records."""
        conn, c = db.connection()
        try:
            c.execute("SELECT * FROM patient_record")
            patients = c.fetchall()
            show_patient_details(patients)
        except Exception as e:
            st.error(f"Error retrieving patients: {e}")
        finally:
            conn.close()

    def search_patient(self):
        """Searches for a patient by ID."""
        patient_id = st.text_input("Enter Patient ID to search")
        if not patient_id:
            return

        if not verify_id_exists("patient_record", patient_id):
            st.error("Invalid Patient ID")
            return

        st.success("Patient ID Verified")

        conn, c = db.connection()
        try:
            c.execute("SELECT * FROM patient_record WHERE id = ?", (patient_id,))
            patient = c.fetchone()
            if patient:
                show_patient_details([patient])
            else:
                st.error("Patient not found.")
        except Exception as e:
            st.error(f"Error retrieving patient: {e}")
        finally:
            conn.close()


# --- Display Functions ---
def show_patient_details(list_of_patients):
    """Displays patient details."""
    patient_titles = [
        "Patient ID", "Name", "Age", "Gender", "Date of birth (DD-MM-YYYY)",
        "Blood group", "Contact number", "Alternate contact number",
        "Aadhar ID / Voter ID", "Weight (kg)", "Height (cm)", "Address",
        "City", "State", "PIN code", "Next of kin's name",
        "Next of kin's relation to patient",
        "Next of kin's contact number", "Email ID",
        "Date of registration (DD-MM-YYYY)", "Time of registration (hh:mm:ss)"
    ]
    show_details(list_of_patients, patient_titles)