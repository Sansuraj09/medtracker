import os
from dotenv import load_dotenv

load_dotenv()

pwd = os.environ.get('MYSQL_PASSWORD')
print(f"Password value: '{pwd}'")
print(f"Password length: {len(pwd) if pwd else 0}")
print(f"Password bytes: {pwd.encode() if pwd else 'None'}")
