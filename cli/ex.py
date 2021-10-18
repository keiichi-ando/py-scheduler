#!/usr/bin/env python
from sys import argv as args, exit as sys_exit
from logging import getLogger
import settings

from app.handlers import fetch_json, fetch_json, service_enable, get_current_power_state, get_service_state
from app.helpers import post_alert


if __name__ == '__main__':

    _tag = 'その他'
    _command = ''

    if not len(args) != 2:
        print('引数を指定してください  ex.py <service_name> <command>(update, poweron, up, down...)')
        sys_exit(1)

    try:
        _target = args[1]
        _command = args[2]

        # カレンダー更新
        if _command == 'update':
            _tag = 'スケジュール取得'

            fetch_json(_target)

        if _command in ('up', 'down', 'poweron'):
            _tag = f'サービス状態変更 {_command}'
            service_enable(_target, _command)

    except (Exception) as e:
        getLogger().error(f'{_tag}エラー: {e}', )
        post_alert(f'{_tag}エラー', f'{e}')
