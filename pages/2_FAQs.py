import streamlit as st


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


if __name__ == '__main__':
    add_logo()
    st.title("FAQs")
    st.markdown("**Q: Where is the vaccine scheduling database hosted?**")
    st.markdown("""**A:** The Python SQL Driver [pymssql](https://www.pymssql.org/) allows the Python application to connect to a [Microsoft Azure](https://azure.microsoft.com/en-us/) database.""")
    st.markdown("**Q: What is the purpose of this application?**")
    st.markdown("""**A:** This application can be deployed by hospitals or clinics and supports interaction with users through a GUI.
                   Patients can search for caregiver availabilities, reserve appointments with caregivers scheduled on a particular day,
                   select available vaccines, cancel appointments, and view all scheduled appointments. Caregivers can search for other
                   caregiver availabilities, upload availabilities, cancel appointments, view all scheduled appointments, and add doses
                   to the vaccine inventory.""")
    st.markdown("**Q: Where is the code base for this application located?**")
    st.markdown("""**A:** The code base for this application can be found on Jake Flynn's [Github](https://github.com/jakeflynn56/).""")
    st.markdown("**Q: Who can register for this application?**")
    st.markdown("""**A:** Anyone who would like to demo the application can create a Patient or Caregiver account to demo the application.""")
