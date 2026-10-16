import tkinter as tk
from pathlib import Path

import pytest

from MyDiceRoll import GreenDiceRoll
from tests.test_roll import MaxRng


@pytest.fixture
def app():
    root = tk.Tk()
    app = GreenDiceRoll(root, MaxRng())
    root.update()
    yield app
    if _alive(root):
        root.destroy()


def _alive(root):
    try:
        root.winfo_exists()
    except tk.TclError:
        return False
    return True


def enter(app, text):
    app.entry.delete(0, tk.END)
    app.entry.insert(0, text)
    app.entry.focus_force()
    app.update()
    app.entry.event_generate('<Return>')
    app.update()


def result(app):
    return app.result_area.get('1.0', 'end-1c')


def test_window_keeps_original_look(app):
    assert app.master.title() == 'Green Dice Roll'
    assert app.entry.get() == '--- 入力欄 ---'
    assert result(app) == '--- 結果表示欄 ---'
    assert app.copy_button['text'] == '結果をコピーするヴォタン'
    assert app.close_button['text'] == '　　　閉じるヴォタン　　　'


def test_window_size_matches_docker_screen(app):
    assert app.master.geometry().startswith('350x330')
    start_sh = Path(__file__).parent.parent / 'docker' / 'start.sh'
    assert '-screen 0 350x330x24' in start_sh.read_text(encoding='utf-8')


def test_clicking_entry_clears_placeholder_only(app):
    app.entry.focus_force()
    app.update()
    assert app.entry.get() == ''
    enter(app, '1d6')
    app.copy_button.focus_force()
    app.entry.focus_force()
    app.update()
    assert app.entry.get() == '1d6'


def test_result_area_is_read_only(app):
    enter(app, '1d6')
    app.result_area.insert('end', 'typed')
    assert result(app) == '(ｺﾛｺﾛﾘﾝ…) 1d6: 6'


def test_full_width_input_is_shown_half_width(app):
    enter(app, '２ｄ６')
    assert result(app) == '(ｺﾛｺﾛﾘﾝ…) 2d6: 12\n(2d6: 6, 6 ｿﾞﾛ目!)'


def test_keypad_enter_also_rolls(app):
    app.entry.delete(0, tk.END)
    app.entry.insert(0, '1d6')
    app.entry.focus_force()
    app.update()
    app.entry.event_generate('<KP_Enter>')
    app.update()
    assert result(app) == '(ｺﾛｺﾛﾘﾝ…) 1d6: 6'


def test_scrollbar_follows_long_result(app):
    assert app.result_area['yscrollcommand'].endswith('set')
    enter(app, ' '.join(['1d6'] * 20))
    lines = app.result_area.count('1.0', 'end', 'update', 'displaylines')
    assert lines > int(app.result_area['height'])
    assert app.scrollbar.winfo_ismapped()


def test_window_fits_docker_screen(app):
    assert app.master.winfo_reqwidth() <= 350
    assert app.master.winfo_reqheight() <= 330


def test_enter_shows_total(app):
    enter(app, '2d3 -1d2 5')
    assert result(app) == '(ｺﾛｺﾛﾘﾝ…) 2d3 -1d2 5: 9\n(2d3: 3, 3 ｿﾞﾛ目! / -1d2: 2)'


def test_input_is_selected_after_rolling(app):
    enter(app, '1d6')
    assert app.entry.selection_get() == '1d6'


def test_error_replaces_old_result(app):
    enter(app, '1d6')
    enter(app, 'abc')
    assert result(app) == "'abc' は読めないよ"


def test_copy_puts_result_on_clipboard(app):
    enter(app, '2d6')
    app.copy_button.invoke()
    assert app.clipboard_get() == '>> (ｺﾛｺﾛﾘﾝ…) 2d6: 12\n(2d6: 6, 6 ｿﾞﾛ目!)'


@pytest.mark.parametrize('before', [[], ['1d6', 'abc']])
def test_copy_does_nothing_without_result(app, before):
    for text in before:
        enter(app, text)
    app.clipboard_clear()
    app.clipboard_append('keep')
    app.copy_button.invoke()
    assert app.clipboard_get() == 'keep'


def test_close_button_destroys_window(app):
    root = app.master
    app.close_button.invoke()
    assert not _alive(root)
