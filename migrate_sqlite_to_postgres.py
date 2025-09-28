#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL (Render/Linux-friendly, auto-generates schema).

Usage:
  python migrate_sqlite_to_postgres.py --sqlite data.db --postgres "postgres://user:pass@host:5432/dbname"
"""
import argparse
import sqlite3
import sys
import re

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("psycopg2 is required. Install psycopg2-binary.", file=sys.stderr)
    raise

def adapt_schema_for_postgres(create_stmt):
    """Convert SQLite CREATE TABLE statement to Postgres-compatible."""
    s = create_stmt
    s = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY', s, flags=re.I)
    s = re.sub(r'DATETIME DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP', s, flags=re.I)
    s = re.sub(r'PRAGMA foreign_keys = ON;', '', s, flags=re.I)
    return s

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", default="data.db")
    parser.add_argument("--postgres", required=True,
                        help="Postgres URL e.g. postgres://user:pass@host:5432/dbname")
    args = parser.parse_args()

    # Connect SQLite
    sqlite_conn = sqlite3.connect(args.sqlite)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # Connect Postgres
    try:
        pg = psycopg2.connect(args.postgres)
        pg.autocommit = False
        pgcur = pg.cursor()
    except Exception as e:
        print("Failed to connect to Postgres:", e, file=sys.stderr)
        sys.exit(1)

    # Fetch all table creation statements from SQLite
    sqlite_cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = sqlite_cur.fetchall()

    # Create tables in Postgres
    for table in tables:
        tname, create_sql = table
        pg_create_sql = adapt_schema_for_postgres(create_sql)
        try:
            print(f"Creating table {tname}...")
            pgcur.execute(pg_create_sql)
            pg.commit()
        except Exception as e:
            print(f"  Warning: failed to create table {tname}:", e)
            pg.rollback()

    # Copy data
    for table in tables:
        tname = table[0]
        print(f"Copying table {tname}...")
        rows = sqlite_cur.execute(f"SELECT * FROM {tname}").fetchall()
        if not rows:
            print("  no rows, skipping insert")
            continue

        cols = rows[0].keys()
        col_list = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        insert_sql = f"INSERT INTO {tname} ({col_list}) VALUES ({placeholders})"
        values = [tuple(r[c] for c in cols) for r in rows]

        try:
            pgcur.executemany(insert_sql, values)
            pg.commit()
            print(f"  {len(rows)} rows copied.")
        except Exception as e:
            print(f"  insert error for table {tname}:", e)
            pg.rollback()

    # Fix sequences for SERIAL columns
    for table in tables:
        tname = table[0]
        try:
            seq_sql = f"SELECT setval(pg_get_serial_sequence('{tname}', 'id'), COALESCE(MAX(id),0)) FROM {tname};"
            pgcur.execute(seq_sql)
            pg.commit()
        except Exception as e:
            # деякі таблиці можуть не мати id SERIAL, пропускаємо
            pass

    print("Migration complete. Verify data on Postgres.")
    sqlite_conn.close()
    pg.close()

if __name__ == '__main__':
    main()
