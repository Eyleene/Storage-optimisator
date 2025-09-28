
# Deploy to Render.com (Flask + Postgres)

Summary:
 - This repo supports running locally with SQLite (default).
 - To run on Render use a managed Postgres instance and set the `DATABASE_URL` env var.
 - The app will detect `DATABASE_URL` and use Postgres automatically.

Steps (minimal):

1. Create a new Web Service on Render linked to this repo or upload the project.
   - Build Command: (leave empty) or `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

2. Create a Render Postgres database (Dashboard -> New -> Postgres). Copy the DATABASE_URL provided.

3. In the Web Service's Environment, add an environment variable:
   - `DATABASE_URL` = the URL from the Postgres service (looks like `postgres://...`)

4. Initialize schema + migrate data:
   Option A (fresh start):
     - In your Render shell or locally, run the SQL in `schema.sql` adapted for Postgres.
     - Or run the included migration script **locally** to push existing `data.db` into Postgres:
       ```bash
       export DATABASE_URL="postgres://user:pass@host:port/dbname"
       python migrate_sqlite_to_postgres.py --sqlite data.db
       ```
   Option B (if you prefer to keep SQLite on Render):
     - Use a Render persistent disk and mount it. This repo does not include disk mount config.
     - Using Postgres is recommended on Render for persistence.

5. Deploy the Web Service. Render will use `gunicorn` to run the app.

Notes:
 - Render offers Free Web Services and Free Postgres instances. Free Postgres has storage limits (1 GB) and other limitations. See Render docs. 
 - SQLite files on ephemeral filesystems will not persist between deploys or restarts. Use Postgres for reliable persistence.
