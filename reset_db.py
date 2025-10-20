import sqlite3

DB_PATH = "tutorin.db"  # 👈 asegúrate de que es el nombre de tu DB

def reset_sessions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Vaciar la tabla sessions
    cursor.execute("DELETE FROM sessions;")

    # Opcional: vaciar historial
    cursor.execute("DELETE FROM history;")

    conn.commit()
    conn.close()
    print("✅ Tablas 'sessions' y 'history' reseteadas.")

if __name__ == "__main__":
    reset_sessions()
