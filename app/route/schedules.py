from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from logging import getLogger
import json
from app.handlers import get_schedule, get_scheduled_jobs, set_jobschedule, append_extra_date
from app.helpers import get_service_viewname, is_json
from .. import scheduler as app_scheduler

schedules = Blueprint('schedules', __name__)

HTTP_OK = 200
HTTP_BAD_REQUEST = 400


@schedules.after_request
def after_request(response):
    getLogger().info('%s %s %s %s %s', request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response


@schedules.route('/daylist', methods=['GET'])
def schedules_list() -> tuple:
    """ service schedule day list

    Returns: (tuple)
            ({ 
              statusCode: <http status code>,
              message: <response message>,
              data: {'schedules': {'chibasite': [{<date>: <holiday flug>}...], {'rsite': [{<date>: <holiday flug>}...]}}
            }, <http status code>)
    """
    _data = {}
    _data['chibasite'] = {'data': get_schedule('chibasite'), 'service_viewname': get_service_viewname('chibasite')}
    _data['rsite'] = {'data': get_schedule('rsite'), 'service_viewname': get_service_viewname('rsite')}
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": {"schedules": _data}}), HTTP_OK


@schedules.route('/joblist', methods=['GET'])
def jobs_list() -> tuple:
    """ service schedule job list

    Returns: (tuple)
            ({ 
              statusCode: <http status code>,
              message: <response message>,
              data: [{id: <job id>, func: <call function>, args: <function args>, next_run_at: <next execute date time>, trigger:<Any>}...]
            }, <http status code>)
    """

    _data = get_scheduled_jobs(app_scheduler)
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": _data}), HTTP_OK


@schedules.route('/jobs/reset', methods=['POST'])
@jwt_required()
def jobs_reload() -> tuple:
    """ JOB 再セットのみ

    Returns: (tuple)
            ({ 
              statusCode: <http status code>,
              message: <response message>,
              data: 
            }, <http status code>)
    """
    set_jobschedule(app_scheduler)

    _data = get_scheduled_jobs(app_scheduler)
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": _data}), HTTP_OK


@schedules.route('/booking/<servicename>', methods=['POST'])
@jwt_required()
def schedule_add_extra(servicename: str) -> tuple:
    """休出スケジュール追加

    Args:
        servicename (str): [description]

    Returns:
        tuple: [description]
    """
    if is_json(request.get_data()) == False:
        body = {'statusCode': HTTP_BAD_REQUEST, 'message': 'Request body is empty (require json key `date`)'}
        return jsonify(body), HTTP_BAD_REQUEST

    _request_body = json.loads(request.get_data())
    if not 'date' in _request_body.keys():
        body = {'statusCode': HTTP_BAD_REQUEST, 'message': 'Missing `date` value (YYYY-MM-DD) in request'}
        return jsonify(body), HTTP_BAD_REQUEST

    append_extra_date(servicename, _request_body['date'])

    _data = {}
    _data['chibasite'] = {'data': get_schedule('chibasite'), 'service_viewname': get_service_viewname('chibasite')}
    _data['rsite'] = {'data': get_schedule('rsite'), 'service_viewname': get_service_viewname('rsite')}
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": {"schedules": _data}}), HTTP_OK
