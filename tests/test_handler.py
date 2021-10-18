from os import path, unlink
from datetime import date, datetime, time, timedelta
from app.handlers import get_schedule, is_workdate, append_extra_date, _read_extra_days
import json
import pytest
import settings


class TestHandler(object):

    @classmethod
    def setup_class(cls):

        # 通常カレンダー (2week)
        _filename = cls._get_test_json_filename()
        _file_contents = '{"statusCode": 200, "data": {"schedule": ' + cls._create_days() + '}}'
        with open(_filename, 'w') as f:
            f.write(_file_contents)

        # 予定外カレンダー (直近の土曜日)
        _filename = cls._get_test_json_filename().replace('_test', '_test_extra')
        _file_contents = '{"data": {"schedule": [{"date": "' + cls.holidays[0] + '", "holiday": "e"}]}}'
        with open(_filename, 'w') as f:
            f.write(_file_contents)

    @classmethod
    def teardown_class(cls):
        pass
        _filenames = (cls._get_test_json_filename(), cls._get_test_json_filename().replace('_test', '_test_extra'))
        for _f in _filenames:
            if path.exists(_f):
                unlink(_f)

    @classmethod
    def _get_test_json_filename(cls) -> str:
        """TEST用 JSON ファイル名

        Returns:
            (str): ファイル名フルパス
        """
        return path.join(settings.APP_PATH, 'data', 'calendar_test.json')

    @classmethod
    def _create_days(cls) -> str:
        cls.workdays = []
        cls.holidays = []

        _dates = cls._create_2weeks_datelist()

        _res = []
        for _date in _dates:
            _is_holiday = (datetime.strptime(_date, '%Y-%m-%d')).strftime('%a') in ('Sat', 'Sun')
            _res.append({"date": _date, 'holiday': '1' if _is_holiday else ''})

            if (_is_holiday):
                cls.holidays.append(_date)
            else:
                cls.workdays.append(_date)

        return json.dumps(_res)

    @classmethod
    def _create_2weeks_datelist(cls) -> tuple:
        d1 = date.today()
        d2 = date.today() + timedelta(14)

        _res = []
        for i in range((d2 - d1).days + 1):
            _res.append((d1 + timedelta(i)).isoformat())

        return tuple(_res)

    def test_JSONファイルを読み込んでdict変換_ファイルなし(self):
        with pytest.raises(FileNotFoundError):
            get_schedule('not_exists_filename')

        assert True

    def test_JSONファイルを読み込んでdict変換(self):

        try:
            _target = get_schedule('test')

            assert _target[self.workdays[0]] == ""
            assert _target[self.workdays[10]] == ""
            assert _target[self.holidays[1]] == "1"  # normal
            assert _target[self.holidays[0]] == "e"  # extra

        except FileNotFoundError as e:
            assert False

    def test_JSONファイルを読み込んで休日判定(self):

        try:
            assert is_workdate('test')
            assert is_workdate('test', self.workdays[0])
            assert is_workdate('test', self.workdays[10])
            assert is_workdate('test', self.holidays[1]) == False  # normal
            assert is_workdate('test', self.holidays[0])  # extra

        except FileNotFoundError as e:
            assert False

    def test_予定外日付を配列で取得(self):

        try:
            assert _read_extra_days('test') == tuple([self.holidays[0]])

        except FileNotFoundError as e:
            assert False

    def test_予定外日付を配列に追加と過去日除去(self):

        try:
            _old_date = '2021-10-10'
            _today = date.today().isoformat()
            _new_date1 = self.holidays[0]
            _new_date2 = self.holidays[1]

            append_extra_date('test', _old_date)  # 追加対象外
            append_extra_date('test', _today)     # 追加対象外
            append_extra_date('test', _new_date1)  # 対象
            append_extra_date('test', _new_date2)  # 対象

            assert _read_extra_days('test') == tuple([self.holidays[0], self.holidays[1]])

        except FileNotFoundError as e:
            assert False
