#jfr
import vobject, psycopg2, requests, uuid
from utils import DB, RAD, is_local, generate_uid, list_addressbooks, create_session

#export vcards into a single file, for use in payload.
def export_vcards(cards, filepath):
    count = 0
    with open(filepath, 'w', encoding='utf-8') as o:
        for card in cards:
            o.write(f"{card.serialize()}")
            count += 1
    print(f"{filepath} created with {count} vCards.")

#takes all the records found in the contacts table and generates vcards out of them.
def generate_vcards(group):
    cards = []
    db_connection = psycopg2.connect(**DB)
    db_cursor = db_connection.cursor()

    db_cursor.execute("""
    select full_name, email, phone, title from contacts c
    join group_contacts gc on c.id = gc.contact_id
    join groups g on gc.group_id = g.id
    where g.name = %s
    """, (group,))
    #the cursor object is iterable, so we can iterate through retrieved records.
    for full_name, email, phone, title in db_cursor:
        vcard = vobject.vCard()

        vcard.add('fn') # full name - 'fn' attribute is required by vobject
        vcard.fn.value = full_name

        vcard.add('n')  # username
        vcard.n.value = vobject.vcard.Name(family='', given=full_name)

        uid_field = vcard.add('uid')
        uid_field.value = generate_uid(email)

        email_field = vcard.add('email')
        email_field.value = email
        email_field.type_param = 'INTERNET'

        tel_field = vcard.add('tel')
        tel_field.value = phone
        tel_field.type_param='WORK'

        if title:
            title_field = vcard.add('title')
            title_field.value = title

        cards.append(vcard)
        #vcard.serialize()
        #vcard.prettyPrint()
    db_cursor.close()
    db_connection.close()

    #print("Exporting vcards to output.vcf")
    #export_vcards(cards)
    return cards

def upload_card_to_radicale(session, radicale_url, username, addressbook, vcard):
    vcard_file = f"{vcard.uid.value}.vcf"
    contact_url = f"{radicale_url}/{username}/{addressbook}/{vcard_file}"
    headers = {
        "Content-Type": "text/vcard"
    }
    vcard_content = vcard.serialize()
    #FIXME: In session.put verify is set to 'False', this should be changed if these scripts are used somewhere other than the server.
    try:
        response = session.put(contact_url, headers=headers, data=vcard_content, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error uploading: {e}")

def upload_group_to_radicale(group, addressbook):
    session = create_session(RAD["user"], RAD["password"])
    upload_to_radicale(RAD["href"], RAD["user"], RAD["password"], addressbook, RAD["ca_cert"], group, session)

def upload_to_radicale(radicale_url, radicale_username, radicale_password, addressbook, ca_cert, group, session=None):
    if session is None:
        session = create_session(RAD["user"], RAD["password"])
        session.auth = (radicale_username, radicale_password)
        if is_local(radicale_url):
            session.verify = False
        elif ca_cert == "false":
            session.verify = False
        elif ca_cert == "true":
            session.verify = True
        else:
            session.verify = ca_cert

    cards = generate_vcards(group)
    if not cards:
        print("Error at contact card creation")
        return
    for card in cards:
        upload_card_to_radicale(session, radicale_url, radicale_username, addressbook, card) # This is no good

if __name__ == "__main__":
    #print(RAD)
    session = create_session(RAD["user"], RAD["password"])
    addressbook = None
    results = list_addressbooks(session, RAD["href"], RAD["user"])
    while addressbook not in results:
        addressbook = input(f"Choose an addressbook: {results}: ")
    group = input("Type in the group you want to upload: ")
    upload_to_radicale(RAD["href"], RAD["user"], RAD["password"], addressbook, RAD["ca_cert"], group, session)
