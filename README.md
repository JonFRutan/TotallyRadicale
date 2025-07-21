# TotallyRadicale  
Contact management scripts for joining together a PostgreSQL database and a [Radicale](https://radicale.org/v3.html) server.  
Included within the project are all necessary Python requirements, which includes Radicale.  
The ultimate goal is for this to be a "batteries included" CardDAV system eventually allowing for dynamic mass imports, syncing, and Radicale exporting. It's far from complete; my first and foremost goal is to curtail it to my use case, and then eventually smooth out the whole process.  

## Requirements  
- **Python**  
- **PostgreSQL**  

Python libraries will be managed using a virtual environment.  

## Setup  
In the project root type `make` and the Makefile will set up the virtual environment, install requirements, and run the database initialization script.  
Within your server you will need to create a contacts_db admin user, remember to give it privileges to your contacts database using the psql command:  
 `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC TO contacts_admin;`  
Fill out a local .env file with the needed database and login information.  

These setups are not yet complete, and you will run into errors using them.  
  
## Goals    
- Structure a database schema for managing users and contacts. **(Done)**   
- Take in a CSV and populate our database. **(Done)**   
- Using the local contacts table, generate a set of vCard from it. **(Done)**  
- Set up an export script to Radicale using the generated vCards.  **(Done)**  
- Create a Flask frontend for easier access to functionality and data administration.  
- Redefine setup scripts to be universal and complete.
- Redesign import system for more flexible CSV (Or other) -> Postgres.  
- Redesign export system for more powerful Radicale integration.

