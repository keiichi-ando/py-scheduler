from dotenv import load_dotenv
from os import path
from sys import path as syspath, argv as args, exit as sys_exit
import json
import logging.config

CLI_PATH = path.abspath(path.dirname(__file__))
APP_PATH = path.join(CLI_PATH, '..')
syspath.insert(0, CLI_PATH)
syspath.insert(0, APP_PATH)

load_dotenv()

# logger setup load
_logconfig = path.join(CLI_PATH, 'logconfig.json')
_json = json.loads(open(_logconfig, encoding='UTF-8').read())
logging.config.dictConfig(_json)
