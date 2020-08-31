import os
from config import db
from models import Images

# Delete database file if it  already exiata currently
if os.path.exists('user.db'):
    os.remove('user.db')

db.create_all()

db.session.commit()