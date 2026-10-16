import re

import pytest

from MyDiceRoll import result_line, roll


class MaxRng:
    def randint(self, a, b):
        return b


class MinRng:
    def randint(self, a, b):
        return a


def test_readme_example_with_max_and_min_rolls():
    assert roll('2d3 -1d2 5', MaxRng())[0] == 6 - 2 + 5
    assert roll('2d3 -1d2 5', MinRng())[0] == 2 - 1 + 5


def test_uppercase_d_and_extra_spaces():
    assert roll('  2D6   -3 ', MaxRng())[0] == 12 - 3


def test_more_than_ten_items():
    assert roll(' '.join(['1'] * 11), MaxRng())[0] == 11


def test_plus_signs_still_work():
    assert roll('+5 +1d6', MaxRng())[0] == 11


def test_uses_random_by_default():
    assert 1 <= roll('1d6')[0] <= 6


def test_up_to_1000_dice():
    assert roll('1000d1', MaxRng())[0] == 1000


@pytest.mark.parametrize('text', ['', '   '])
def test_empty_input(text):
    with pytest.raises(ValueError, match='何か書いてね'):
        roll(text)


@pytest.mark.parametrize('token', ['abc', '2d3-1d2', '3d-6', '1d6-', '1d2d3', 'd6', '2d', '2d3+5'])
def test_unreadable_item(token):
    with pytest.raises(ValueError, match=re.escape(f"'{token}' は読めないよ")):
        roll(f'1d6 {token}')


@pytest.mark.parametrize('token', ['0d6', '1001d6', '1d0', '-1d0'])
def test_out_of_range_dice(token):
    with pytest.raises(ValueError, match=f"'{token}': ダイスは 1〜1000 個、1 面以上にしてね"):
        roll(token)


def test_full_width_input():
    assert roll('２Ｄ３　－１ｄ２　５', MaxRng())[0] == 6 - 2 + 5


def test_result_line_shows_each_die():
    assert result_line('2d3 -1d2 5', MaxRng()) == '(ｺﾛｺﾛﾘﾝ…) 2d3 -1d2 5: 9\n(2d3: 3, 3 / -1d2: 2)'


def test_result_line_shows_sum_for_more_than_ten_dice():
    assert result_line('10d2 11d2', MaxRng()) == (
        '(ｺﾛｺﾛﾘﾝ…) 10d2 11d2: 42\n(10d2: 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 / 11d2: 22)'
    )


@pytest.mark.parametrize('text', ['1d6', '1d6 5', '5'])
def test_result_line_has_no_breakdown_for_one_die(text):
    assert '\n' not in result_line(text, MaxRng())


def test_roll_returns_each_die():
    assert roll('2d3 -1d2 5', MaxRng()) == (9, [('2d3', [3, 3]), ('-1d2', [2])])
