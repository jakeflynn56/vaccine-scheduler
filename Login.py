from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import streamlit as st
import pandas as pd


def get_availability(d):
    # Returns list of available Caregivers in alphabetical order for a given Time
    # Returns None if no Caregivers are available at the given Time
    res = []
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    get_patient_details = """SELECT Username FROM Availabilities WHERE Time = %s EXCEPT 
                             SELECT Caregiver FROM Appointments WHERE Time = %s ORDER BY Username"""
    try:
        cursor.execute(get_patient_details, (d, d))
        for row in cursor:
            res.append(row['Username'])
    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return res if len(res) > 0 else None


def delete_appointment_from_db(id):
    # Deletes the specified appointment from the Appointments table
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    delete_appointment = "DELETE FROM Appointments WHERE AppointmentID = %s"
    try:
        cursor.execute(delete_appointment, id)
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        raise
    finally:
        cm.close_connection()
    return None


def get_cancelation_info(id):
    # Returns the appointment information for a canceled appointment
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    get_cancelation_info = "SELECT Vaccine, Time, Caregiver, Patient FROM Appointments WHERE AppointmentID = %s"
    try:
        cursor.execute(get_cancelation_info, id)
        for row in cursor:
            info = row['Vaccine'], row['Time'], row['Caregiver'], row['Patient']
            return info
    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return None


def login_patient(username, password):
    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        st.warning("Login failed.")
        st.error(e)
        quit()
    except Exception as e:
        st.warning("Login failed.")
        st.error(e)
        return
    # check if the login was successful
    if patient is None:
        return False
    else:
        return True


def login_caregiver(username, password):
    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        st.warning("Login failed.")
        st.error(e)
        quit()
    except Exception as e:
        st.warning("Login failed.")
        st.error(e)
        return
    # check if the login was successful
    if caregiver is None:
        return False
    else:
        return True


def search_caregiver_schedule(date):
    date = str(date)
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    avail_d = []
    # Checks if there is a Caregiver available on specified date
    try:
        d = datetime.datetime(year, month, day)
        availabilities = get_availability(d)
    except pymssql.Error as e:
        st.warning("Search Caregiver Schedule Failed")
        st.error(e)
        return
    vaccine_available = False
    for v in current_vaccines:
        if current_vaccines[v].get_available_doses() > 0:
            vaccine_available = True
    if availabilities and vaccine_available:
        st.success("Caregivers with availability at the specified time:")
        for avaiability in availabilities:
            for v in current_vaccines:
                if current_vaccines[v].get_available_doses() > 0:
                    avail_d.append({"Caregiver":avaiability, "Vaccine Name": v, "Available Doses":current_vaccines[v].get_available_doses()})
        st.write(pd.DataFrame(avail_d))
        return availabilities[0]
    elif availabilities:
        st.warning("There are no vaccines available at this time.")
    else:
        st.warning("There are no caregivers available at the specified time.")
        return availabilities
    

def reserve(vaccine, appointment):
    # assume input is hyphenated in the format yyyy-mm-dd
    date = str(appointment)
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        date = datetime.datetime(year, month, day)
        get_availability(date)
    except pymssql.Error as e:
        st.warning("Reservation Failed")
        st.error(e)
        return
    if get_availability(date):
        caregiver = get_availability(date)[0]
    else:
        st.warning("No Caregiver is available!")
        return
    if vaccine in current_vaccines and current_vaccines[vaccine].get_available_doses() > 0:
        current_vaccines[vaccine].decrease_available_doses(1)
        appointment = Appointment(date, vaccine, caregiver, st.session_state['current_patient'].get_username())
        appointment.save_to_db()
        st.success("Reservation successful.")
        appointment.get_appointment()
    else:
        st.warning("Not enough available doses!")
        return


def upload_availability(date):
    date = str(date)
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        st.session_state['current_caregiver'].upload_availability(d)
    except pymssql.Error as e:
        st.warning("Upload Availability Failed")
        st.error(e)
        return
    except ValueError:
        st.warning("Please enter a valid date!")
        return
    except Exception as e:
        st.warning("Error occurred when uploading availability")
        st.error(e)
        return
    st.success("Availability uploaded!")


def cancel(id):
    id = id.split()[0]
    if not id.isnumeric():
        st.warning("Please enter a valid Appointment ID.")
        return
    info = get_cancelation_info(id)
    # Checks if the appointments exists and if the appointment is related to the current user logged in
    if info and ((st.session_state['current_caregiver'] and info[2] == st.session_state['current_caregiver'].get_username()) or (st.session_state['current_patient'] and info[3] == st.session_state['current_patient'].get_username())):
        delete_appointment_from_db(id)
        current_vaccines[info[0]].increase_available_doses(1)
        st.success("Cancellation successful.")
    else:
        st.warning("You entered the incorrect Appointment ID!")


def add_doses(vaccine_name, doses):
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        st.warning("Error occurred when adding doses")
        st.error(e)
        quit()
    except Exception as e:
        st.warning("Error occurred when adding doses")
        st.error(e)
        return
    # if the vaccine is not found in the database, add a new (vaccine, doses)
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            st.warning("Error occurred when adding doses")
            st.error(e)
            quit()
        except Exception as e:
            st.warning("Error occurred when adding doses")
            st.error(e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            st.warning("Error occurred when adding doses")
            st.error(e)
            quit()
        except Exception as e:
            st.warning("Error occurred when adding doses")
            st.error(e)
            return
    st.success("Doses updated!")


def show_appointments():
    if st.session_state['current_patient'] is None and st.session_state['current_caregiver']:
        Appointment(None, None, st.session_state['current_caregiver'].get_username(), None).get_patients()
    elif st.session_state['current_patient'] and st.session_state['current_caregiver'] is None:
        Appointment(None, None, None, st.session_state['current_patient'].get_username()).get_caregivers()


def show_main_page():
    with mainSection:
        if st.session_state['current_patient']:
            call_login_patient()
        elif st.session_state['current_caregiver']:
            call_login_caregiver()


def show_login_page():
    with loginSection.form('login'):
        if st.session_state['loggedIn'] == False:
            st.markdown("#### Login")
            userName = st.text_input("Username")
            password = st.text_input("Password", type="password")
            select = st.selectbox("User Type", ["Caregiver", "Patient"])
            b = st.form_submit_button("Login")
    if b:
        LoggedIn_Clicked(userName, password, select)


def LoggedIn_Clicked(userName, password, select):
    if select == "Patient" and login_patient(userName, password):
        st.session_state['loggedIn'] = True
        st.session_state['current_patient'] = Patient(userName, password=password).get()
    elif select == "Caregiver" and login_caregiver(userName, password):
        st.session_state['loggedIn'] = True
        st.session_state['current_caregiver'] = Caregiver(userName, password=password).get()
    else:
        st.session_state['loggedIn'] = False
        st.session_state['current_patient'] = None
        st.session_state['current_caregiver'] = None
        st.error("Invalid user name or password")


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    st.session_state['current_patient'] = None
    st.session_state['current_caregiver'] = None


def show_logout_page():
    loginSection.empty()
    registerSection.empty()
    with logOutSection:
        st.button("Log Out", key="logout", on_click=LoggedOut_Clicked)


def call_login_patient():
    # Creates the main page for a patient
    st.markdown("Logged in as: " + "*" + st.session_state['current_patient'].get_username() + "*")
    tab1, tab2, tab3, tab4 = st.tabs(["Find availabilities", "Reserve an appointment", "Cancel an appointment", "Show appointments"])
    with tab1:
        new_placeholder = st.empty()
        with new_placeholder.form("Availabilities"):
            st.markdown("#### Find availabilities")
            availabilities = st.date_input("Availabilities")
            submit2 = st.form_submit_button("Find")
        if submit2:
            search_caregiver_schedule(availabilities)
    with tab2:
        new_placeholder = st.empty()
        with new_placeholder.form("reserve"):
            st.markdown("#### Reserve an appointment")
            vaccine = st.selectbox("Vaccine", ["moderna", "pfizer", "j&j"])
            appointment = st.date_input("Appointment")
            submit2 = st.form_submit_button("Reserve")
        if submit2:
            reserve(vaccine, appointment)
    with tab3:
        new_placeholder = st.empty()
        with new_placeholder.form("cancel"):
            st.markdown("#### Cancel an appointment")
            id = st.text_input("Appointment ID")
            submit2 = st.form_submit_button("Cancel")
        if submit2:
            cancel(id)
    with tab4:
        button = st.button("Show appointments")
        if button:
            show_appointments()


def call_login_caregiver():
    # Creates the main page for a caregiver
    st.markdown("Logged in as: " + "*" + st.session_state['current_caregiver'].get_username() + "*")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Find availabilities", "Upload availabilities", "Cancel an appointment", "Show appointments", "Add doses"])
    with tab1:
        new_placeholder = st.empty()
        with new_placeholder.form("Availabilities"):
            st.markdown("#### Find availabilities")
            availabilities = st.date_input("Availabilities")
            submit2 = st.form_submit_button("Find")
        if submit2:
            search_caregiver_schedule(availabilities)
    with tab2:
        new_placeholder = st.empty()
        with new_placeholder.form("upload"):
            st.markdown("#### Upload availabilities")
            date = st.date_input("Availability")
            submit2 = st.form_submit_button("Upload")
        if submit2:
            upload_availability(date)
    with tab3:
        new_placeholder = st.empty()
        with new_placeholder.form("cancel"):
            st.markdown("#### Cancel an appointment")
            id = st.text_input("Appointment ID")
            submit2 = st.form_submit_button("Cancel")
        if submit2:
            cancel(id)
    with tab4:
        button = st.button("Show appointments")
        if button:
            show_appointments()
    with tab5:
        new_placeholder = st.empty()
        with new_placeholder.form("doses"):
            st.markdown("#### Add doses")
            vaccine = st.selectbox("Vaccine", ['pfizer', 'moderna', 'j&j'])
            num = st.slider("Number of doses", 0, 10)
            submit2 = st.form_submit_button("Add doses")
        if submit2:
            add_doses(vaccine, num)


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
    # The three types of authorized vaccines are moderna, pfizer, and j&j
    current_vaccines = {"moderna": Vaccine("moderna", 3), "pfizer": Vaccine("pfizer", 3), "j&j": Vaccine("j&j", 3)}
    for v in current_vaccines:
        if not current_vaccines[v].get():
            current_vaccines[v].save_to_db()
    headerSection = st.container()
    mainSection = st.container()
    loginSection = st.container()
    registerSection = st.container()
    logOutSection = st.container()
    with headerSection:
        st.title("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")
        # first run will have nothing in session_state
        if 'loggedIn' not in st.session_state:
            st.session_state['loggedIn'] = False
            st.session_state['current_patient'] = None
            st.session_state['current_caregiver'] = None
            show_login_page()
        else:
            if st.session_state['loggedIn'] and st.session_state['current_patient']:
                show_logout_page()    
                show_main_page()
            elif st.session_state['loggedIn'] and st.session_state['current_caregiver']:
                show_logout_page()    
                show_main_page()
            else:
                show_login_page()
