from os import environ
FLASK_ENV=environ.get("FLASK_ENV")
print(FLASK_ENV)