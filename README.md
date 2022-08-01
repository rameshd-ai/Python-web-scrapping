# Prerequisites
1. change the secret_key inside the main_file.py
    a. you can use the following python script to generate a secret_key:
        import os
        os.urandom(12).hex()
2. configure the database:
    a. Change these parameters inside the main_file.py:
        MYSQL_HOST
        MYSQL_USER
        MYSQL_PASSWORD
        MYSQL_DB

        
# Installation
1. Create a virtual environment and activate it
2. Run the following command:
    pip3 install -r requirements.txt
3. Run server:
    python3 main_file.py
4. Open the browser and go to 0.0.0.0:8000