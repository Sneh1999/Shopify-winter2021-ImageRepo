import os

config = {
    "apiKey": os.environ.get('APIKEY'),
    "authDomain": os.environ.get('AUTH_DOMAIN'),
    "databaseURL": os.environ.get('DATABASE_URL'),
    "projectId": os.environ.get('PROJECT_ID'),
    "storageBucket": os.environ.get('STORAGE_BUCKET'),
    "messagingSenderId": os.environ.get('MESSAGING_SENDER_ID'),
    "appId": os.environ.get('APP_ID'),
    "measurementId": os.environ.get('MEASUREMENT_ID'),
    "serviceAccount" : "./key.json"
}