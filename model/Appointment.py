import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import pandas as pd
import streamlit as st


class Appointment:
    def __init__(self, date, vaccine, caregiver, patient):
        self.date = date
        self.vaccine = vaccine
        self.caregiver = caregiver
        self.patient = patient

    # getters
    def get_patients(self):
        print_df = []
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        get_appointment_details = "SELECT AppointmentID, Vaccine, Time, Patient FROM Appointments WHERE Caregiver = %s ORDER BY AppointmentID"
        try:
            cursor.execute(get_appointment_details, self.caregiver)
            for row in cursor:
                print_df.append({"Appointment ID":row['AppointmentID'], "Vaccine Name":row['Vaccine'], "Date":row['Time'], "Patient Name": row['Patient']})
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
            st.write(pd.DataFrame(print_df)) if print_df else st.warning("You have no scheduled appointments.")
        return None
    
    def get_caregivers(self):
        print_df = []
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        get_appointment_details = "SELECT AppointmentID, Vaccine, Time, Caregiver FROM Appointments WHERE Patient = %s ORDER BY AppointmentID"
        try:
            cursor.execute(get_appointment_details, self.patient)
            for row in cursor:
                print_df.append({"Appointment ID":row['AppointmentID'], "Vaccine Name":row['Vaccine'], "Date":row['Time'], "Caregiver Name": row['Caregiver']})
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
            st.write(pd.DataFrame(print_df)) if print_df else st.warning("You have no scheduled appointments.")
        return None

    def get_appointment(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        get_appointment_details = "SELECT TOP 1 AppointmentID, Caregiver FROM Appointments ORDER BY AppointmentID DESC"
        try:
            cursor.execute(get_appointment_details)
            for row in cursor:
                s = "Appointment ID: " + str(row['AppointmentID']) + ", Caregiver Username: " + row['Caregiver']
                st.success(s)
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(add_appointment, (self.date, self.vaccine, self.caregiver, self.patient))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
        return None
