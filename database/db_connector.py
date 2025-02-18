import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, db


def initialize_db()-> db:
    """
    Initializes firebase realtime database and returns it's instance which
    can be used for querying
    """
    load_dotenv()
    _rtdb_configs = {
        "type": os.environ.get("RTDF_TYPE"),
        "auth_uri": os.environ.get("RTDB_AUTH_URI"),
        "client_id": os.environ.get("RTDB_CLIENT_ID"),
        "token_uri": os.environ.get("RTDB_TOKEN_URi"),
        "project_id": os.environ.get("RTDB_PROJECT_ID"),
        "private_key": os.environ.get("RTDB_PRIVATE_KEY"),
        "client_email": os.environ.get("RTDB_CLIENT_EMAIL"),
        "private_key_id": os.environ.get("RTDB_PRIVATE_KEY_ID"),
        "auth_provider_x509_cert_url": os.environ.get(
            "RTDB_AUTH_PROVIDER_X509_CERT_URL"
        ),
        "universe_domain": os.environ.get("RTDB_UNIVERSE_DOMAIN"),
        "client_x509_cert_url": os.environ.get("RTDB_CLIENT_X509_CERT_URL"),
    }
    db_url = os.environ.get("RTDB_URL")
    cred = credentials.Certificate(_rtdb_configs)
    initialize_app(cred, {
        "databaseURL": f"{db_url}/"
    })
    return db
