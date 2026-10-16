import re

import pytest

from MyDiceRoll import roll


class MaxRng:
    def randint(self, a, b):
        return b


class MinRng:
    def randint(self, a, b):
        return a


def test_readme_example_with_max_and_min_rolls():
    assert roll('2d3 -1d2 5', MaxRng()) == 6 - 2 + 5
    assert roll('2d3 -1d2 5', MinRng()) == 2 - 1 + 5


def test_uppercase_d_and_extra_spaces():
    assert roll('  2D6   -3 ', MaxRng()) == 12 - 3


def test_more_than_ten_items():
    assert roll(' '.join(['1'] * 11), MaxRng()) == 11


def test_plus_signs_still_work():
    assert roll('+5 +1d6', MaxRng()) == 11


def test_uses_random_by_default():
    assert 1 <= roll('1d6') <= 6


def test_up_to_1000_dice():
    assert roll('1000d1', MaxRng()) == 1000


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
