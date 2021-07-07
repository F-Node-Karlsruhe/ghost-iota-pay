from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_basicauth import BasicAuth
from flask_admin.contrib.sqla import ModelView
from database import db
from database.models.access import Access
from database.models.authors import Author
from database.models.slugs import Slug


class AuthenticatedAdminView(AdminIndexView):

    def is_accessible(self):
        if not auth.authenticate():
            return False
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return auth.challenge()

    super(AdminIndexView)


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        if not auth.authenticate():
            return False
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return auth.challenge()

    super(ModelView)

class HomeView(BaseView):
    @expose('/')
    def index(self):
        arg1 = 'Hello'
        return self.render('admin/myhome.html', arg1=arg1)


class PkModelView(AuthenticatedModelView):
    column_display_pk = True

    super(AuthenticatedModelView)


admin = Admin(index_view=AuthenticatedAdminView(), template_mode='bootstrap4')
auth = BasicAuth()

admin.add_view(PkModelView(Access, db.session, name='Access', category='Database'))
admin.add_view(PkModelView(Author, db.session, name='Authors', category='Database'))
admin.add_view(PkModelView(Slug, db.session, name='Posts', category='Database'))
