import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import config, Config
from database import Database
from forum_manager import ForumManager
from user_manager import UserManager
from content_manager import ContentManager
from ai_moderator import AIModeratorSystem
from search_discovery import SearchAndDiscoverySystem
from notification_system import NotificationSystem

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Telemedicine app startup')

    # Initialize database
    db = Database.get_instance()

    # Initialize all system components
    forum_manager = ForumManager(db)
    user_manager = UserManager(db)
    content_manager = ContentManager(db)
    ai_moderator = AIModeratorSystem(db)
    search_discovery = SearchAndDiscoverySystem(db)
    notification_system = NotificationSystem(db, {
        'server': Config.SMTP_SERVER,
        'port': Config.SMTP_PORT,
        'username': Config.SMTP_USERNAME,
        'password': Config.SMTP_PASSWORD
    }, Config.FIREBASE_CREDENTIALS)

## WE TAKE NOTE OF THIS:
    # Register blueprints (routes) here
    # from .api import api as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.close()

    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(debug=Config.DEBUG)
