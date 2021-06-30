from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from database.db import db
from database.models.access import Access
from database.models.authors import Author
from database.models.sessions import Session
from database.models.slugs import Slug

admin = Admin()

class PkModelView(ModelView):
    column_display_pk = True
    super(ModelView)

admin.add_view(PkModelView(Access, db.session))
admin.add_view(PkModelView(Author, db.session))
admin.add_view(PkModelView(Session, db.session))
admin.add_view(PkModelView(Slug, db.session))

