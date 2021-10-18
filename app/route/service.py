from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from logging import getLogger
from app.handlers import get_current_power_state, get_schedule, get_service_state, set_power_state, set_service_state
from app.route.auth import HTTP_BAD_REQUEST

service = Blueprint('service', __name__)

HTTP_OK = 200


@service.after_request
def after_request(response):
    getLogger().info('%s %s %s %s %s', request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response


@service.route('/state/<servicename>', methods=['GET'])
def service_status(servicename: str) -> tuple:
    """ service list

    Returns: 
        tuple:
            ({ 
              statusCode: <http status code>,
              message: <response message>,
              data: {'schedules': {'chibasite': {message: <status message>, 'statusCode': <target service response status code>}, {'rsite': ...}
            }, <http status code>)
    """
    _data = get_service_state(servicename)
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": {"status": _data}}), HTTP_OK


@service.route('/powerstate/<servicename>', methods=['GET'])
def power_status(servicename: str) -> tuple:
    """ server power status (use iDRAC)

    Returns: 
        tuple:
    """
    _data = get_current_power_state(servicename)
    return jsonify({"statusCode": HTTP_OK, "message": "success", "data": {"status": _data}}), HTTP_OK


@service.route('/up/<servicename>', methods=['POST'])
@jwt_required()
def up(servicename: str) -> tuple:
    """ service enable

    Args:
        servicename (str): target service

    Returns:
        tuple:
    """
    set_service_state(servicename, 'up')
    _data = get_service_state(servicename)
    return jsonify({"statusCode": _data['statusCode'], "message": _data['message'], "data": {"status": _data}}), HTTP_OK


@service.route('/down/<servicename>', methods=['POST'])
@jwt_required()
def down(servicename: str) -> tuple:
    """ service disable

    Args:
        servicename (str): target service

    Returns:
        tuple:
    """
    set_service_state(servicename, 'down')
    _data = get_service_state(servicename)
    return jsonify({"statusCode": _data['statusCode'], "message": _data['message'], "data": {"status": _data}}), HTTP_OK


@service.route('/poweron/<servicename>', methods=['POST'])
@jwt_required()
def poweron(servicename: str) -> tuple:
    """ server power on

    Args:
        servicename (str): target service

    Returns:
        tuple:
    """
    set_power_state(servicename)
    _data = get_current_power_state(servicename)
    return jsonify({"statusCode": _data['statusCode'], "message": _data['message'], "raw_response": _data}), HTTP_OK


@service.route('/poweroff/<servicename>', methods=['POST'])
@jwt_required()
def poweroff(servicename: str) -> tuple:
    """ server power trun off

    Args:
        servicename (str): target service

    Returns:
        tuple:
    """
    set_power_state(servicename, 'ForceOff')
    _data = get_current_power_state(servicename)
    return jsonify({"statusCode": _data['statusCode'], "message": _data['message'], "raw_response": _data}), HTTP_OK
