import re

import pytest

from MyDiceRoll import normalize, result_line, roll


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


@pytest.mark.parametrize('token', ['abc', '2d3-1d2', '3d-6', '1d6-', '1d2d3', 'd', '2d', '2d3+5'])
def test_unreadable_item(token):
    with pytest.raises(ValueError, match=re.escape(f"'{token}' は読めないよ")):
        roll(f'1d6 {token}')


@pytest.mark.parametrize('token', ['0d6', '1d0', '-1d0'])
def test_out_of_range_dice(token):
    with pytest.raises(ValueError, match=f"'{token}': ダイスは 1 個以上、1 面以上にしてね"):
        roll(token)


def test_error_shows_normalized_item():
    with pytest.raises(ValueError, match="'2d0'"):
        roll('２ｄ０')


@pytest.mark.parametrize('text', ['1001d6', '1000d1 1d1', '500d1 -501d1'])
def test_more_than_1000_dice_in_total(text):
    with pytest.raises(ValueError, match='ダイスは全部で 1000 個までにしてね'):
        roll(text)


def test_exactly_1000_dice_in_total():
    assert roll('500d1 -500d1', MaxRng())[0] == 0


@pytest.mark.parametrize(
    'token',
    ['1234567', '1d1234567', '1234567d1', '9' * 5000],
    ids=['7-digits', 'sides', 'count', '5000-digits'],
)
def test_numbers_longer_than_6_digits_are_unreadable(token):
    with pytest.raises(ValueError, match='は読めないよ'):
        roll(token)


def test_6_digit_numbers():
    assert roll('999999 -1d999999', MaxRng())[0] == 0


@pytest.mark.parametrize('minus', ['ー', '−'])
def test_ime_minus_signs(minus):
    assert roll(f'5 {minus}1d2 {minus}1', MaxRng())[0] == 2


def test_full_width_input():
    assert roll('２Ｄ３　－１ｄ２　５', MaxRng())[0] == 6 - 2 + 5


def test_result_line_shows_each_die():
    assert (
        result_line('2d3 -1d2 5', MaxRng())
        == '(ｺﾛｺﾛﾘﾝ…) 2d3 -1d2 5: 9\n(2d3: 3, 3 ｿﾞﾛ目! / -1d2: 2)'
    )


def test_result_line_shows_sum_for_more_than_ten_dice():
    assert result_line('10d2 11d2', MaxRng()) == (
        '(ｺﾛｺﾛﾘﾝ…) 10d2 11d2: 42\n(10d2: 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ｿﾞﾛ目! / 11d2: 22)'
    )


@pytest.mark.parametrize('text', ['1d6', '1d6 5', '5', '11d6', '-999d6 5'])
def test_result_line_has_no_breakdown_for_one_die_or_one_summed_item(text):
    assert '\n' not in result_line(text, MaxRng())


def test_roll_returns_each_die():
    assert roll('2d3 -1d2 5', MaxRng()) == (9, [('2d3', [3, 3]), ('-1d2', [2])])


@pytest.mark.parametrize(
    ('text', 'sound'),
    [
        ('5', '(ｺﾛｺﾛﾘﾝ…)'),
        ('99d1', '(ｺﾛｺﾛﾘﾝ…)'),
        ('99d1 1d1', '(ｼﾞｬﾗｼﾞｬﾗｼﾞｬﾗ…)'),
        ('999d1', '(ｼﾞｬﾗｼﾞｬﾗｼﾞｬﾗ…)'),
        ('500d1 -500d1', '(ﾄﾞｼｬｰｰｰ…)'),
    ],
)
def test_sound_grows_with_dice(text, sound):
    assert result_line(text, MaxRng()).startswith(f'{sound} {text}: ')


class SequenceRng:
    def __init__(self, *values):
        self.values = iter(values)

    def randint(self, a, b):
        return next(self.values)


def test_zorome_only_when_all_dice_of_an_item_match():
    assert result_line('2d6 2d6 1d6 1d6', SequenceRng(3, 3, 3, 4, 5, 5)) == (
        '(ｺﾛｺﾛﾘﾝ…) 2d6 2d6 1d6 1d6: 23\n(2d6: 3, 3 ｿﾞﾛ目! / 2d6: 3, 4 / 1d6: 5 / 1d6: 5)'
    )


def test_count_can_be_omitted():
    assert roll('d6 -d4', MaxRng()) == (2, [('d6', [6]), ('-d4', [4])])


@pytest.mark.parametrize(
    ('text', 'normalized'),
    [
        ('2d3 - 1d2 + 5', '2d3 -1d2 +5'),
        ('-  5', '-5'),
        ('２ｄ３　ー　１', '2d3 -1'),
        ('1d6 -', '1d6 -'),
    ],
)
def test_signs_followed_by_spaces_stick_to_the_next_item(text, normalized):
    assert normalize(text) == normalized


def test_lone_trailing_sign_is_unreadable():
    with pytest.raises(ValueError, match="'-' は読めないよ"):
        roll('1d6 -')
