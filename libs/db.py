import sqlite3

def get_data(db_path:str, SQL_request:str, params: tuple = ()):
    """Get data from database

    Args:
        db_path (str): Database path
        SQL_request (str): SQL request for get data
        params (tuple, optional): Params for request. Defaults to ().

    Raises:
        Exception: if error in cursor.execute(SQL_request, params)

    Returns:
        if data != None:
            return data[0]
        else:
            return None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(SQL_request, params)
    except sqlite3.Error as e:
        raise Exception(f"Error in executing SQL: {e}")
    
    row = cursor.fetchone()
    conn.close()
    if row != None:
        return row[0]
    else:
        return None

def execute_request(db_path:str, SQL_request:str, params: tuple = ()):
    """Execute SQL

    Args:
        db_path (str): Database path
        SQL_request (str): SQL request for execute and commit data
        params (tuple, optional): Params for request. Defaults to ().

    Raises:
        Exception: if error in cursor.execute(SQL_request, params)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(SQL_request, params)
        conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"Error in executing SQl: {e}")
    finally:
        conn.close()

