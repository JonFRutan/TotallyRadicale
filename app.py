#jfr
import requests
from flask import Flask, render_template, request, redirect, url_for
import PythonScripts

app = Flask(__name__)

#Needed pages: Index, Import, Export, View (for contacts and users)
#Import page needs: Importing from file (take filepath as upload)
#Export page needs: Exporting from DB into PostgreSQL
#View page needs: Iterate list of contacts / users (by group)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import', methods=["GET", "POST"])
def import_csv():
    if request.method == 'POST':
        file = request.files["file"]
        group = request.form["group"]
        filepath = f"/tmp/{file.filename}"
        file.save(filepath)
        import_users_from_csv(filepath, group)
        flash("Contacts imported successfully")
        return redirect("/")
    return render_template('import.html')

@app.route('/export', methods=["POST"])
def export_group():
    group = request.form["group"]
    addressbook = request.form["addressbook"]
    upload_group_to_radicale(group, addressbook)


if __name__ == '__main__':
    app.run(debug=True)