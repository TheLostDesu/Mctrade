from app.models import User
from app import db
import flask


flask db migrate -m "users table"

u = User(username='susan', email='susan@example.com')
print(u)
db.session.add(u)
db.session.commit()
