import tkinter as tk
import pyperclip, platform
from tkinter import ttk
from stockfish import Stockfish

if platform.system() == 'Windows':
    stockfish = Stockfish(path='.\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe')
elif platform.system() == 'Linux':
    stockfish = Stockfish(path='./stockfish_15.1_linux_x64/stockfish-ubuntu-20.04-x86-64')
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

def update_engine():
    stockfish.update_engine_parameters({'Skill Level':s_lv.get()})
    stockfish.set_depth(dp.get())
    alert2.config(text='Updated engine parameters successfully!\nPlease mind that the settings may affect engine performance.')
    return

def reset_engine():
    stockfish.reset_engine_parameters()
    s_lv.set(20)
    dp.set(15)
    alert2.config(text='Resetted engine parameters.')
    return

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
            alert.config(text=f"Black played: {play_move}")
        else:
            alert.config(text=f"White played: {play_move}")
        stockfish.make_moves_from_current_position([play_move])
        turn = turn + 1
    else:
        if len(play_move) == 0:
            alert.config(text=f'Generated new best moves.')
        elif len(play_move) != 4:
            alert.config(text=f"Please use the preferred chess notation by UCI engines'.\n(e.g. a2a4 means piece on a2 moves to a4)")
        else:
            alert.config(text=f'Move {play_move} is an illegal move.')

    if turn % 2 == 0:
        to_move.config(text='Black to move:')
    else:
        to_move.config(text='White to move:')

    move.delete(0, tk.END)

    board.config(text=stockfish.get_board_visual())

    evaluation = stockfish.get_evaluation()
    evalpos = evaluation['value']
    if evaluation['type'] == 'cp':
        eval.config(text=evaluation['value'])
        scale = evalpos + 1000 #max 2000, min 0, w -1000, b -1000
        evalbar.config(value=scale)
    else:
        if evalpos > 0: #white mate in x
            eval.config(text=f"M{evaluation['value']}")
            evalbar.config(value=2000)
        elif evalpos < 0: #black mate in x
            eval.config(text=f"M{evaluation['value']}")
            evalbar.config(value=0)
        else: #mate in 0, checkmated
            if stockfish.get_fen_position().split(' ')[1] == 'w':
                eval.config(text="0-1")
            else:
                eval.config(text="1-0")
            eval1.config(text='')
            return

    eval1.config(text=stockfish.get_best_move())
    top_moves = ''
    num = 1
    for i in stockfish.get_top_moves(3):
        if i['Centipawn'] == None:
            top_moves += f"{num}. {i['Move']}, M{i['Mate']}\n"
            num = num + 1
        else:
            top_moves += f"{num}. {i['Move']}, pos {i['Centipawn']}\n"
            num = num + 1
    eval2.config(text=top_moves)
    return

root = tk.Tk()
root.geometry('800x600')
root.title('Stockfish Engine 15.1')
root.iconbitmap('./stockfish.ico')

style = ttk.Style(root)
style.theme_use('alt')

# stockfish settings
s_lv = tk.IntVar()
dp = tk.IntVar()
s_lv.set(20)
dp.set(15)

label = tk.Label(root, text='Stockfish-15.1@github.com/archisha69', foreground='#006942')
label.place(x=0, y=0)

to_skill_lv = tk.Label(root, text='Stockfish skill level:', font='Verdana 10')
to_skill_lv.place(x=450, y=30)
lv = [10, 15, 20]
skill_lv = tk.OptionMenu(root, s_lv, *lv,)
skill_lv.place(x=630, y=25)

to_depth = tk.Label(root, text='Stockfish depth:', font='Verdana 10')
to_depth.place(x=450, y=60)
d = [10, 15, 20]
depth = tk.OptionMenu(root, dp, *d)
depth.place(x=630, y=58)

update = tk.Button(root, text='update', font='Verdana 10', command=update_engine)
update.place(x=450, y=90)
reset = tk.Button(root, text='reset', font='Verdana 10', command=reset_engine)
reset.place(x=520, y=90)

alert2 = tk.Label(root, font='Verdana 8', foreground='#ff0000', justify='left')
alert2.place(x=450, y=130)

# gameplay
to_move = tk.Label(root, text='White to move:', font='Verdana 10')
to_move.place(x=20, y=30)
move = tk.Entry(root)
move.place(x=150, y=35)
confirm = tk.Button(root, text='move', font='Verdana 10', command=get_move)
confirm.place(x=300, y=30)
alert = tk.Label(root, font='Verdana 8', foreground='#ff0000', justify='left')
alert.place(x=20, y=60)

to_eval = tk.Label(root, text='Evaluation:', font='Verdana 10')
to_eval.place(x=20, y=95)
eval = tk.Label(root, font='Verdana 10')
eval.place(x=20, y=115)
style.configure('black.Horizontal.TProgressbar', background='#ffffff', troughcolor='#000000', pbarrelief='flat', troughrelief='flat')
evalbar = ttk.Progressbar(root, maximum=2000, value=1000, length=315, style='black.Horizontal.TProgressbar')
evalbar.place(x=80, y=120)

eval1 = tk.Label(root, text='Best Moves:', font='Verdana 10')
eval1.place(x=20, y=140)
eval1 = tk.Label(root, font='Verdana 10', foreground='#54a611', background='#fcfcfc', justify='left')
eval1.place(x=20, y=160)
eval2 = tk.Label(root, font='Verdana 10', foreground='#03a614', justify='left')
eval2.place(x=20, y=190)

board = tk.Label(root, text=stockfish.get_board_visual(), font=f'Fixedsys 8', justify='left')
board.place(x=20, y=250)

copy_fen = tk.Button(root, text='copy FEN', font='Verdana 10', command=copy_fen)
copy_fen.place(x=320, y=260)
alert1 = tk.Label(root, font='Verdana 8', foreground='#ff0000')
alert1.place(x=320, y=300)

get_move()
root.mainloop()

