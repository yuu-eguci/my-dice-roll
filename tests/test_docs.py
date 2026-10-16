import re
from pathlib import Path

import pytest

from MyDiceRoll import HOW_TO, PLACEHOLDER, result_line, roll
from tests.test_roll import SequenceRng

README = Path(__file__).parent.parent / 'README.md'
README_TEXT = README.read_text(encoding='utf-8')
HOW_TO_SECTION = README_TEXT.split('## 書きかた')[1].split('\n## ')[0]
# 書いてはいけない例
NOT_LIKE_THIS = '2d3-1d2+5'
# `...` のうち、数字を含んでいてダイスの入力に見えるもの
EXAMPLES = [
    example
    for example in re.findall(r'`([^`]+)`', HOW_TO_SECTION)
    if re.fullmatch(r'[-+\d\sdｄ０-９ー　]*[\d０-９][-+\d\sdｄ０-９ー　]*', example)
    and example != NOT_LIKE_THIS
]


def test_readme_and_window_show_the_same_example():
    for example in [NOT_LIKE_THIS, '2d3 -1d2 5']:
        assert f"'{example}'" in HOW_TO
        assert f'`{example}`' in HOW_TO_SECTION
    assert f'`{PLACEHOLDER}`' in HOW_TO_SECTION


@pytest.mark.parametrize('example', EXAMPLES)
def test_readme_examples_can_be_rolled(example):
    roll(example)


def test_readme_finds_examples():
    assert EXAMPLES == [
        '2d3 -1d2 5',
        '2d3',
        '-1d2',
        '5',
        '-5',
        'd6',
        '1d6',
        '2d3 - 1d2 + 5',
        '2d3 -1d2 +5',
        '２ｄ６　ー３',
    ]


def test_example_with_plus_and_no_spaces_is_rejected():
    with pytest.raises(ValueError, match='は読めないよ'):
        roll(NOT_LIKE_THIS)


def test_readme_sample_output_is_what_the_script_prints():
    command, *output = re.search(r'```bash\n(docker compose run .*?)```', README_TEXT, re.S)[
        1
    ].splitlines()
    assert command.endswith('python MyDiceRoll.py 2d3 -1d2 5')
    assert output == [
        '# ' + line for line in result_line('2d3 -1d2 5', SequenceRng(1, 3, 2)).splitlines()
    ]
