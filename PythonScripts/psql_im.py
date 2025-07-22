#jfr
import psycopg2, csv, sys
from utils import DB, RAD, clean_csv

# eventually I'd like this to be a subfunction for when a CSV is provided, not the sole import functionality
def import_users_from_csv(file_path, group=None):
    db_connection = psycopg2.connect(**DB)
    db_cursor = db_connection.cursor()
    if group is None:
        group = input("Enter groups associated with these contacts (comma-seperated): ").strip()
    group_names = [g.strip() for g in group.split(",") if g.strip()]
    group_ids = []

    for group_name in group_names:
        db_cursor.execute("""
        insert into groups (name) values (%s)
        on conflict do nothing
        """, (group_name,))
        db_cursor.execute("Select id from groups where name = %s", (group_name,))
        res = db_cursor.fetchone()
        if res:
            group_ids.append(res[0])

    csv_file = clean_csv(file_path)
    import_count = 0
    for row in csv_file:
        display_name = row['DisplayName'].split(",")[0].strip()
        phone = row['MobilePhone'].strip()
        title = row['JobTitle'].strip()
        email = row['Mail'].strip()
        username = display_name.replace(" ", ".")

        db_cursor.execute("""
            insert into users (username, display_name, email, phone, title)
            values (%s, %s, %s, %s, %s)
            on conflict (username) do update set
                display_name = excluded.display_name,
                email = excluded.email,
                phone = excluded.phone,
                title = excluded.title
                returning id
        """, (username, display_name, email, phone, title))
        user_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            insert into contacts (full_name, email, phone, title)
            values (%s, %s, %s, %s)
            on conflict (full_name) do update set
                full_name = excluded.full_name,
                email = excluded.email,
                phone = excluded.phone,
                title = excluded.title
                returning id
        """, (display_name, email, phone, title))
        contact_id = db_cursor.fetchone()[0]

        for group_id in group_ids:
            db_cursor.execute("""
            insert into group_contacts (group_id, contact_id)
            values (%s, %s)
            on conflict do nothing
            """, (group_id, contact_id))
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
    import_users_from_csv(sys.argv[1])
    #user_to_contact_sync()
