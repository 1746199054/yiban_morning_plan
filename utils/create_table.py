from app import db
from models import Map, User, SignLog, ErrorLog

if __name__ == '__main__':
    db.create_all()
