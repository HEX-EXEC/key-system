import psycopg2

# Your connection string
conn_string = "dbname='tsdb' user='tsdbadmin' password='e0rkcyzda52cs58p' host='gf6h0nkxjq.ua5ytp4rwe.tsdb.cloud.timescale.com' port='39061' sslmode='require'"

try:
    # Connect to the database
    conn = psycopg2.connect(conn_string)
    print("Connected to the database successfully!")

    # Create a cursor to run queries
    cursor = conn.cursor()

    # Test with a simple query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Database version: {version}")

    # Clean up
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to the database: {e}")