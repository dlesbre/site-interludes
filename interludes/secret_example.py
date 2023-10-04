# Secrets that must be changed in production

SECRET_KEY = "i*4$=*fa(644(*!9m2)0-*&sows2uz$b^brb(=)elfn3+y6#1n"

# List of ("name", "email") people who get server notifications:
# errors, new activities submitted, mass email sent
ADMINS = [
    ("superuser", "superuser@admin.fr"),
]

DB_NAME = "db.sqlite3"

SERVER_EMAIL = "root@localhost"
DEFAULT_FROM_EMAIL = "webmaster@localhost"
EMAIL_HOST = "localhost"
EMAIL_PORT = 587
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
