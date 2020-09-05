from flask import (Flask,render_template)
import connexion
import json
import os
from dotenv import load_dotenv

load_dotenv()

key_dict = {
    "type": os.environ.get('TYPE'),
    "project_id": os.environ.get('PROJECT_ID'),
    "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
    "private_key": os.environ.get('PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('CLIENT_EMAIL'),
    "client_id": os.environ.get('CLIENT_ID'),
    "auth_uri": os.environ.get('AUTH_URI'),
    "token_uri": os.environ.get('TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.environ.get('CLIENT_X509_CERT_URL')
}



with open('./key.json', 'w') as json_file:
  json.dump(key_dict, json_file)
#Create the application instance 
app = connexion.App(__name__, specification_dir='./',options={"swagger_ui": True})

app.add_api('swagger.yml')


app.app.config['SECRET_KEY'] =  'thisisasecretkey'
#Create a url route in our application for "/"

@app.route('/')
def home():
    return render_template("home.htm")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


