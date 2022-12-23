from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import re
import streamlit as st
import pandas as pd


def check_password_strength(password):
    # ReGex to check if a password contains uppercase, lowercase, special character, and numeric value
    regex = ("^(?=.*[a-z])(?=." +
             "*[A-Z])(?=.*\\d)" +
             "(?=.*[!@#?]).+$")
    # Compile the ReGex
    p = re.compile(regex)
    # Return False if the password is less than 8 characters
    if (len(password) < 8):
        return False
    # Return True if the password matches ReGex
    if(re.search(p, password)):
        return True
    else:
        return False


def create_patient(username, password):
    # create_patient <username> <password>
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the patient
    patient = Patient(username, salt=salt, hash=hash)
    # save patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(username, password):
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)
    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def show_register_page():
    headerSection = st.container()
    registerSection = st.container()
    with headerSection:
        st.title("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")
        with registerSection.form('register'):
            st.markdown("#### Register")
            userName = st.text_input("Username")
            password = st.text_input("Password", type="password", help="Password must be at least 8 characters, contain a mixture of both uppercase and lowercase letters, a mixture of letters and numbers, and inclusion of at least one special character.")
            select = st.selectbox("User Type", ["Caregiver", "Patient"])
            # st.button("Login", on_click=LoggedIn_Clicked, args=(userName, password, select))
            b = st.form_submit_button("Register")
        if b and not check_password_strength(password):
            st.warning("Please choose a stronger password.")
        elif b and select == "Patient" and username_exists_patient(userName):
            st.warning("User already exists. Please choose another username.")
        elif b and select == "Caregiver" and username_exists_caregiver(userName):
            st.warning("User already exists. Please choose another username.")
        elif b and select == "Patient":
            create_patient(userName, password)
            st.success("Registration successful")
        elif b and select == "Caregiver":
            create_caregiver(userName, password)
            st.success("Registration successful")


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "Vaccine Scheduler";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    add_logo()
    if not st.session_state['loggedIn']:
        show_register_page()
    else:
        st.warning("User already logged in.")
