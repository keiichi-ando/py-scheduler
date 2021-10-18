from os import path, makedirs, getenv
import errno
import json
import logging
import logging.handlers
from logging import getLogger
import settings
import requests
from apscheduler.job import Job


class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """App log を app_path/log(sub folder)に出力するための wrapper class

    Args:
        logging (logging.handlers.TimedRotatingFileHandler): [description]
    """

    def __init__(self, filename, *args, **kwargs):
        _logfile = path.join(settings.APP_PATH, 'log', str(path.basename(filename)))
        self.mkdir_p(path.dirname(_logfile))
        super().__init__(_logfile, *args, **kwargs)

    def mkdir_p(self, path):
        """http://stackoverflow.com/a/600612/190597 (tzot)"""
        try:
            makedirs(path, mode=0o777, exist_ok=True)  # Python>3.2
        except TypeError:
            try:
                makedirs(path)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and path.isdir(path):
                    pass
                else:
                    raise


def post_alert(title: str, message: str = '') -> None:
    """アラートをRocket.Chatに投稿

    Args:
        title (str): [投稿メッセージ]
        message (str): [投稿詳細]
    """
    _url = getenv('RCHAT_WEBHOOK_URL', '')
    if (_url == ''):
        getLogger().warn('environ RCHAT_WEBHOOK_URL not exists or empty value')
        return

    _color = '#E11345'
    _data = {"alias": f"({getenv('RCHAT_WEBHOOK_NAME', '')})", "text": title}
    if (message):
        _detail = {'attachments': [{'text': message, 'color': _color}]}
        _data.update(**_detail)

    response = requests.post(_url, json.dumps(_data), headers={'Content-Type': 'application/json'})
    if (response.ok):
        getLogger().debug(f'rocketchat post alert [ok], {response.text}')
    else:
        getLogger().debug(f'rocketchat post alert [fail], {response.raise_for_status()} : {message}')


def serialize_job(job: Job) -> dict:
    """ schedule job を dict へ変換 

    Args:
        job (apscheduler.job.Job): job

    Returns:
        dict: {id, func, args, next_run_at, trigger}
    """
    return {"id": job.id, "func": job.func_ref, "args": job.args, "next_run_at": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'), "trigger": str(job.trigger)}


def is_json(request_body) -> bool:
    """ JSON形式のデータ判定 (for http request)

    Args:
        myjson (): 

    Returns:
        bool: 
    """
    try:
        _ = json.loads(request_body)
    except ValueError as e:
        return False
    return True


def get_service_viewname(servicename: str) -> str:
    """サービスの表示名

    Args:
        servicename (str): [description]

    Returns:
        str: [description]
    """
    if servicename in ('rsite'):
        return 'r site'
    if servicename in ('chibasite'):
        if (getenv('CHBSITE_SERVICE_HOST', '').startswith('192.168.12.')):
            return 'gifu site'
        return 'chiba site'

    return servicename
