import os
import psycopg2

def get_db_connection():
    conn_str = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres.yhjnczndmoaabhotgqmh:Hoanganh147204@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
    )
    return psycopg2.connect(conn_str)
