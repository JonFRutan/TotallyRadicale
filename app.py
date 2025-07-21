#jfr
import requests
from flask import Flask, render_template, request, redirect, url_for
import PythonScripts as cs

app = Flask(__name__)

#Needed pages: Index, Import, Export, View (for contacts and users)
#Import page needs: Importing from file (take filepath as upload)
#Export page needs: Exporting from DB into PostgreSQL
#View page needs: Iterate list of contacts / users (by group)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/import')
def import_to_db():
    return None

@app.route('/export')
def export_to_db():
    return None


if __name__ == '__main__':
    app.run(debug=True)