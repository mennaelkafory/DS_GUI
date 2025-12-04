import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error


@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="menna",  
        database="Company"
    )

#select data

def get_columns_info(table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SHOW COLUMNS FROM {table}")
    return cur.fetchall()  
def get_columns(table):
    info = get_columns_info(table)
    return [col[0] for col in info]


def select_data(table):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df, use_container_width=True)

#insert data hide auto_increament columns

def insert_data(table):
    st.subheader("Insert New Row")

    col_info = get_columns_info(table)

    # hide auto_increment columns
    insertable_cols = [c[0] for c in col_info if "auto_increment" not in c[5]]

    st.info("AUTO_INCREMENT columns are hidden and will be generated automatically.")

    user_values = {}
    for col in insertable_cols:
        user_values[col] = st.text_input(f"{col}:")

    if st.button("Insert"):
        try:
            conn = get_connection()
            cur = conn.cursor()

            cols_str = ", ".join(insertable_cols)
            placeholders = ", ".join(["%s"] * len(insertable_cols))
            values = [user_values[c] for c in insertable_cols]

            query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
            cur.execute(query, values)
            conn.commit()

            st.success("Row inserted successfully ✔")

        except Error as e:
            st.error(f"Error: {e}")


# ---------------------------------------------------------
# update data (Check if condition exists first)
# ---------------------------------------------------------
def update_data(table):
    st.subheader("Update Row")

    cols = get_columns(table)

    st.info("Choose the condition for the WHERE clause:")

    condition_col = st.selectbox("Condition Column:", cols)
    condition_value = st.text_input("Condition Value:")

    st.divider()
    st.subheader("Columns to Update")

    update_values = {}
    for col in cols:
        new_val = st.text_input(f"New value for {col} (optional):")
        if new_val != "":
            update_values[col] = new_val

    if st.button("Update"):
        if condition_value == "":
            st.error("❌ Cannot update without a WHERE condition.")
            return

        if len(update_values) == 0:
            st.error("❌ No columns selected to update.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            #check if value exists
            cur.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {condition_col} = %s",
                (condition_value,)
            )
            exists = cur.fetchone()[0]

            if exists == 0:
                st.warning("⚠ No rows found with this condition. Update canceled.")
                return

            # update
            set_part = ", ".join([f"{col} = %s" for col in update_values])
            set_values = list(update_values.values())

            query = f"UPDATE {table} SET {set_part} WHERE {condition_col} = %s"
            set_values.append(condition_value)

            cur.execute(query, set_values)
            conn.commit()

            st.success("Row updated successfully ✔")

        except Error as e:
            st.error(f"Error: {e}")


# ---------------------------------------------------------
# delete data (check  codition)
# ---------------------------------------------------------
def delete_data(table):
    st.subheader("Delete Row")

    cols = get_columns(table)

    st.info("Choose the condition for the DELETE operation:")

    condition_col = st.selectbox("Condition Column:", cols)
    condition_value = st.text_input("Condition Value to delete:")

    if st.button("Delete"):
        if condition_value == "":
            st.error("❌ Cannot delete without a WHERE condition.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            # check if value exists 
            cur.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {condition_col} = %s",
                (condition_value,)
            )
            exists = cur.fetchone()[0]

            if exists == 0:
                st.warning("⚠ No rows found with this condition. Delete canceled.")
                return

            # delete
            query = f"DELETE FROM {table} WHERE {condition_col} = %s"
            cur.execute(query, (condition_value,))
            conn.commit()

            st.success("Row deleted successfully ✔")

        except Error as e:
            st.error(f"Error: {e}")


#giu
st.title("📊 Company Database ")

operation = st.selectbox(
    "Choose Operation:",
    ["Select", "Insert", "Update", "Delete"]
)

tables = [
    "Customer", "Customerphone", "Salesperson", "Salespersonphone",
    "Supplier", "Product", "Orders", "Orderdetail"
]

table = st.selectbox("Choose Table:", tables)

st.divider()
st.subheader(f"{operation} on {table}")

# Run selected operation
if operation == "Select":
    select_data(table)
elif operation == "Insert":
    insert_data(table)
elif operation == "Update":
    update_data(table)
elif operation == "Delete":
    delete_data(table)