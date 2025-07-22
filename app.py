#jfr
import os
from flask import Flask, render_template, request, redirect, url_for, flash

from PythonScripts.psql_im import import_users_from_csv
from PythonScripts.radicale_ex import upload_group_to_radicale
from PythonScripts.radicale_sync import sync_contacts
from PythonScripts.utils import RAD

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

#Needed pages: Index, Import, Export, View (for contacts and users)
#Import page needs: Importing from file (take filepath as upload)
#Export page needs: Exporting from DB into PostgreSQL
#View page needs: Iterate list of contacts / users (by group)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import', methods=["GET", "POST"])
def import_csv():
    """Upload a CSV of users and push them to Radicale."""
    if request.method == "POST":
        uploaded = request.files["file"]
        group = request.form.get("group", "")
        filepath = os.path.join("/tmp", uploaded.filename)
        uploaded.save(filepath)

        # Import into the database
        import_users_from_csv(filepath, group)

        # Push to the admin addressbook and sync to JAMF
        upload_group_to_radicale(group, RAD["addressbook"])
        sync_contacts()

        flash("Contacts imported and synced successfully")
        return redirect(url_for("index"))

    return render_template("import.html")

@app.route('/export', methods=["GET", "POST"])
def export_group():
    if request.method == "POST":
        group = request.form["group"]
        addressbook = request.form["addressbook"]
        upload_group_to_radicale(group, addressbook)
        flash("Group exported to Radicale")
        return redirect(url_for("index"))

    return render_template("export.html")


if __name__ == "__main__":
    app.run(debug=True)