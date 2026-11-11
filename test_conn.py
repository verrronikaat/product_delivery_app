import psycopg2
try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="delivery_db",
        user="appuser",
        password="apppassword"
    )
    print("Connection OK")
    conn.close()
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error args: {e.args}")