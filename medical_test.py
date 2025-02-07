import streamlit as st
from datetime import datetime, time
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

def generate_id(prefix='T'):
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


# --- Medical Test Class ---
class Medical_Test:

    def __init__(self):
        self.id = ""
        self.test_name = ""
        self.patient_id = ""
        self.patient_name = ""
        self.doctor_id = ""
        self.doctor_name = ""
        self.medical_lab_scientist_id = ""
        self.test_date_time = ""
        self.result_date_time = ""
        self.cost = 0
        self.result_and_diagnosis = ""
        self.description = ""
        self.comments = ""

    def medical_test_form(self, medical_test_id = None):
        is_update = medical_test_id is not None #To decide whether it is new or update

        if is_update:
            st.write('Updating medical test details:')
            self.id = medical_test_id

        else:
             st.write('Enter medical test details:')
             self.id = generate_id()
             st.write(f'New Medical test ID: {self.id}')

        self.test_name = st.text_input('Test name')
        patient_id = st.text_input('Patient ID')

        if patient_id:
            if not patient.verify_patient_id(patient_id):
                st.error('Invalid Patient ID')
            else:
                st.success('Patient ID Verified')
                self.patient_id = patient_id
                self.patient_name = fetch_name('patient_record', patient_id)
                st.write(f'Patient Name: {self.patient_name}')
        else:
             self.patient_id = None
             st.warning('Patient ID is required.')

        doctor_id = st.text_input('Doctor ID')
        if doctor_id:
            if not doctor.verify_doctor_id(doctor_id):
                st.error('Invalid Doctor ID')
            else:
                st.success('Doctor ID Verified')
                self.doctor_id = doctor_id
                self.doctor_name = fetch_name('doctor_record', doctor_id)
                st.write(f'Doctor Name: {self.doctor_name}')
        else:
             self.doctor_id = None
             st.warning('Doctor ID is required.')

        self.medical_lab_scientist_id = st.text_input('Medical lab scientist ID')

        test_date = st.date_input('Test date (YYYY/MM/DD)')
        test_time = st.time_input('Test time (hh:mm)', time(0, 0))
        self.test_date_time = f'{test_date.strftime("%d-%m-%Y")} ({test_time.strftime("%H:%M")})'

        result_date = st.date_input('Result date (YYYY/MM/DD)')
        result_time = st.time_input('Result time (hh:mm)', time(0, 0))
        self.result_date_time = f'{result_date.strftime("%d-%m-%Y")} ({result_time.strftime("%H:%M")})'

        self.cost = st.number_input('Cost (INR)', value=0, min_value=0, max_value=10000)
        self.result_and_diagnosis = st.text_area('Result and diagnosis', value = "Test result awaited")
        self.description = st.text_area('Description', value="")
        self.comments = st.text_area('Comments (if any)', value="")

        return st.button('Save')

    def add_medical_test(self):
        """Adds a new medical test record to the database."""
        if self.medical_test_form():
            if not all([self.test_name, self.patient_id, self.doctor_id, self.medical_lab_scientist_id, self.test_date_time, self.result_date_time]):
                st.error("Please complete all the input")
                return

            conn, c = db.connection()
            try:
                c.execute(
                    """
                    INSERT INTO medical_test_record
                    (id, test_name, patient_id, patient_name, doctor_id,
                     doctor_name, medical_lab_scientist_id, test_date_time,
                     result_date_time, cost, result_and_diagnosis, description,
                     comments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (self.id, self.test_name, self.patient_id, self.patient_name,
                     self.doctor_id, self.doctor_name, self.medical_lab_scientist_id,
                     self.test_date_time, self.result_date_time, self.cost,
                     self.result_and_diagnosis, self.description, self.comments)
                )
                conn.commit() #save data if successful
                st.success('Medical test details saved successfully.')

            except Exception as e:
                 st.error(f"Error saving medical test: {e}")
            finally:
                conn.close()

    def update_medical_test(self):
        """Updates an existing medical test record in the database."""
        medical_test_id = st.text_input('Enter Medical Test ID to update')
        if not medical_test_id:
            return

        if not verify_id_exists('medical_test_record', medical_test_id):
            st.error('Invalid Medical Test ID')
            return

        st.success('Medical Test ID Verified')
        if self.medical_test_form(medical_test_id):

            conn, c = db.connection()
            try:
                c.execute(
                    """
                    UPDATE medical_test_record
                    SET test_name=?, patient_id=?, patient_name=?, doctor_id=?,
                     doctor_name=?, medical_lab_scientist_id=?, test_date_time=?,
                     result_date_time=?, cost=?, result_and_diagnosis=?, description=?,
                     comments=?
                    WHERE id = ?
                    """,
                    (self.test_name, self.patient_id, self.patient_name,
                     self.doctor_id, self.doctor_name, self.medical_lab_scientist_id,
                     self.test_date_time, self.result_date_time, self.cost,
                     self.result_and_diagnosis, self.description, self.comments,
                     medical_test_id)
                )

                conn.commit() #Save data if successful
                st.success('Medical test details updated successfully.')

            except Exception as e:
                st.error(f"Error updating medical test: {e}")
            finally:
                conn.close()



    def delete_medical_test(self):
        """Deletes an existing medical test record from the database."""
        medical_test_id = st.text_input('Enter Medical Test ID to delete')
        if not medical_test_id:
            return

        if not verify_id_exists('medical_test_record', medical_test_id):
            st.error('Invalid Medical Test ID')
            return

        st.success('Medical Test ID Verified')
        conn, c = db.connection()

        try:
            # Show the current details before deletion
            c.execute("SELECT * FROM medical_test_record WHERE id = ?", (medical_test_id,))
            details = c.fetchall()
            show_medical_test_details(details)

            confirm_delete = st.checkbox('Confirm Deletion')

            if confirm_delete:
                delete = st.button('Delete')

                if delete:
                    c.execute("DELETE FROM medical_test_record WHERE id = ?", (medical_test_id,))
                    conn.commit() #Save data if successful
                    st.success('Medical test details deleted successfully.')
        except Exception as e:
            st.error(f"Error deleting medical test: {e}")
        finally:
             conn.close()


    def medical_tests_by_patient(self):
        """Shows all medical tests of a particular patient."""
        patient_id = st.text_input('Enter Patient ID to get medical tests')
        if not patient_id:
            return

        if not patient.verify_patient_id(patient_id):
            st.error('Invalid Patient ID')
            return

        st.success('Patient ID Verified')
        patient_name = fetch_name('patient_record', patient_id)
        if not patient_name:
            st.error("Patient name not found.")
            return

        conn, c = db.connection()
        try:
            c.execute("SELECT * FROM medical_test_record WHERE patient_id = ?", (patient_id,))
            tests = c.fetchall()
            st.write(f'Medical tests for {patient_name}:')
            show_medical_test_details(tests)
        except Exception as e:
            st.error(f"Error retrieving tests: {e}")
        finally:
             conn.close()


# --- Display Functions ---
def show_medical_test_details(list_of_medical_tests):
    """Displays medical test details."""
    medical_test_titles = [
        'Medical Test ID', 'Test name', 'Patient ID', 'Patient name',
        'Doctor ID', 'Doctor name', 'Medical Lab Scientist ID',
        'Test date and time [DD-MM-YYYY (hh:mm)]',
        'Result date and time [DD-MM-YYYY (hh:mm)]',
        'Result and diagnosis', 'Description', 'Comments', 'Cost (INR)'
    ]
    show_details(list_of_medical_tests, medical_test_titles)