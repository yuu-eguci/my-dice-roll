"""MyDiceRoll

ダイスロールをします。

"""

import random
import re
import sys
import tkinter as tk
import unicodedata

PLACEHOLDER = '--- 入力欄 ---'
HOW_TO = (
    "'+'記号は書かず\n'2d3-1d2+5'であれば\n'2d3 -1d2 5'というように書いてね。\n書いたらエンター。\n"
)
MAX_DICE = 1000
# これより多く振ったら、出目ではなく合計を出す
MAX_SHOWN_DICE = 10
# 大きすぎる数で固まったり Python のエラーが出たりしないように、数は 6 桁まで
DICE = re.compile(r'([+-]?)(\d{1,6})d(\d{1,6})', re.ASCII)
INTEGER = re.compile(r'[+-]?\d{1,6}', re.ASCII)
# 日本語入力で打ちがちなマイナス (長音記号 ー と U+2212 のマイナス記号)
MINUS = str.maketrans('\u30fc\u2212', '--')


def normalize(text):
    """全角を半角に、大文字を小文字にして、スペースをひとつずつにする。"""
    return ' '.join(unicodedata.normalize('NFKC', text).translate(MINUS).lower().split())


def roll(text, rng=random):
    """'2d3 -1d2 5' のような入力のダイスを振って、合計と [(項目, 出目のリスト), ...] を返す。

    読めない入力は ValueError。
    """
    items = normalize(text).split()
    if not items:
        raise ValueError('何か書いてね')
    total = 0
    dice_count = 0
    rolls = []
    for item in items:
        if INTEGER.fullmatch(item):
            total += int(item)
            continue
        dice = DICE.fullmatch(item)
        if not dice:
            raise ValueError(f"'{item}' は読めないよ")
        sign, count, sides = dice[1], int(dice[2]), int(dice[3])
        if count < 1 or sides < 1:
            raise ValueError(f"'{item}': ダイスは 1 個以上、1 面以上にしてね")
        dice_count += count
        if dice_count > MAX_DICE:
            raise ValueError(f'ダイスは全部で {MAX_DICE} 個までにしてね')
        values = [rng.randint(1, sides) for _ in range(count)]
        rolls.append((item, values))
        total += -sum(values) if sign == '-' else sum(values)
    return total, rolls


def sound(dice_count):
    """振ったダイスの数に合わせた音。"""
    if dice_count >= MAX_DICE:
        return '(ﾄﾞｼｬｰｰｰ…)'
    if dice_count >= 100:
        return '(ｼﾞｬﾗｼﾞｬﾗｼﾞｬﾗ…)'
    return '(ｺﾛｺﾛﾘﾝ…)'


def result_line(text, rng=random):
    """結果表示欄に出す文。2 行目に出目を出す。

    読めない入力は ValueError。
    """
    total, rolls = roll(text, rng)
    dice_count = sum(len(values) for _, values in rolls)
    line = f'{sound(dice_count)} {normalize(text)}: {total}'
    # ダイスが 1 個だけのときや、合計しか出さない項目ひとつだけのときは、合計と同じなので出さない
    if dice_count < 2 or (len(rolls) == 1 and dice_count > MAX_SHOWN_DICE):
        return line
    return f'{line}\n({" / ".join(breakdown(item, values) for item, values in rolls)})'


def breakdown(item, values):
    """'2d6: 3, 3 ｿﾞﾛ目!' のような、ひとつの項目の出目。多すぎるときは合計。"""
    if len(values) > MAX_SHOWN_DICE:
        return f'{item}: {sum(values)}'
    zorome = ' ｿﾞﾛ目!' if len(values) > 1 and len(set(values)) == 1 else ''
    return f'{item}: {", ".join(map(str, values))}{zorome}'


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

        tk.Label(label_frame, justify=tk.LEFT, text=HOW_TO).pack()

        self.entry = tk.Entry(main_frame, width=30)
        self.entry.insert(0, PLACEHOLDER)
        self.entry.pack()
        self.entry.bind('<Return>', self.calculate)
        self.entry.bind('<KP_Enter>', self.calculate)
        self.entry.bind('<FocusIn>', self.clear_placeholder)

        tk.Label(main_frame, text='').pack()

        result_frame = tk.Frame(main_frame)
        result_frame.pack()
        self.result_area = tk.Text(result_frame, bg='#f5deb3', height=3, width=25)
        self.result_area.insert('end', '--- 結果表示欄 ---')
        self.result_area.configure(state='disabled')
        self.result_area.pack(side=tk.LEFT)
        # 結果が長くて収まらないときに、続きがあるとわかるように
        self.scrollbar = tk.Scrollbar(result_frame, command=self.result_area.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.result_area.configure(yscrollcommand=self.scrollbar.set)

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
