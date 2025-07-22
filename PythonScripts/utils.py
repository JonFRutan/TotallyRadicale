#jfr
import os, socket, hashlib, uuid, requests, csv
from xml.etree import ElementTree as ET
from urllib.parse import urlparse
from dotenv import load_dotenv

#utils should also define a enum list to categorize the group IDs for use in the group_contacts/user tables

load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')

RAD_URLS=os.getenv('RAD_URLS')
RAD_USER=os.getenv('RAD_USER')
RAD_PASS=os.getenv('RAD_PASS')
RAD_ADDR=os.getenv('RAD_ADDR')
RAD_COMP=os.getenv('RAD_COMP')
RAD_CERT=os.getenv('RAD_CERT', "true").lower()

#FIXME - Rename these and combine them into one large dictionary
#dbuser, dbpass, dbhost, dbname | radhref, raduser, radpass, radaddr

group_ids = {
    'AD': 1,   #Admin
    'EN': 2,   #Engineering
    'HR' : 3,  #Human Resources
    'IT' : 4,  #Info Tech
    'SF': 5    #Safety
}

vcard_info = ["DisplayName", "JobTitle", "Mail", "MobilePhone"]
DB = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST
}

RAD = {
    "href": RAD_URLS,
    "user": RAD_USER,
    "password": RAD_PASS,
    "addressbook": RAD_ADDR, 
    "ca_cert": RAD_CERT,
    "company": RAD_COMP
}

#Deterministic UUID generation to avoid duplicate records in radicale
#NOTE: This is called in radicale_ex using emails as 'identifier'
def generate_uid(identifier: str) -> str:
    return str(uuid.UUID(hashlib.md5(identifier.encode()).hexdigest()))

#creates a session for put/finds
def create_session(username, password):
    session = requests.Session()
    session.auth = (username, password)
    return session

#finds and returns available addressbooks
def list_addressbooks(session, radicale_url, username):
    user_url = f"{radicale_url}/{username}/"
    headers = {
        "Depth": "1",
        "Content-Type": "application/xml"
    }

    data = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<d:propfind xmlns:d="DAV:">'
        '<d:prop><d:displayname/></d:prop>'
        '</d:propfind>'
    )

    try:
        resp = session.request("PROPFIND", user_url, headers=headers, data=data, verify=False)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching addressbooks: {e}")
        return []

    ns = {"d": "DAV:"}
    tree = ET.fromstring(resp.text)
    books = []

    for resp_elem in tree.findall("d:response", ns):
        href = resp_elem.find("d:href", ns)
        if href is not None:
            path = href.text.strip("/")
            if path and path != username:
                books.append(path.split("/")[-1])
    return books

#Checks if connection is on local machine to the radicale URL
#Used in radicale_ex
def is_local(radicale_url):
    host = urlparse(radicale_url).hostname
    local_ips = set()
    local_ips.add("127.0.0.1")
    local_ips.add("localhost")

    try:
        local_ips.update(ip[4][0] for ip in socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET))
    except socket.gaierror:
        pass
    return host in local_ips

#cleans a csv down to explicitly set fields in vcard_info (defined above)
def clean_csv(filepath):
    with open(filepath, newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        cleaned_csv = [{col: row[col] for col in vcard_info if col in row} for row in reader]
    return cleaned_csv