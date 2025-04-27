from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_interaction(user_input, vikusya_answer, tags=None, rating=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Interactions (UserInput, VikusyaAnswer, Tags, Rating, Notes)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_input, vikusya_answer, tags, rating, notes))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_interactions(limit=10, tag_filter=None, date_from=None, date_to=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT Id, Timestamp, UserInput, VikusyaAnswer, Tags, Rating, Notes
    FROM Interactions
    WHERE 1=1
    """
    params = []

    if tag_filter:
        query += " AND Tags ILIKE %s"
        params.append(f"%{tag_filter}%")
    if date_from:
        query += " AND Timestamp >= %s"
        params.append(date_from)
    if date_to:
        query += " AND Timestamp <= %s"
        params.append(date_to)

    query += " ORDER BY Timestamp DESC LIMIT %s"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows