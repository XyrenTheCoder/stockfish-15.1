import tkinter as tk
from tkinter import ttk
import pyperclip, platform, random, json, string, pygame
import chess, chess.engine, chess.pgn, stockfish
from stockfish import Stockfish
from datetime import date

if platform.system() == 'Windows':
    stockfish = Stockfish(path='.\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe')
elif platform.system() == 'Linux':
    stockfish = Stockfish(path='./stockfish_15.1_linux_x64/stockfish-ubuntu-20.04-x86-64')
else:
    print('OS not supported, please try to use another OS instead.') # mac bad
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

pygame.init()
piece_move = pygame.mixer.Sound('./sfx/move-self.mp3')
piece_capture = pygame.mixer.Sound('./sfx/capture.mp3')
piece_castle = pygame.mixer.Sound('./sfx/castle.mp3')
piece_check = pygame.mixer.Sound('./sfx/move-check.mp3')
piece_promote = pygame.mixer.Sound('./sfx/promote.mp3')
game_start = pygame.mixer.Sound('./sfx/notify.mp3')
game_end = pygame.mixer.Sound('./sfx/game-end.mp3')

with open('./archive.json', 'r') as f: archive = json.load(f)
f.close()

opened = False
def open_archive():
    def change_state():
        global opened
        opened = False
        archivewin.destroy()
        return opened
    global opened, archivewin, vis, _label1
    if not opened:
        archivewin = tk.Toplevel(root)
        archivewin.title('Game Archive')
        archivewin.geometry('300x400')
        archivewin.resizable(False, False)
        archivewin.protocol("WM_DELETE_WINDOW", change_state)
        archivewin.config(bg='#312e2b')

        _label = tk.Label(archivewin, text='Game', font='Verdana 10', fg='#ffffff', bg='#312e2b')
        _label.place(x=20, y=30)

        g = list(archive)
        games = tk.OptionMenu(archivewin, gid, *g, command=show_preview)
        games.place(x=70, y=25)
        games.config(fg='#ffffff', bg="#3c3936", activeforeground='#ffffff', activebackground='#3c3936', font='Verdana 8')

        _label0 = tk.Label(archivewin, text='Game Preview:', font='Verdana 10',  fg='#ffffff', bg='#312e2b')
        _label0.place(x=20, y=60)

        vis = tk.Label(archivewin, font='Consolas 10', fg='#7fa650', bg='#312e2b', justify='left')
        vis.place(x=20, y=90)

        open = tk.Button(archivewin, text='open', font='Verdana 10', fg='#ffffff', bg='#8bb24d', activeforeground='#ffffff', activebackground='#537133', command=confirm_open)
        open.place(x=20, y=230)
        delete = tk.Button(archivewin, text='delete', font='Verdana 10', fg='#ffffff', bg='#3c3936', activeforeground='#ffffff', activebackground='#171614', command=confirm_delete)
        delete.place(x=80, y=230)

        _label1 = tk.Label(archivewin, font='Verdana 8',  fg='#b23330', bg='#312e2b', )
        _label1.place(x=20, y=270)

        opened = True

def show_preview(self):
    vis.config(text=chess.Board(archive[gid.get()]))
    return

def confirm_open():
    if gid.get() == "select game id":
        _label1.config(text="No game selected.")
        return
    else:
        global warn
        warn = tk.Toplevel(archivewin)
        warn.title('Confirm')
        warn.geometry('570x150')
        warn.resizable(False, False)
        warn.config(bg='#312e2b')

        _label0 = tk.Label(warn, text=f'Are you sure to open game {gid.get()}?\nThe current game will be lost if not saved to archive with the current position.', font='Verdana 10',  fg='#ffffff', bg='#312e2b', justify='center')
        _label0.place(x=20, y=30)

        confirm = tk.Button(warn, text='confirm', font='Verdana 10', fg='#ffffff', bg='#8bb24d', activeforeground='#ffffff', activebackground='#537133', command=retrieve_game)
        confirm.place(x=260, y=80)

def confirm_delete():
    if gid.get() == "select game id":
        _label1.config(text="No game selected.")
        return
    else:
        global warn
        warn = tk.Toplevel(archivewin)
        warn.title('Delete')
        warn.geometry('340x150')
        warn.resizable(False, False)
        warn.config(bg='#312e2b')

        _label0 = tk.Label(warn, text=f'Are you sure to delete game {gid.get()}?\nThis action cannot be recovered.', font='Verdana 10',  fg='#b23330', bg='#312e2b', justify='center')
        _label0.place(x=20, y=30)

        confirm = tk.Button(warn, text='confirm', font='Verdana 10', fg='#ffffff', bg='#8bb24d', activeforeground='#ffffff', activebackground='#537133', command=delete_game)
        confirm.place(x=130, y=80)

def retrieve_game():
    gameid = gid.get()
    fen = archive[f'{gameid}']
    stockfish.set_fen_position(fen)
    board.config(text=stockfish.get_board_visual())
    if fen.split()[1] == 'b':
        to_move.config(text='Black to move:')
    else:
        to_move.config(text='White to move:')
    alert1.config(text=f"Opened game {gameid} from archive!")
    get_move()
    warn.destroy()
    archivewin.destroy()
    global opened
    opened = False
    return

def save_game():
    a = string.ascii_letters + string.ascii_letters
    gameid = '@'
    for i in range(9):
        gameid += random.choice(a)
    if gameid in archive:
        return save_game()
    else:
        archive[gameid] = stockfish.get_fen_position()
        with open('./archive.json', 'w') as f:
            json.dump(archive, f, indent=4)
        f.close()
    alert1.config(text=f"Saved game {gameid} to archive!")
    return

def delete_game():
    gameid = gid.get()
    if gameid in archive:
        del archive[gameid]
        with open('./archive.json', 'w') as f:
            json.dump(archive, f, indent=4)
        f.close()
        alert1.config(text=f"Deleted game {gameid} from archive!")
        get_move()
        warn.destroy()
        archivewin.destroy()
        global opened
        opened = False
        return
    else:
        _label1.config(text=f'Game {gameid} does not exist or is deleted.')

def reset_board():
    moved.clear()
    stockfish.set_fen_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    if flipboard == True:
        board.config(text=stockfish.get_board_visual(False))
    else:
        board.config(text=stockfish.get_board_visual())
    alert1.config(text='Resetted board.')
    get_move()
    return

def flip_board():
    global flipboard
    if flipboard != True:
        flipboard = True
        board.config(text=stockfish.get_board_visual(False))
    else:
        flipboard = False
        board.config(text=stockfish.get_board_visual())
    return

def update_engine():
    stockfish.update_engine_parameters({'Skill Level':s_lv.get()})
    stockfish.set_depth(dp.get())
    alert2.config(text='Updated engine parameters successfully!\nPlease mind that the settings may affect engine performance.')
    get_move()
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

def get_pgn():
    today = date.today()
    game = chess.pgn.Game()
    game.headers["Event"] = "Stockfish Engine 15.1"
    game.headers["Site"] = "https://github.com/archisha69/stockfish-15.1"
    game.headers["Date"] = today.strftime("%Y.%m.%d")
    game.headers["Round"] = "0"
    game.headers["White"] = "Stockfish Engine 15.1"
    game.headers["Black"] = "Stockfish Engine 15.1"
    try:
        node = game.add_variation(moved[0])
        for m in moved[1:]:
            node = node.add_variation(m)
        return game
    except IndexError:
        alert1.config(text='PGN empty!')

def copy_pgn():
    pyperclip.copy(str(get_pgn()))
    alert1.config(text="Copied PGN from current position!")
    return

flipboard = False
board2 = chess.Board()
moved = []
def get_move():
    move.config(state='normal')
    confirm.config(state='normal', bg='#8bb24d')
    play_move = move.get().strip()

    if len(play_move) == 0:
        alert.config(text=f'Generated new best moves.')
    elif stockfish.is_move_correct(play_move) and play_move != '':
        # if board2.gives_check(chess.Move.from_uci(play_move)):
        #     piece_check.play()
        if play_move == 'e1g1' or play_move == 'e1c1' or play_move == 'e8g8' or play_move == 'e8c8':
            if (stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.WHITE_KING and stockfish.get_what_is_on_square('h1') == Stockfish.Piece.WHITE_ROOK) or (stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.WHITE_KING and stockfish.get_what_is_on_square('a1') == Stockfish.Piece.WHITE_ROOK) or (stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.BLACK_KING and stockfish.get_what_is_on_square('h8') == Stockfish.Piece.BLACK_ROOK) or (stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.BLACK_KING and stockfish.get_what_is_on_square('a8') == Stockfish.Piece.BLACK_ROOK):
                piece_castle.play()
            else:
                print(play_move[:2], play_move[2:])
                print(stockfish.get_what_is_on_square(play_move[:2]), stockfish.get_what_is_on_square(play_move[2:]))
                piece_move.play()
        elif stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.WHITE_PAWN and play_move[2:3] == '8' or stockfish.get_what_is_on_square(play_move[:2]) == Stockfish.Piece.BLACK_PAWN and play_move[2:3] == '1':
            piece_promote.play()
        elif stockfish.will_move_be_a_capture(play_move) != Stockfish.Capture.NO_CAPTURE:
            piece_capture.play()
        else:
            piece_move.play()

        if stockfish.get_fen_position().split()[1] == 'b':
            alert.config(text=f"Black played: {play_move}")
        else:
            alert.config(text=f"White played: {play_move}")
        stockfish.make_moves_from_current_position([play_move])
        # board2.push(chess.Move.from_uci(play_move))
        moved.append(chess.Move.from_uci(play_move))
    else:
        alert.config(text=f'Move {play_move} is an illegal move or is not an UCI move.')

    if stockfish.get_fen_position().split()[1] == 'b':
        to_move.config(text='Black to move:')
    else:
        to_move.config(text='White to move:')

    move.delete(0, tk.END)

    if flipboard == True:
        board.config(text=stockfish.get_board_visual(False))
    else:
        board.config(text=stockfish.get_board_visual())

    top_moves = ''
    num = 1
    for i in stockfish.get_top_moves(3):
        if i['Centipawn'] == None:
            top_moves += f"{num}. {i['Move']}, M{i['Mate']}\n"
            num = num + 1
        else:
            top_moves += f"{num}. {i['Move']}, eval {i['Centipawn'] / 100}\n"
            num = num + 1
    eval2.config(text=top_moves)

    evaluation = stockfish.get_evaluation()
    evalpos = evaluation['value']
    if evaluation['type'] == 'cp':
        eval.config(text=evalpos / 100) #centipawn
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
                evalbar.config(value=0)
            else:
                eval.config(text="1-0")
                evalbar.config(value=2000)
            move.config(state='disabled')
            confirm.config(state='disabled', bg='#4b4847')
            eval2.config(text='')
            pygame.time.delay(500)
            game_end.play()
            return
    return

root = tk.Tk()
root.geometry('800x1020')
root.title('Stockfish Engine 15.1')
root.iconbitmap('./stockfish.ico')
root.config(bg='#312e2b')

style = ttk.Style(root)
style.theme_use('alt')

# stockfish settings
s_lv = tk.IntVar()
dp = tk.IntVar()
gid = tk.StringVar()
s_lv.set(20)
dp.set(15)
gid.set('select game id')

label = tk.Label(root, text='Stockfish-15.1@github.com/archisha69', fg='#8bb24d', bg='#312e2b')
label.place(x=0, y=0)

# stockfish settings
to_skill_lv = tk.Label(root, text='Stockfish skill level:', font='Verdana 10', fg='#ffffff', bg='#312e2b')
to_skill_lv.place(x=800, y=30)
lv = [10, 15, 20]
skill_lv = tk.OptionMenu(root, s_lv, *lv)
skill_lv.place(x=950, y=25)
skill_lv.config(fg='#ffffff', bg="#3c3936", activeforeground='#ffffff', activebackground='#3c3936', font='Verdana 8')

to_depth = tk.Label(root, text='Stockfish depth:', font='Verdana 10', fg='#ffffff', bg='#312e2b')
to_depth.place(x=800, y=60)
d = [10, 15, 20]
depth = tk.OptionMenu(root, dp, *d)
depth.place(x=950, y=55)
depth.config(fg='#ffffff', bg="#3c3936", activeforeground='#ffffff', activebackground='#3c3936', font='Verdana 8')

update = tk.Button(root, text='update', font='Verdana 10', command=update_engine, fg='#ffffff', bg='#8bb24d', activeforeground='#ffffff', activebackground='#537133')
update.place(x=800, y=90)
reset = tk.Button(root, text='reset', font='Verdana 10', command=reset_engine, fg='#ffffff', bg='#3c3936', activeforeground='#ffffff', activebackground='#171614')
reset.place(x=900, y=90)

alert2 = tk.Label(root, font='Verdana 8', fg='#b23330', bg='#312e2b', justify='left')
alert2.place(x=800, y=130)

# gameplay
eval = tk.Label(root, font='Verdana 10', fg='#ffffff', bg='#312e2b')
eval.place(x=20, y=30)
style.configure('black.Vertical.TProgressbar', background='#f9fbfb', troughcolor='#403d39', pbarrelief='flat', troughrelief='flat')
evalbar = ttk.Progressbar(root, maximum=2000, value=1000, length=500, style='black.Vertical.TProgressbar', orient='vertical',)
evalbar.place(x=25, y=60)

board = tk.Label(root, text=stockfish.get_board_visual(), font='Consolas 17', fg='#ffffff', bg='#3c3936', justify='left', border=20, padx=10)
board.place(x=60, y=30)

to_eval = tk.Label(root, text='Analysis:', font='Verdana 15', fg='#ffffff', bg='#312e2b')
to_eval.place(x=600, y=30)

eval2 = tk.Label(root, font='Verdana 10', fg='#ffffff', bg='#3c3936', justify='left')
eval2.place(x=600, y=70)

to_move = tk.Label(root, text='White to move:', font='Verdana 10', fg='#8bb24d', bg='#312e2b')
to_move.place(x=600, y=250)
move = tk.Entry(root)
move.place(x=730, y=255)
confirm = tk.Button(root, text='move', font='Verdana 10', command=get_move, fg='#ffffff', bg='#8bb24d', activeforeground='#ffffff', activebackground='#537133')
confirm.place(x=900, y=250)
alert = tk.Label(root, font='Verdana 8', fg='#b23330', bg='#312e2b', justify='left')
alert.place(x=600, y=280)

flipb = tk.Button(root, text='flip board', font='Verdana 10', command=flip_board)
flipb.place(x=600, y=310)

resetb = tk.Button(root, text='reset board', font='Verdana 10', command=reset_board)
resetb.place(x=600, y=340)

fen = tk.Button(root, text='copy FEN', font='Verdana 10', command=copy_fen)
fen.place(x=600, y=370)

pgn = tk.Button(root, text='copy PGN', font='Verdana 10', command=copy_pgn)
pgn.place(x=600, y=400)

save_to_archive = tk.Button(root, text='save to archive', font='Verdana 10', command=save_game)
save_to_archive.place(x=600, y=430)

open_from_archive = tk.Button(root, text='open archive', font='Verdana 10', command=open_archive)
open_from_archive.place(x=600, y=460)

alert1 = tk.Label(root, font='Verdana 8', fg='#b23330', bg='#312e2b')
alert1.place(x=600, y=500)

get_move()
root.mainloop()

