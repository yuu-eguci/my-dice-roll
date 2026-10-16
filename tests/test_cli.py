import os
import subprocess
import sys
from pathlib import Path

import pytest

import MyDiceRoll


def test_arguments_print_result_without_window(capsys, monkeypatch):
    monkeypatch.setattr(MyDiceRoll.random, 'randint', lambda a, b: b)
    monkeypatch.setattr(MyDiceRoll.tk, 'Tk', None)
    assert MyDiceRoll.main(['2d3', '-1d2', '5']) == 0
    assert capsys.readouterr().out == '(ｺﾛｺﾛﾘﾝ…) 2d3 -1d2 5: 9\n(2d3: 3, 3 ｿﾞﾛ目! / -1d2: 2)\n'


@pytest.mark.parametrize(
    ('args', 'message'), [(['1d6', 'abc'], "'abc' は読めないよ"), ([' '], '何か書いてね')]
)
def test_unreadable_arguments_print_error(capsys, args, message):
    assert MyDiceRoll.main(args) == 1
    assert capsys.readouterr() == ('', message + '\n')


@pytest.mark.parametrize(('args', 'code'), [(['2d3', '-1d2', '5'], 0), (['abc'], 1)])
def test_running_the_script_with_arguments(args, code):
    done = subprocess.run(
        [sys.executable, 'MyDiceRoll.py', *args],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        encoding='utf-8',
        env={**os.environ, 'PYTHONUTF8': '1', 'DISPLAY': ''},
        check=False,
    )
    assert done.returncode == code
    assert done.stdout.startswith('(ｺﾛｺﾛﾘﾝ…) 2d3 -1d2 5: ' if code == 0 else '')
