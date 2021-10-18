from os import path, getenv
from datetime import date
from logging import getLogger
import json
import requests
import settings

from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers import post_alert, serialize_job, get_service_viewname


def set_jobschedule(app_scheduler: BackgroundScheduler) -> None:
    """ 基本スケジュールをセット
    """
    app_scheduler.remove_all_jobs()
    _jobs = _get_jobs()
    for _j in _jobs:
        app_scheduler.add_job(eval(_j['func']), _j['trigger'], args=_j['args'], hour=_j['hour'], minute=_j['minute'], id=_j['id'])


def get_scheduled_jobs(app_scheduler: BackgroundScheduler) -> tuple:
    """セットした JOB を配列で取得

    Args:
        app_scheduler (BackgroundScheduler): [description]

    Returns:
        tuple
    """
    _jobs = app_scheduler.get_jobs()
    _data = []
    for _job in _jobs:
        _data.append(serialize_job(_job))

    return tuple(_data)


def log_scheduled_jobs(app_scheduler: BackgroundScheduler) -> None:
    """セットした JOB をログに出力 (app 起動時の確認用)

    Args:
        app_scheduler (BackgroundScheduler): [description]
    """
    _jobs = get_scheduled_jobs(app_scheduler)
    for _job in _jobs:
        getLogger().info(f'scheduled job: {str(_job)}')


def service_enable(service_name: str, method: str) -> None:
    """ scheduler entry-point : サービス状態変更 (スケジュール実行用)

    Args:
        service_name (str): target service
        method (str): (up|down|poweron)

    Return:
        void

    """
    # 休業日は実行しない
    if is_workdate(service_name) == False:
        getLogger().info(f'<{service_name}> Service enable has been discontinued. Not a working day!')
        return

    getLogger().info(f'<{service_name}> Service enable execute. {method}')

    if method == 'poweron':
        return set_power_state(service_name)

    return set_service_state(service_name, method)


def get_service_state(service_name: str) -> dict:
    """ WebApp サービス状態を取得

    Args:
        service_name (str): target service

    Raises:
        Exception: [description]

    Returns:
        dist: {'statusCode': xxx, 'message': xxx}
    """
    _host = _get_service_host(service_name)
    _res = requests.get(f'http://{_host}/status')
    response = _res.json()
    response['service_name'] = service_name
    response['service_viewname'] = get_service_viewname(service_name)
    return response


def set_service_state(service_name: str, method: str) -> None:
    """ WebApp サービス状態の変更

    Args:
        service_name (str): target service
        method (str): up/down

    Raises:
        Exception: [description]
    """
    _host = _get_service_host(service_name)
    if (_host == '' or not method in ('up', 'down')):
        raise Exception(f'<{service_name}> 未対応 url:"{_host}/{method}"')

    response = requests.get(f'http://{_host}/{method}')
    _code = response.status_code
    getLogger().info(f'<{service_name}> url: {_host}/{method}, {_code}: {response.text}')


def get_current_power_state(service_name: str) -> dict:
    """REDFISH service state get

    refs: https://github.com/dell/iDRAC-Redfish-Scripting

    Args:
        service_name (str): target service

    Returns:
        dict: {'statusCode': xxx, 'message': xxx}
    """
    _idrac_ip = _get_idrac_host(service_name)
    response = requests.get(f'https://{_idrac_ip}/redfish/v1/Systems/System.Embedded.1/', verify=False, auth=_get_idrac_user())
    data = response.json()
    return {'statusCode': response.status_code, 'message': f'PowerState: {data[u"PowerState"]}'}


def set_power_state(service_name: str, state_to: str = 'On') -> None:
    """ REDFISH service state set (change state_to)

    refs: https://github.com/dell/iDRAC-Redfish-Scripting

    Args:
        service_name (str): target service
        state_to (str): status change to ( On | ForceOff )
    """
    _idrac_ip = _get_idrac_host(service_name)
    if (_idrac_ip == '' or not state_to in ('On')):
        raise Exception(f'<{service_name}> 未対応 url:"{_idrac_ip}/{state_to}"')

    # response = requests.get(f'https://{_idrac_ip}/redfish/v1/Systems/System.Embedded.1/', verify=False, auth=_get_idrac_user())
    # data = response.json()
    getLogger().info(f"- WARNING, setting new server power state to: {state_to}")

    url = f'https://{_idrac_ip}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset'
    payload = {'ResetType': state_to}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, auth=_get_idrac_user())

    statusCode = response.status_code
    if statusCode == 204:
        getLogger().info(f'- PASS, status code {statusCode} returned, server power state successfully set to "{state_to}"')
    else:
        getLogger().info(f'- FAIL, Command failed, status code {statusCode} returned: {response.text}')


def get_schedule(service_name: str) -> dict:
    """スケジュールdict を作成 

    Args:
        service_name (str): target service

    Raises:
        FileNotFoundError: calendar_<service_name>.json ファイルが見つからない

    Returns:
        dict: {KEY: 日付 Y-m-d, VALUE: 休日フラグ blank=営業日 1=休業日 e=予定外}
    """

    _schedule = {}

    # 通常カレンダーを読み込み
    _filename = _get_json_filename(service_name)
    if path.exists(_filename) == False:
        raise FileNotFoundError(f'<{service_name}> json file not found: {_filename}')

    _file_contents = json.loads(open(_filename, encoding='UTF-8').read())
    for _d in _file_contents['data']['schedule']:
        _schedule[_d['date']] = _d['holiday']

    # 予定外ファイルがあるときは休日フラグを上書き
    _filename = _get_extra_json_filename(service_name)
    if path.exists(_filename):
        _file_contents = json.loads(open(_filename, encoding='UTF-8').read())
        for _d in _file_contents['data']['schedule']:
            if _d['date'] in _schedule:
                _schedule[_d['date']] = _d['holiday']

    return _schedule


def fetch_json(service_name: str) -> None:
    """ scheduler entry-point : スケジュールファイルの更新 (remote -> local file)

    Args:
        service_name (str): target service

    Raises:
        Exception: 引数NG
        Exception: リモート通信エラー
    """
    try:
        _filename = _get_json_filename(service_name)
        _host = _get_service_host(service_name)
        if (not _host or not _filename):
            raise Exception(f'<{service_name}> fetch_json() 引数指定エラー host: "{_host}", file: "{_filename}"')

        # 休業日は実施しない
        if (path.exists(_filename)):
            if is_workdate(service_name) == False:
                getLogger().info(f'<{service_name}> Calendar fetch abort. Not workday!')
                return

        getLogger().info(f'<{service_name}> Calendar fetch: {_host}')

        res = requests.get(f'http://{_host}/api/v1/calendar/schedule/2weeks/')
        if res.status_code != requests.codes.ok:
            raise Exception(f'<{service_name}> {_host} [{res.status_code}] {res.text}')

        _schedule_json = json.loads(res.text)
        with open(_filename, 'w') as f:
            json.dump(_schedule_json, f)

        getLogger().info(f'<{service_name}> Calendar file update: {_filename}')

    except (Exception) as e:
        getLogger().error(f'JSON スケジュール取得エラー: {e}', )
        post_alert(f'JSON スケジュール取得エラー', f'{e}')


def append_extra_date(service_name: str, append_date: str) -> None:
    """ 計画外予約 (本日より先の日付)

    Args:
        service_name (str): target service
        append_date (str): isoformat date YYYY-MM-DD
    """
    _newdata = {}
    _today = date.today().isoformat()
    _current = _read_extra_days(service_name)

    # dict化して日付重複なしにする、本日以前は追加しない
    for _date in _current:
        if _date > _today:
            _newdata[_date] = 'e'
    if append_date > _today:
        _newdata[append_date] = 'e'

    _res = []
    for _k in _newdata.keys():
        _res.append({"date": _k, "holiday": _newdata[_k]})

    _filename = _get_extra_json_filename(service_name)
    with open(_filename, 'w') as f:
        json.dump({"data": {"schedule": _res}}, f)


def is_workdate(service_name: str, workdate: str = '') -> bool:
    """ 稼働日判定 (本日)

    Args:
        service_name (str): target service
        workdate (str): optional 確認する日付け Y-m-d
    Return:
        bool True:稼働日 / False:休業日
    """
    _mydate = date.today().isoformat() if workdate == '' else workdate
    _schedule = get_schedule(service_name)

    if _mydate in _schedule.keys():
        return _schedule[_mydate] != '1'

    return False


def get_all_users() -> dict:
    """認証用ユーザーデータ取得

    Returns:
        dict: [description]
    """
    _filename = path.abspath(path.join(settings.APP_PATH, 'data', f'users.json'))
    if path.exists(_filename) == False:
        return {}
    return json.loads(open(_filename, encoding='UTF-8').read())['data']


def _get_jobs() -> dict:
    _dict = json.loads(open(_get_jobs_json_filename(), encoding='UTF-8').read())
    return _dict['jobs']


def _get_jobs_json_filename() -> str:
    return path.abspath(path.join(settings.APP_PATH, 'data', f'jobs.json'))


def _get_json_filename(service_name: str) -> str:
    return path.abspath(path.join(settings.APP_PATH, 'data', f'calendar_{service_name}.json'))


def _get_extra_json_filename(service_name: str) -> str:
    return path.abspath(path.join(settings.APP_PATH, 'data', f'calendar_{service_name}_extra.json'))


def _get_service_host(service_name: str) -> str:
    if service_name == 'rsite':
        return getenv('RSITE_SERVICE_HOST', '')
    if service_name == 'chibasite':
        return getenv('CHBSITE_SERVICE_HOST', '')

    return ''


def _get_idrac_host(service_name: str) -> str:
    if service_name == 'rsite':
        return getenv('RSITE_IDRAC_HOST', '')
    if service_name == 'chibasite':
        return getenv('CHBSITE_IDRAC_HOST', '')

    return ''


def _get_idrac_user() -> tuple:
    _idrac_username = 'root'
    _idrac_password = 'calvin'
    return (_idrac_username, _idrac_password)


def _read_extra_days(service_name: str) -> tuple:
    _res = []

    _filename = _get_extra_json_filename(service_name)
    if path.exists(_filename):
        _file_contents = json.loads(open(_filename, encoding='UTF-8').read())
        for _d in _file_contents['data']['schedule']:
            if (_d['date'] != ''):
                _res.append(_d['date'])

    return tuple(_res)
