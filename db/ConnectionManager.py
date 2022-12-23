import pymssql
import streamlit as st


class ConnectionManager:

    def __init__(self):
        self.server_name = st.secrets['SERVER'] + ".database.windows.net"
        self.db_name = st.secrets['DBNAME']
        self.user = st.secrets['USERID']
        self.password = st.secrets['PASSWORD']
        self.conn = None

    def create_connection(self):
        try:
            self.conn = pymssql.connect(server=self.server_name,
                                        user=self.user,
                                        password=self.password,
                                        database=self.db_name)
        except pymssql.Error as db_err:
            st.warning("""Database Programming Error in SQL
                          connection processing!""")
            st.error(db_err)
            quit()
        return self.conn

    def close_connection(self):
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            st.warning("""Database Programming Error in SQL
                          connection processing!""")
            st.error(db_err)
            quit()
