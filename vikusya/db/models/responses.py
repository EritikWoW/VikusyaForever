from vikusya.db.connection import get_connection
from vikusya.utils.logger import log_action, log_error

def insert_vikusya_response(response, context, source="manual"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO VikusyaResponses (Response, Source, Context)
        VALUES (%s, %s, %s) ON CONFLICT DO NOTHING RETURNING Id;
    """, (response, source, context))
    if cursor.fetchone():
        log_action(f"Добавила ответ Викуси: '{response}' (контекст: {context})", category="responses")
    conn.commit()
    cursor.close()
    conn.close()

def fetch_random_response(context, source="manual"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Response FROM VikusyaResponses
        WHERE Context = %s AND Source = %s
        ORDER BY RANDOM() LIMIT 1;
    """, (context, source))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None