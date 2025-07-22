#jfr
import sys, os, shutil
from datetime import datetime
#from utils import DB, RAD

RADICALE_STORAGE = "/var/lib/radicale/collections/collection-root"
ADMIN_BOOK = os.path.join(RADICALE_STORAGE, "adminuser", "super")
JAMF_BOOK = os.path.join(RADICALE_STORAGE, "jamfuser", "super")

def sync_contacts():
    if not os.path.isdir(ADMIN_BOOK):
        print(f"[Error] File {ADMIN_BOOK} not found.")
        return
    os.makedirs(os.path.dirname(JAMF_BOOK), exist_ok=True)

    if os.path.exists(JAMF_BOOK):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{JAMF_BOOK}.bak-{timestamp}"
        shutil.move(JAMF_BOOK, backup_path)
        print(f"[INFO] Existing jamfuser/super backed up to: {backup_path}")

    shutil.copytree(ADMIN_BOOK, JAMF_BOOK)
    print(f"Admin -> Jamf Sync Successful")

if __name__ == "__main__":
    sync_contacts()