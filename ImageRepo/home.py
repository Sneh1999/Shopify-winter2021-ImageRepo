from flask import (Flask,render_template)

import connexion

#Create the application instance 
app = connexion.App(__name__, specification_dir='./',options={"swagger_ui": True})

app.add_api('swagger.yml')


#Create a url route in our application for "/"
@app.route('/')
def home():
    return render_template("home.htm")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


