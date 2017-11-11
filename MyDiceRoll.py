# coding: utf-8

"""MyDiceRoll

ダイスロールをします。

========================================
バージョン1.0(2015-05-06)
    完成。
バージョン1.1(2017-09-25)
    久々に開いてdoc書いた。
    昔を懐かしむ意味もこめてリファクタリングはしない。
"""

import tkinter as Tk
import random, sys

class GreenDiceRoll(Tk.Frame):
    def __init__(self, master = None):
        Tk.Frame.__init__(self, master)
        self.master.geometry('350x330')
        self.master.title('Green Dice Roll')

        z = Tk.StringVar()
        z.set(u'--- 入力欄 ---')
        y = u'--- 結果表示欄 ---'
        u = Tk.StringVar()

        def if_minus(a):
            if a.find('-') > (- 1) and a.find('d') > (- 1): return 1
            else: return 0
        def if_integer(a):
            if a.find('d') == (- 1): return 1
            else: return 0
        def dice_roll(a, b, e = 0): # aDb の結果を出す
            d = 0
            for i in range(a):
                c = random.randint(1, b)
                d += c
            return d + e
        def calculate(event):
            x = z.get()
            # D を小文字にする
            x = x.lower()
            # 要素の個数を求める
            number = len(x.split(' '))
            # 要素ひとつずつ変数を設定する
            a = b = c = d = e = f = g = h = i = j = 0
            x_list = [a, b, c, d, e, f, g, h, i, j]
            for foo in range(number):
                x_list[foo] = x.split(' ')[foo]
            # 「マイナスかつ D 要素」の位置を探す
            m1 = m2 = m3 = m4 = m5 = m6 = m7 = m8 = m9 = m10 = 0
            m_list = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10]
            for foo in range(number):
                m_list[foo] = if_minus(x_list[foo]) # マイナスで D の要素のリスト番号が1になる
            # 「ただの整数」の位置を探す
            i1 = i2 = i3 = i4 = i5 = i6 = i7 = i8 = i9 = i10 = 0
            i_list = [i1, i2, i3, i4, i5, i6, i7, i8, i9, i10]
            for foo in range(number):
                i_list[foo] = if_integer(x_list[foo])
            # d の計算する
            r1 = r2 = r3 = r4 = r5 = r6 = r7 = r8 = r9 = r10 = 0
            r_list = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10]
            for foo in range(number):
                if m_list[foo] == i_list[foo] == 0:
                    r_list[foo] = dice_roll(int(x_list[foo].split('d')[0]), int(x_list[foo].split('d')[1]))
            for foo in range(number):
                if m_list[foo] == 1:
                    x_list[foo] = x_list[foo].replace('-', '')
                    r_list[foo] = dice_roll(int(x_list[foo].split('d')[0]), int(x_list[foo].split('d')[1]))
                    r_list[foo] = r_list[foo] * - 1
            for foo in range(number):
                if i_list[foo] == 1:
                    r_list[foo] = int(x_list[foo])
            # 全部を足した結果を出す
            result = sum(r_list)
            y = (u'(ｺﾛｺﾛﾘﾝ…) %s: %d' % (x, result))
            r_area.delete('1.0', Tk.END)
            r_area.insert('end', y)
            u.set(y)
        def result_copy(): # クリップボードにコピー
            def get_clipboard():
                return Tk.Text().clipboard_get()
            def put_clipboard(a):
                Tk.Text().clipboard_clear()
                Tk.Text().clipboard_append(a)
            y = '>> ' + u.get()
            put_clipboard(y)
            assert y == get_clipboard()

        mainFrame = Tk.Frame(self, relief = 'groove', borderwidth = 2)
        mainFrame.pack()

        labelFrame = Tk.LabelFrame(mainFrame, text = 'せつめい')
        labelFrame.pack()

        label = Tk.Label(labelFrame, justify = Tk.LEFT, text = u'\'+\'記号は書かず\n\'2d3-1d2+5\'であれば\n\'2d3 -1d2 5\'というように書いてね。\n書いたらエンター。\n')
        label.pack()

        entry = Tk.Entry(mainFrame, textvariable = z, width = 30)
        entry.pack()
        entry.bind('<Return>', calculate)

        label2 = Tk.Label(mainFrame, text = '')
        label2.pack()

        r_area = Tk.Text(mainFrame, bg = '#f5deb3', height = 3, width = 25)
        r_area.insert('end', y)
        r_area.pack()

        copy = Tk.Button(mainFrame, text = u'結果をコピーするヴォタン', command = result_copy, height = 2)
        copy.pack()

        button = Tk.Button(mainFrame, text = u'　　　閉じるヴォタン　　　', command = sys.exit, height = 2)
        button.pack()

if __name__ == '__main__':
    gdr = GreenDiceRoll()
    gdr.pack()
    gdr.mainloop()