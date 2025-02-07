import streamlit as st
from datetime import datetime, date
import database as db
import pandas as pd
import department

# Function to verify doctor ID
def verify_doctor_id(doctor_id):
    """Checks if a doctor ID exists in the doctor_record table."""
    conn, c = db.connection()
    c.execute("SELECT id FROM doctor_record WHERE id = ?", (doctor_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Function to show doctor details
def show_doctor_details(list_of_doctors):
    """Displays doctor details in a Streamlit table or as a series."""
    doctor_titles = ['Doctor ID', 'Name', 'Age', 'Gender', 'Date of birth (DD-MM-YYYY)',
                     'Blood group', 'Department ID', 'Department name',
                     'Contact number', 'Alternate contact number', 'Aadhar ID / Voter ID',
                     'Email ID', 'Qualification', 'Specialisation',
                     'Years of experience', 'Address', 'City', 'State', 'PIN code']

    if not list_of_doctors:
        st.warning('No data to show')
    else:
        # Convert list of tuples to list of lists for DataFrame compatibility
        doctor_details = [list(doctor) for doctor in list_of_doctors]

        df = pd.DataFrame(data=doctor_details, columns=doctor_titles)
        st.write(df)


# Function to calculate age
def calculate_age(dob):
    """Calculates age from a date of birth."""
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


# Function to generate doctor ID
def generate_doctor_id():
    """Generates a unique doctor ID based on current date and time."""
    now = datetime.now()
    id_1 = now.strftime('%S%M%H')
    id_2 = now.strftime('%Y%m%d')[2:]
    doctor_id = f'DR-{id_1}-{id_2}'
    return doctor_id


# Function to get department name
def get_department_name(dept_id):
    """Fetches department name from the database given a department ID."""
    conn, c = db.connection()
    c.execute("SELECT name FROM department_record WHERE id = ?", (dept_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None


# Doctor Class
class Doctor:
    def __init__(self):
        self.name = ""
        self.id = ""
        self.age = 0
        self.gender = ""
        self.date_of_birth = ""
        self.blood_group = ""
        self.department_id = ""
        self.department_name = ""
        self.contact_number_1 = ""
        self.contact_number_2 = None
        self.aadhar_or_voter_id = ""
        self.email_id = ""
        self.qualification = ""
        self.specialisation = ""
        self.years_of_experience = 0
        self.address = ""
        self.city = ""
        self.state = ""
        self.pin_code = ""

    def add_doctor(self):
        """Adds a new doctor record to the database."""
        st.subheader("Add New Doctor")

        with st.form("add_doctor_form"):
            self.name = st.text_input("Full Name")
            self.gender = st.radio("Gender", ["Female", "Male", "Other"])
            if self.gender == "Other":
                self.gender = st.text_input("Please Specify")  # Allow other genders
            dob = st.date_input("Date of Birth (YYYY/MM/DD)")
            self.date_of_birth = dob.strftime("%d-%m-%Y")
            self.age = calculate_age(dob)
            self.blood_group = st.text_input("Blood Group")
            self.department_id = st.text_input("Department ID")

            if self.department_id:
                if not department.verify_department_id(self.department_id):
                    st.error("Invalid Department ID")
                else:
                    self.department_name = get_department_name(self.department_id)
                    if self.department_name:
                        st.success(f"Department Verified: {self.department_name}")
                    else:
                         st.error("Department Name not found for this ID")


            self.contact_number_1 = st.text_input("Contact Number")
            self.contact_number_2 = st.text_input("Alternate Contact Number (Optional)")
            self.aadhar_or_voter_id = st.text_input("Aadhar ID / Voter ID")
            self.email_id = st.text_input("Email ID")
            self.qualification = st.text_input("Qualification")
            self.specialisation = st.text_input("Specialisation")
            self.years_of_experience = st.number_input("Years of Experience", min_value=0, max_value=100, value=0)
            self.address = st.text_area("Address")
            self.city = st.text_input("City")
            self.state = st.text_input("State")
            self.pin_code = st.text_input("PIN Code")
            self.id = generate_doctor_id()

            submitted = st.form_submit_button("Save")
            if submitted:
                if not self.name or not self.gender or not self.date_of_birth or not self.blood_group or not self.department_id or not self.contact_number_1 or not self.aadhar_or_voter_id or not self.email_id or not self.qualification or not self.specialisation or not self.address or not self.city or not self.state or not self.pin_code:
                    st.error("Please fill in all the required fields.")

                else:

                    conn, c = db.connection()
                    try:
                        c.execute(
                            """
                            INSERT INTO doctor_record (id, name, age, gender, date_of_birth, blood_group,
                                department_id, department_name, contact_number_1, contact_number_2,
                                aadhar_or_voter_id, email_id, qualification, specialisation,
                                years_of_experience, address, city, state, pin_code)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                self.id, self.name, self.age, self.gender, self.date_of_birth,
                                self.blood_group, self.department_id, self.department_name,
                                self.contact_number_1, self.contact_number_2, self.aadhar_or_voter_id,
                                self.email_id, self.qualification, self.specialisation,
                                self.years_of_experience, self.address, self.city, self.state, self.pin_code
                            ),
                        )
                        conn.commit()  # Commit the changes
                        st.success("Doctor details saved successfully.")
                        st.write(f"Your Doctor ID is: {self.id}")

                    except Exception as e:
                         st.error(f"Error inserting data: {e}")
                    finally:
                        conn.close()

    def update_doctor(self):
        """Updates an existing doctor record in the database."""
        st.subheader("Update Doctor Details")
        doctor_id = st.text_input("Enter Doctor ID to Update")

        if doctor_id:
            if not verify_doctor_id(doctor_id):
                st.error("Invalid Doctor ID")
            else:
                st.success("Doctor ID Verified")
                conn, c = db.connection()

                # Fetch existing data
                c.execute("SELECT * FROM doctor_record WHERE id = ?", (doctor_id,))
                doctor_data = c.fetchone()
                conn.close()

                if doctor_data:
                    st.write("Current Details:")
                    show_doctor_details([doctor_data])
                else:
                    st.error("Doctor data not found.")
                    return  # Exit if data not found

                with st.form("update_doctor_form"):
                    department_id = st.text_input("New Department ID", value=doctor_data[7] if doctor_data else "")
                    if department_id:
                        if not department.verify_department_id(department_id):
                            st.error("Invalid Department ID")
                        else:
                            department_name = get_department_name(department_id)
                            if department_name:
                                st.success(f"Department Verified: {department_name}")
                            else:
                                st.error("Department Name not found for this ID")


                    contact_number_1 = st.text_input("New Contact Number", value=doctor_data[9] if doctor_data else "")
                    contact_number_2 = st.text_input("New Alternate Contact Number (Optional)", value=doctor_data[10] if doctor_data else "")
                    email_id = st.text_input("New Email ID", value=doctor_data[11] if doctor_data else "")
                    qualification = st.text_input("New Qualification", value=doctor_data[12] if doctor_data else "")
                    specialisation = st.text_input("New Specialisation", value=doctor_data[13] if doctor_data else "")
                    years_of_experience = st.number_input("New Years of Experience", min_value=0, max_value=100, value=doctor_data[14] if doctor_data else 0)
                    address = st.text_area("New Address", value=doctor_data[15] if doctor_data else "")
                    city = st.text_input("New City", value=doctor_data[16] if doctor_data else "")
                    state = st.text_input("New State", value=doctor_data[17] if doctor_data else "")
                    pin_code = st.text_input("New PIN Code", value=doctor_data[18] if doctor_data else "")

                    update_submitted = st.form_submit_button("Update")

                    if update_submitted:
                        conn, c = db.connection()
                        try:
                            #Recalculate age.
                            c.execute("SELECT date_of_birth FROM doctor_record WHERE id = ?", (doctor_id,))
                            dob_str = c.fetchone()[0]

                            dob = datetime.strptime(dob_str, "%d-%m-%Y").date()
                            age = calculate_age(dob)

                            c.execute(
                                """
                                UPDATE doctor_record
                                SET age = ?, department_id = ?, department_name = (SELECT name FROM department_record WHERE id = ?),
                                contact_number_1 = ?, contact_number_2 = ?, email_id = ?,
                                qualification = ?, specialisation = ?, years_of_experience = ?,
                                address = ?, city = ?, state = ?, pin_code = ?
                                WHERE id = ?
                                """,
                                (
                                    age,
                                    department_id, department_id,
                                    contact_number_1, contact_number_2,
                                    email_id, qualification, specialisation,
                                    years_of_experience, address, city, state, pin_code,
                                    doctor_id,
                                ),
                            )

                            conn.commit()
                            st.success("Doctor details updated successfully.")

                        except Exception as e:
                            st.error(f"Error updating data: {e}")
                        finally:
                            conn.close()


    def delete_doctor(self):
        """Deletes an existing doctor record from the database."""
        st.subheader("Delete Doctor")
        doctor_id = st.text_input("Enter Doctor ID to Delete")

        if doctor_id:
            if not verify_doctor_id(doctor_id):
                st.error("Invalid Doctor ID")
            else:
                st.success("Doctor ID Verified")
                conn, c = db.connection()

                # Fetch and show doctor data before deletion
                c.execute("SELECT * FROM doctor_record WHERE id = ?", (doctor_id,))
                doctor_data = c.fetchone()
                if doctor_data:
                    st.write("Details of Doctor to be Deleted:")
                    show_doctor_details([doctor_data])  # Show the details before asking for confirmation
                else:
                    st.error("Doctor not found.")
                    conn.close()  # Close connection before returning
                    return

                confirm_delete = st.checkbox("Confirm Deletion")

                if confirm_delete:
                    delete_button = st.button("Delete")

                    if delete_button:
                        try:
                            c.execute("DELETE FROM doctor_record WHERE id = ?", (doctor_id,))
                            conn.commit()
                            st.success("Doctor deleted successfully.")

                        except Exception as e:
                             st.error(f"Error deleting doctor: {e}")

                        finally:
                            conn.close()



    def show_all_doctors(self):
        """Shows all doctor records from the database."""
        st.subheader("All Doctors")
        conn, c = db.connection()
        c.execute("SELECT * FROM doctor_record")
        doctors = c.fetchall()
        conn.close()
        show_doctor_details(doctors)

    def search_doctor(self):
        """Searches and displays a doctor's details by ID."""
        st.subheader("Search Doctor")
        doctor_id = st.text_input("Enter Doctor ID to Search")

        if doctor_id:
            if not verify_doctor_id(doctor_id):
                st.error("Invalid Doctor ID")
            else:
                st.success("Doctor ID Verified")
                conn, c = db.connection()
                c.execute("SELECT * FROM doctor_record WHERE id = ?", (doctor_id,))
                doctor = c.fetchone()
                conn.close()

                if doctor:
                    st.write("Doctor Details:")
                    show_doctor_details([doctor])
                else:
                    st.error("Doctor not found.")