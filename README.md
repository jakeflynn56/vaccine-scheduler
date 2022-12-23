# Streamlit Application for Vaccine Scheduler

**Purpose**
This application can be deployed by hospitals or clinics and supports interaction with users through a GUI. Patients can search for caregiver availabilities, reserve appointments with caregivers scheduled on a particular day, select available vaccines, cancel appointments, and view all scheduled appointments. Caregivers can search for other caregiver availabilities, upload availabilities, cancel appointments, view all scheduled appointments, and add doses to the vaccine inventory.

**Technology**
The Python SQL Driver [pymssql](https://www.pymssql.org/) allows the Python application to connect to a [Microsoft Azure](https://azure.microsoft.com/en-us/) database. The GUI is created using [Streamlit](https://streamlit.io/), which is an open source web app framework in Python.