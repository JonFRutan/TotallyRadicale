#jfr
import psycopg2, csv, sys
from utils import DB as DB

# For future proofing we currently create user entities out of imported contacts (assuming they're exported from some employee database/spreadsheet)
# This creates a contact for every person listed in the user table.
def user_to_contact_sync():
    db_connection = psycopg2.connect(**DB)
    db_cursor = db_connection.cursor()
    db_cursor.execute("select display_name, email, phone from users;")
    rows = db_cursor.fetchall() #since we cursor.execute within the loop we need to get these out first
    synced = 0

    for row in rows:
        full_name = row[0]
        email = row[1]
        phone = row[2]

        db_cursor.execute("""
            insert into contacts (full_name, email, phone)
            values (%s, %s, %s)
            on conflict (full_name) do update set
                full_name = excluded.full_name,
                email = excluded.email,
                phone = excluded.phone
                returning id
        """, (full_name, email, phone))
        synced += 1

    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    print(f"{synced} users synced into contacts.")

# eventually I'd like this to be a subfunction for when a CSV is provided, not the sole import functionality
def import_from_csv(file_path):
    db_connection = psycopg2.connect(**DB)
    db_cursor = db_connection.cursor()

    with open(file_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        import_count = 0
        for row in reader:
            username = row['username']
            display_name = row['display_name']
            email = row['email']
            phone = row['phone']
            tags = [t.strip() for t in row.get('assigned_tags', '').split(',') if t.strip()]
            
            db_cursor.execute("""
                insert into users (username, display_name, email, phone)
                values (%s, %s, %s, %s)
                on conflict (username) do update set
                    display_name = excluded.display_name,
                    email = excluded.email,
                    phone = excluded.phone
                    returning id
            """, (username, display_name, email, phone))
            user_id = db_cursor.fetchone()[0]
            for tag in tags:
                db_cursor.execute("insert into groups (name) values (%s) on conflict do nothing", (tag,))
                db_cursor.execute("select id from groups where name = %s", (tag,))
                group_id = db_cursor.fetchone()[0]

                db_cursor.execute("""
                    insert into group_users (group_id, user_id)
                    values (%s, %s)
                    on conflict do nothing
                """, (group_id, user_id))
            import_count += 1
        
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        print(f"{import_count} users added to database.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Provide a filepath to a CSV file as an argument.")
        print("Usage: python import_users.py ./files/sample.csv")
        exit(1)
    import_from_csv(sys.argv[1])
    #user_to_contact_sync()
