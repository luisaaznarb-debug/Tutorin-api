import sqlite3

# Conectar a la base de datos existente
conn = sqlite3.connect("tutorin.db")
cursor = conn.cursor()

# Asegurar que la tabla sessions tenga la columna error_count
cursor.execute("PRAGMA table_info(sessions);")
columns = [col[1] for col in cursor.fetchall()]

if "error_count" not in columns:
    print("🛠️ Añadiendo columna 'error_count' a la tabla sessions...")
    cursor.execute("ALTER TABLE sessions ADD COLUMN error_count INTEGER DEFAULT 0;")
    conn.commit()
    print("✅ Columna añadida correctamente.")
else:
    print("👌 La columna 'error_count' ya existe.")

conn.close()
