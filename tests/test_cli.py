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


@pytest.mark.parametrize(
    ('args', 'code', 'stdout', 'stderr'),
    [
        (['5', '-1'], 0, '(ｺﾛｺﾛﾘﾝ…) 5 -1: 4\n', ''),
        (['abc'], 1, '', "'abc' は読めないよ\n"),
    ],
)
def test_running_the_script_with_arguments(args, code, stdout, stderr):
    done = subprocess.run(
        [sys.executable, 'MyDiceRoll.py', *args],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        encoding='utf-8',
        env={**os.environ, 'PYTHONUTF8': '1', 'DISPLAY': ''},
        check=False,
    )
    assert (done.returncode, done.stdout, done.stderr) == (code, stdout, stderr)


def test_same_seed_prints_same_result(capsys):
    outputs = []
    for _ in range(2):
        assert MyDiceRoll.main(['--seed', '42', '10d100']) == 0
        outputs.append(capsys.readouterr().out)
    assert outputs[0] == outputs[1]
    assert outputs[0].startswith('(ｺﾛｺﾛﾘﾝ…) 10d100: ')


@pytest.mark.parametrize('args', [['--seed', 'x', '1d6'], ['--seed']])
def test_seed_needs_a_number(capsys, args):
    assert MyDiceRoll.main(args) == 1
    assert capsys.readouterr() == ('', '--seed のあとには数を書いてね\n')
