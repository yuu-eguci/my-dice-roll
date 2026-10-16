"""MyDiceRoll

ダイスロールをします。

"""

import random
import re
import sys
import tkinter as tk
import unicodedata

PLACEHOLDER = '--- 入力欄 ---'
MAX_DICE = 1000
# これより多く振ったら、出目ではなく合計を出す
MAX_SHOWN_DICE = 10
DICE = re.compile(r'([+-]?)(\d+)d(\d+)', re.ASCII)
INTEGER = re.compile(r'[+-]?\d+', re.ASCII)


def normalize(text):
    """全角を半角に、大文字を小文字にして、スペースをひとつずつにする。"""
    return ' '.join(unicodedata.normalize('NFKC', text).lower().split())


def roll(text, rng=random):
    """'2d3 -1d2 5' のような入力のダイスを振って、合計と [(項目, 出目のリスト), ...] を返す。

    読めない入力は ValueError。
    """
    items = normalize(text).split()
    if not items:
        raise ValueError('何か書いてね')
    total = 0
    rolls = []
    for item in items:
        if INTEGER.fullmatch(item):
            total += int(item)
            continue
        dice = DICE.fullmatch(item)
        if not dice:
            raise ValueError(f"'{item}' は読めないよ")
        sign, count, sides = dice[1], int(dice[2]), int(dice[3])
        if not (1 <= count <= MAX_DICE and sides >= 1):
            raise ValueError(f"'{item}': ダイスは 1〜{MAX_DICE} 個、1 面以上にしてね")
        values = [rng.randint(1, sides) for _ in range(count)]
        rolls.append((item, values))
        total += -sum(values) if sign == '-' else sum(values)
    return total, rolls


def result_line(text, rng=random):
    """結果表示欄に出す文。ダイスを 2 個以上振ったら 2 行目に出目を出す。

    読めない入力は ValueError。
    """
    total, rolls = roll(text, rng)
    line = f'(ｺﾛｺﾛﾘﾝ…) {normalize(text)}: {total}'
    if sum(len(values) for _, values in rolls) < 2:
        return line
    shown = [
        f'{item}: {sum(values)}'
        if len(values) > MAX_SHOWN_DICE
        else f'{item}: {", ".join(map(str, values))}'
        for item, values in rolls
    ]
    return f'{line}\n({" / ".join(shown)})'


class GreenDiceRoll(tk.Frame):
    def __init__(self, master, rng=random):
        super().__init__(master)
        self.rng = rng
        self.last_result = ''
        self.master.geometry('350x330')
        self.master.title('Green Dice Roll')
        self.pack()

        main_frame = tk.Frame(self, relief='groove', borderwidth=2)
        main_frame.pack()

        label_frame = tk.LabelFrame(main_frame, text='せつめい')
        label_frame.pack()

        label = tk.Label(
            label_frame,
            justify=tk.LEFT,
            text="'+'記号は書かず\n'2d3-1d2+5'であれば\n'2d3 -1d2 5'というように書いてね。\n"
            '書いたらエンター。\n',
        )
        label.pack()

        self.entry = tk.Entry(main_frame, width=30)
        self.entry.insert(0, PLACEHOLDER)
        self.entry.pack()
        self.entry.bind('<Return>', self.calculate)
        self.entry.bind('<FocusIn>', self.clear_placeholder)

        tk.Label(main_frame, text='').pack()

        self.result_area = tk.Text(main_frame, bg='#f5deb3', height=3, width=25)
        self.result_area.insert('end', '--- 結果表示欄 ---')
        self.result_area.configure(state='disabled')
        self.result_area.pack()

        self.copy_button = tk.Button(
            main_frame, text='結果をコピーするヴォタン', command=self.copy_result, height=2
        )
        self.copy_button.pack()

        self.close_button = tk.Button(
            main_frame, text='　　　閉じるヴォタン　　　', command=self.master.destroy, height=2
        )
        self.close_button.pack()

    def clear_placeholder(self, event=None):
        if self.entry.get() == PLACEHOLDER:
            self.entry.delete(0, tk.END)

    def calculate(self, event=None):
        try:
            self.last_result = result_line(self.entry.get(), self.rng)
            shown = self.last_result
        except ValueError as error:
            self.last_result = ''
            shown = str(error)
        self.result_area.configure(state='normal')
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert('end', shown)
        self.result_area.configure(state='disabled')

    def copy_result(self):
        if self.last_result:
            self.clipboard_clear()
            self.clipboard_append('>> ' + self.last_result)


def main(args):
    """引数があれば画面を出さずに振る。なければ画面を出す。"""
    if args:
        try:
            print(result_line(' '.join(args)))
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        return 0
    root = tk.Tk()
    GreenDiceRoll(root)
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
