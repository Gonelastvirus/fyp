If you pushed this DB publicly, change the admin password immediately inside your Flask app shell:
# Run Flask shell
flask shell

# Inside the shell
```bash
from models import db, User
admin = User.query.filter_by(email='admin@example.com').first()
admin.set_password('NewStrongPassword123!')
db.session.commit()
```
