import re
from pathlib import Path

import pytest

from MyDiceRoll import HOW_TO, PLACEHOLDER, roll

README = Path(__file__).parent.parent / 'README.md'
HOW_TO_SECTION = README.read_text(encoding='utf-8').split('## 書きかた')[1].split('\n## ')[0]
# `...` のうち、数字を含んでいてダイスの入力に見えるもの
EXAMPLES = [
    example
    for example in re.findall(r'`([^`]+)`', HOW_TO_SECTION)
    if re.fullmatch(r'[-\d\sdｄ０-９ー　]*[\d０-９][-\d\sdｄ０-９ー　]*', example)
]


def test_readme_and_window_show_the_same_example():
    for example in ['2d3-1d2+5', '2d3 -1d2 5']:
        assert f"'{example}'" in HOW_TO
        assert f'`{example}`' in HOW_TO_SECTION
    assert f'`{PLACEHOLDER}`' in HOW_TO_SECTION


@pytest.mark.parametrize('example', EXAMPLES)
def test_readme_examples_can_be_rolled(example):
    roll(example)


def test_readme_finds_examples():
    assert EXAMPLES == ['2d3 -1d2 5', '2d3', '-1d2', '5', '-5', '２ｄ６　ー３']


def test_example_with_plus_and_no_spaces_is_rejected():
    with pytest.raises(ValueError, match='は読めないよ'):
        roll('2d3-1d2+5')
