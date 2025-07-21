#jfr
import os, socket, hashlib, uuid, requests
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
    "ca_cert": RAD_CERT
}

#Deterministic UUID generation to avoid duplicates
def generate_uid(identifier: str) -> str:
    return str(uuid.UUID(hashlib.md5(identifier.encode()).hexdigest()))

#creates a session for put/finds or whatever else
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