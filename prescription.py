import streamlit as st
from datetime import datetime
import database as db
import pandas as pd
import patient
import doctor

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

def generate_id(prefix='M'):
    """Generates a unique ID."""
    now = datetime.now()
    id_1 = now.strftime('%S%M%H')
    id_2 = now.strftime('%Y%m%d')[2:]
    return f'{prefix}-{id_1}-{id_2}'

def fetch_name(table_name, id_value):
    """Fetches a name from a given table by ID."""
    conn, c = db.connection()
    c.execute(f"SELECT name FROM {table_name} WHERE id = ?", (id_value,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# --- Prescription Class ---
class Prescription:

    def __init__(self):
        self.id = str()
        self.patient_id = str()
        self.patient_name = str()
        self.doctor_id = str()
        self.doctor_name = str()
        self.diagnosis = str()
        self.comments = str()
        self.medicine_1_name = str()
        self.medicine_1_dosage_description = str()
        self.medicine_2_name = str()
        self.medicine_2_dosage_description = str()
        self.medicine_3_name = str()
        self.medicine_3_dosage_description = str()

    def prescription_form(self, prescription_id=None):
        """Unified form for adding/updating prescriptions."""
        is_update = prescription_id is not None

        if is_update:
            st.write("Updating prescription details:")
            self.id = prescription_id
        else:
            st.write("Enter prescription details:")
            self.id = generate_id()
            st.write(f"New Prescription ID: {self.id}")

        patient_id = st.text_input("Patient ID")
        if patient_id:
            if not patient.verify_patient_id(patient_id):
                st.error("Invalid Patient ID")
            else:
                st.success("Patient ID Verified")
                self.patient_id = patient_id
                self.patient_name = fetch_name("patient_record", patient_id)
                st.write(f"Patient Name: {self.patient_name}")
        else:
            st.error("Patient ID is required.")
            return False

        doctor_id = st.text_input("Doctor ID")
        if doctor_id:
            if not doctor.verify_doctor_id(doctor_id):
                st.error("Invalid Doctor ID")
            else:
                st.success("Doctor ID Verified")
                self.doctor_id = doctor_id
                self.doctor_name = fetch_name("doctor_record", doctor_id)
                st.write(f"Doctor Name: {self.doctor_name}")
        else:
            st.error("Doctor ID is required.")
            return False

        self.diagnosis = st.text_area("Diagnosis")
        self.comments = st.text_area("Comments (if any)", value="")
        self.medicine_1_name = st.text_input("Medicine 1 name")
        self.medicine_1_dosage_description = st.text_area("Medicine 1 dosage and description")
        self.medicine_2_name = st.text_input("Medicine 2 name (if any)", value="")
        self.medicine_2_dosage_description = st.text_area("Medicine 2 dosage and description", value="")
        self.medicine_3_name = st.text_input("Medicine 3 name (if any)", value="")
        self.medicine_3_dosage_description = st.text_area("Medicine 3 dosage and description", value="")

        return st.button("Save")

    def add_prescription(self):
        """Adds a new prescription record to the database."""
        if self.prescription_form():
            if not all([self.patient_id, self.doctor_id]):
                st.error("Please fill in all required fields.")
                return

            conn, c = db.connection()
            try:
                c.execute(
                    """
                    INSERT INTO prescription_record (
                        id, patient_id, patient_name, doctor_id, doctor_name,
                        diagnosis, comments, medicine_1_name, medicine_1_dosage_description,
                        medicine_2_name, medicine_2_dosage_description, medicine_3_name,
                        medicine_3_dosage_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.id, self.patient_id, self.patient_name, self.doctor_id,
                        self.doctor_name, self.diagnosis, self.comments,
                        self.medicine_1_name, self.medicine_1_dosage_description,
                        self.medicine_2_name, self.medicine_2_dosage_description,
                        self.medicine_3_name, self.medicine_3_dosage_description,
                    ),
                )
                conn.commit()
                st.success("Prescription details saved successfully.")
            except Exception as e:
                st.error(f"Error saving prescription: {e}")
            finally:
                conn.close()

    def update_prescription(self):
        """Updates an existing prescription record."""
        prescription_id = st.text_input("Enter Prescription ID to update")
        if not prescription_id:
            return

        if not verify_id_exists("prescription_record", prescription_id):
            st.error("Invalid Prescription ID")
            return

        st.success("Prescription ID Verified")

        if self.prescription_form(prescription_id):
            conn, c = db.connection()
            try:
                c.execute(
                    """
                    UPDATE prescription_record
                    SET diagnosis = ?, comments = ?, medicine_1_name = ?,
                        medicine_1_dosage_description = ?, medicine_2_name = ?,
                        medicine_2_dosage_description = ?, medicine_3_name = ?,
                        medicine_3_dosage_description = ?
                    WHERE id = ?
                    """,
                    (
                        self.diagnosis, self.comments, self.medicine_1_name,
                        self.medicine_1_dosage_description, self.medicine_2_name,
                        self.medicine_2_dosage_description, self.medicine_3_name,
                        self.medicine_3_dosage_description, prescription_id,
                    ),
                )
                conn.commit()
                st.success("Prescription details updated successfully.")
            except Exception as e:
                st.error(f"Error updating prescription: {e}")
            finally:
                conn.close()

    def delete_prescription(self):
        """Deletes an existing prescription record."""
        prescription_id = st.text_input("Enter Prescription ID to delete")
        if not prescription_id:
            return

        if not verify_id_exists("prescription_record", prescription_id):
            st.error("Invalid Prescription ID")
            return

        st.success("Prescription ID Verified")

        conn, c = db.connection()
        try:
            # Show the current details before deletion
            c.execute("SELECT * FROM prescription_record WHERE id = ?", (prescription_id,))
            details = c.fetchall()
            show_prescription_details(details)

            confirm_delete = st.checkbox("Confirm Deletion")
            if confirm_delete:
                delete = st.button("Delete")
                if delete:
                    c.execute("DELETE FROM prescription_record WHERE id = ?", (prescription_id,))
                    conn.commit()
                    st.success("Prescription details deleted successfully.")
        except Exception as e:
            st.error(f"Error deleting prescription: {e}")
        finally:
            conn.close()

    def prescriptions_by_patient(self):
        """Shows all prescriptions of a particular patient."""
        patient_id = st.text_input("Enter Patient ID to get prescriptions")
        if not patient_id:
            return

        if not patient.verify_patient_id(patient_id):
            st.error("Invalid Patient ID")
            return

        st.success("Patient ID Verified")
        patient_name = fetch_name("patient_record", patient_id)
        if not patient_name:
            st.error("Patient name not found.")
            return

        conn, c = db.connection()
        try:
            c.execute("SELECT * FROM prescription_record WHERE patient_id = ?", (patient_id,))
            prescriptions = c.fetchall()
            st.write(f"Prescriptions for {patient_name}:")
            show_prescription_details(prescriptions)
        except Exception as e:
            st.error(f"Error retrieving prescriptions: {e}")
        finally:
            conn.close()


# --- Display Functions ---
def show_prescription_details(list_of_prescriptions):
    """Displays prescription details."""
    prescription_titles = [
        "Prescription ID", "Patient ID", "Patient name", "Doctor ID",
        "Doctor name", "Diagnosis", "Comments", "Medicine 1 name",
        "Medicine 1 dosage and description", "Medicine 2 name",
        "Medicine 2 dosage and description", "Medicine 3 name",
        "Medicine 3 dosage and description",
    ]
    show_details(list_of_prescriptions, prescription_titles)