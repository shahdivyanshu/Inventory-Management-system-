from Inventory import app
from .views import *


def set_urls():
    app.add_url_rule('/', 'home', view_func=home, methods = ['GET', 'POST'])
    app.add_url_rule('/login/', 'login', view_func=login)
    app.add_url_rule('/logout/', 'logout', view_func=logout)
    app.add_url_rule('/dashboard/', 'dashboard', view_func=dashboard)
    app.add_url_rule('/issue/', 'issue', view_func=issue, methods = ['GET', 'POST'])
    app.add_url_rule('/renew/', 'renew', view_func=renew, methods = ['GET', 'POST'])
    app.add_url_rule('/return_item/', 'return_item', view_func=return_item, methods = ['GET', 'POST'])
    app.add_url_rule('/account/', 'account', view_func=account)
    app.add_url_rule('/show_list/', 'show_list', view_func=show_list)
    app.add_url_rule('/admin/', 'admin', view_func=admin)
    app.add_url_rule('/reset_user/', 'reset_user', view_func=reset_user, methods = ['GET', 'POST'])
    app.add_url_rule('/accessCupboard/', 'accessCupboard', view_func=accessCupboard, methods = ['GET', 'POST'])
    app.add_url_rule('/lock_details/', 'lock_details', view_func=lock_details, methods = ['GET', 'POST'])


# Main function
if __name__ == "__main__":
    load_data()

    app.run(debug=True)