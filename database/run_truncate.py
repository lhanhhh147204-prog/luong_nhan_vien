import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db_config
conn = db_config.get_db_connection()
cursor = conn.cursor()
cursor.execute('TRUNCATE NhanVien CASCADE')
conn.commit()
print("TRUNCATE done")
