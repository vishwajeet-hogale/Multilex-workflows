"""
AIM:    To convert yyyy-mm-dd h-m-s to yyyy-mm-dd
"""

# importing datetime and (db.py from local directory)
from datetime import datetime
from UpdateDatabaseWF import db

"""
correct_publish_date(date):     

In:     date >> string object
Out:    string object    


setup_connection():
In:     None
Out:    connection to DB object

update_table(table_name, field, where, cursor):
In:     Table Name, field tuple (set field vale to x in format (field Name, x)), where statementm, cursor object
Out:    None

select(col, from_, where, cursor):
In:     columns name to be selected, from table name, where clause, cursor object
Out:    returns Cursor data

main() -> updates the date, takes value from scraped_date and formats it and places it in publish_date
returns None
"""


# Function To return correct string
def correct_publish_date(date):
    # if time has ':' in b/w hour and min replace "-" with ":"
    date_Obj = datetime.strptime(date, "%Y-%m-%d %H-%M-%S")
    date_str = datetime.strftime(date_Obj, "%Y-%m-%d")
    return date_str


# Update Table SQl query
def update_table(table_name, field, where, cursor):

    sqlQuery = f"""

    UPDATE {table_name} SET {field[0]} = '{field[1]}'
    {where};

    """
    cursor.execute(sqlQuery)
    return


# Select from SQL query
def select(col, from_, where, cursor):

    sqlQuery = f"""
    SELECT {col} FROM TABLE {from_}
    {where};
    """
    cursor.execute(sqlQuery)
    return cursor


# Main Func
def main():
    """
    sets up conn and cursor,
    gets Number of entries
    updates the each field at specified id
    """
    conn = db.setup_connection()
    cursor = conn.cursor()

    no_entry = select("COUNT(*)", "Multilex", "", cursor)

    for idNo in range(1, no_entry + 1):
        date = select("scraped_date", "Multilex", f"WHERE id = {idNo}")
        date_corrected = correct_publish_date(date)
        update_table(
            "Multilex", ("publish_date", date_corrected), f"WHERE id = {idNo}", cursor
        )

    cursor.close()
    conn.close()
    print("Finished Update")
    exit(0)


if __name__ == "__main__":
    main()
