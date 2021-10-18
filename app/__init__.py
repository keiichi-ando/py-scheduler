from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from os import path, getenv
from datetime import timedelta
from logging import getLogger
import logging.config
import json

from apscheduler.schedulers.background import BackgroundScheduler
from app.handlers import set_jobschedule, log_scheduled_jobs
from app.route.auth import jwt_unauthorized_loader_handler

# scheduler
scheduler = BackgroundScheduler(daemon=True)
set_jobschedule(scheduler)
scheduler.start()


def create_app():

    # logger setup load
    _logconfig = path.join(path.abspath(path.dirname(__file__)), 'logconfig.json')
    _json = json.loads(open(_logconfig, encoding='UTF-8').read())
    logging.config.dictConfig(_json)

    app = Flask(__name__, static_folder='../src/dist/static')

    app.secret_key = getenv('SEACRET_KEY', '')
    app.config['JSON_AS_ASCII'] = False
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=300)

    CORS(app)

    jwt = JWTManager(app)
    jwt.unauthorized_loader(jwt_unauthorized_loader_handler)

    # blueprint for auth routes in our app
    from .route.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api')

    # blueprint for frontend
    from .route.http import http as http_blueprint
    app.register_blueprint(http_blueprint)

    # blueprint for non-auth parts of app
    from .route.service import service as service_blueprint
    app.register_blueprint(service_blueprint, url_prefix='/api/service')

    # blueprint for non-auth parts of app
    from .route.schedules import schedules as scheduler_blueprint
    app.register_blueprint(scheduler_blueprint, url_prefix='/api/schedules')

    # scheduler
    log_scheduled_jobs(scheduler)

    return app
