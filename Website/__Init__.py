from flask import Flask , url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from Website import oauth2

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    
    
    # Oauth GG
    
    from authlib.integrations.flask_client import OAuth

    oauth = OAuth(app)

    app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
    app.config['GOOGLE_CLIENT_ID'] = "792508167175-r46ddso1kj15qfm6pjbhjr8ldgk248bj.apps.googleusercontent.com"
    app.config['GOOGLE_CLIENT_SECRET'] = "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"


    google = oauth.register(
        name = 'google',
        client_id = app.config["GOOGLE_CLIENT_ID"],
        client_secret = app.config["GOOGLE_CLIENT_SECRET"],
        access_token_url = 'https://accounts.google.com/o/oauth2/token',
        access_token_params = None,
        authorize_url = 'https://accounts.google.com/o/oauth2/auth',
        authorize_params = None,
        api_base_url = 'https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
        client_kwargs = {'scope': 'openid email profile'},
        jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",
    )

    # Google login route
    @app.route('/login/google')
    def google_login():
        google = oauth.create_client('google')
        redirect_uri = url_for('google_authorize', _external=True)
        return google.authorize_redirect(redirect_uri)


    # Google authorize route
    @app.route('/login/google/authorize')
    def google_authorize():
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        resp = google.get('userinfo').json()
        print(f"\n{resp}\n")
        return "You are successfully signed in using google"

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')