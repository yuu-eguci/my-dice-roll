"""MyDiceRoll

ダイスロールをします。

"""

import random
import re
import tkinter as tk

MAX_DICE = 1000
DICE = re.compile(r'([+-]?)(\d+)d(\d+)', re.ASCII)
INTEGER = re.compile(r'[+-]?\d+', re.ASCII)


def roll(text, rng=random):
    """'2d3 -1d2 5' のような入力のダイスを振って合計を返す。読めない入力は ValueError。"""
    items = text.lower().split()
    if not items:
        raise ValueError('何か書いてね')
    total = 0
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
        result = sum(rng.randint(1, sides) for _ in range(count))
        total += -result if sign == '-' else result
    return total


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
        self.entry.insert(0, '--- 入力欄 ---')
        self.entry.pack()
        self.entry.bind('<Return>', self.calculate)

        tk.Label(main_frame, text='').pack()

        self.result_area = tk.Text(main_frame, bg='#f5deb3', height=3, width=25)
        self.result_area.insert('end', '--- 結果表示欄 ---')
        self.result_area.pack()

        self.copy_button = tk.Button(
            main_frame, text='結果をコピーするヴォタン', command=self.copy_result, height=2
        )
        self.copy_button.pack()

        self.close_button = tk.Button(
            main_frame, text='　　　閉じるヴォタン　　　', command=self.master.destroy, height=2
        )
        self.close_button.pack()

    def calculate(self, event=None):
        text = ' '.join(self.entry.get().lower().split())
        try:
            self.last_result = f'(ｺﾛｺﾛﾘﾝ…) {text}: {roll(text, self.rng)}'
            shown = self.last_result
        except ValueError as error:
            self.last_result = ''
            shown = str(error)
        self.result_area.delete('1.0', tk.END)
        self.result_area.insert('end', shown)

    def copy_result(self):
        if self.last_result:
            self.clipboard_clear()
            self.clipboard_append('>> ' + self.last_result)


def main():
    root = tk.Tk()
    GreenDiceRoll(root)
    root.mainloop()


if __name__ == '__main__':
    main()
