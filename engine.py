import tkinter as tk
import pyperclip, platform
from stockfish import Stockfish

if platform.system() == 'Windows':
    stockfish = Stockfish(path='.\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe')
elif platform.system() == 'Linux':
    stockfish = Stockfish(path='.\stockfish_15.1_linux_x64\stockfish-ubuntu-20.04-x86-64')
else:
    print('OS not supported, please try to use another OS instead.')
    exit()

# {
#     "Debug Log File": "",
#     "Contempt": 0,
#     "Min Split Depth": 0,
#     "Threads": 1, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
#     "Ponder": "false",
#     "Hash": 16, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
#     "MultiPV": 1,
#     "Skill Level": 20,
#     "Move Overhead": 10,
#     "Minimum Thinking Time": 20,
#     "Slow Mover": 100,
#     "UCI_Chess960": "false",
#     "UCI_LimitStrength": "false",
#     "UCI_Elo": 1350
# }

def copy_fen():
    pyperclip.copy(stockfish.get_fen_position())
    alert1.config(text="Copied FEN from current position!")
    return

turn = 1
def get_move():
    global turn
    play_move = move.get().strip()

    if stockfish.is_move_correct(play_move) == True and len(play_move) == 4:
        if turn % 2 == 0:
            alert.config(text=f"black played: {play_move}")
        else:
            alert.config(text=f"white played: {play_move}")
        stockfish.make_moves_from_current_position([play_move])
        turn = turn + 1
    else:
        if len(play_move) == 0:
            alert.config(text=f'Generated new best moves.')
        elif len(play_move) != 4:
            alert.config(text=f"Please use the preferred chess notation by UCI engines'. (e.g. a2a4 means piece on a2 moves to a4)")
        else:
            alert.config(text=f'Move {play_move} is an illegal move.')

    if turn % 2 == 0:
        to_move.config(text='black to move:')
    else:
        to_move.config(text='white to move:')

    move.delete(0, tk.END)

    board.config(text=stockfish.get_board_visual())
    eval.config(text=stockfish.get_evaluation())
    eval1.config(text=stockfish.get_best_move())
    top_moves = ''
    for i in stockfish.get_top_moves(3):
        if i['Centipawn'] == None:
            top_moves += f"{i['Move']}, M{i['Mate']}\n"
        else:
            top_moves += f"{i['Move']}, pos {i['Centipawn']}\n"
    eval2.config(text=top_moves)

root = tk.Tk()
root.geometry('800x600')
root.title('Stockfish engine 3.28.0')
root.iconbitmap('./stockfish.ico')

'''
global s_lv, dp, mde
s_lv = tk.IntVar()
dp = tk.IntVar()
mde = tk.StringVar()

to_skill_lv = tk.Label(root, text='stockfish skill level:', font='Verdana 10')
to_skill_lv.place(x=20, y=20)
lv = ['10', '15', '20']
skill_lv = tk.OptionMenu(root, s_lv, *lv, command=stockfish.set_skill_level(s_lv.get()))
s_lv.set(20)
skill_lv.place(x=200, y=15)

to_depth = tk.Label(root, text='stockfish depth:', font='Verdana 10')
to_depth.place(x=20, y=40)
d = ['10', '15', '20']
depth = tk.OptionMenu(root, dp, *d, command=stockfish.set_depth(dp.get()))
dp.set(15)
depth.place(x=200, y=35)

to_mode = tk.Label(root, text='stockfish mode:', font='Verdana 10')
to_mode.place(x=20, y=60)
m = ['default', 'chess960']
mode = tk.OptionMenu(root, mde, *m, command=stockfish.update_engine_parameters({"UCI_Chess960": "true"}) if mde.get() == 'chess960' else stockfish.update_engine_parameters({"UCI_Chess960": "false"}))
mde.set('default')
mode.place(x=200, y=55)
'''

to_move = tk.Label(root, text='white to move:', font='Verdana 10')
to_move.place(x=20, y=100)
move = tk.Entry(root)
move.place(x=150, y=100)
confirm = tk.Button(root, text='move', font='Verdana 10', command=get_move)
confirm.place(x=300, y=100)
alert = tk.Label(root, font='Verdana 8', foreground='#ff0000')
alert.place(x=20, y=130)

to_eval = tk.Label(root, text='eval:', font='Verdana 10')
to_eval.place(x=20, y=160)
eval = tk.Label(root, font='Verdana 10')
eval.place(x=20, y=180)

eval1 = tk.Label(root, text='best moves:', font='Verdana 10')
eval1.place(x=20, y=205)
eval1 = tk.Label(root, font='Verdana 10', foreground='#54a611', background='#fcfcfc', justify='left')
eval1.place(x=20, y=225)
eval2 = tk.Label(root, font='Verdana 10', foreground='#03a614', justify='left')
eval2.place(x=20, y=245)

board = tk.Label(root, text=stockfish.get_board_visual(), font=f'Fixedsys 8', justify='left')
board.place(x=20, y=300)

copy_fen = tk.Button(root, text='copy FEN', font='Verdana 10', command=copy_fen)
copy_fen.place(x=320, y=300)
alert1 = tk.Label(root, font='Verdana 8', foreground='#ff0000')
alert1.place(x=320, y=330)

get_move()
root.mainloop()

