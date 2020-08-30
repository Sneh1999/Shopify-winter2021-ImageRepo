import os
from config import db
from models import Images

# Delete database file if it  already exiata currently
if os.path.exists('image.db'):
    os.remove('image.db')

db.create_all()

db.session.commit()