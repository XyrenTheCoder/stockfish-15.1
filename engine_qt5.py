import tkinter as tk
from tkinter import ttk
import pyperclip, platform, random, json, string, pygame
import chess, chess.engine, chess.pgn, stockfish
from stockfish import Stockfish
from datetime import date
from PIL import Image, ImageTk

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

if platform.system() == 'Windows':
    stockfish = Stockfish(path='.\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe')
elif platform.system() == 'Linux':
    stockfish = Stockfish(path='./stockfish_15.1_linux_x64/stockfish-ubuntu-20.04-x86-64')
else:
    print('OS not supported, please try to use another OS instead.') # mac bad
    exit()

# newest default values
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



def flip_board():
    global flipboard
    if flipboard != True:
        flipboard = True
        board.config(text=stockfish.get_board_visual(False))
        labelimg0.config(image=tk_board1)
    else:
        flipboard = False
        board.config(text=stockfish.get_board_visual())
        labelimg0.config(image=tk_board0)
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
        labelimg0.config(image=tk_board1)
    else:
        board.config(text=stockfish.get_board_visual())
        labelimg0.config(image=tk_board0)

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

'''
style = ttk.Style(root)
style.theme_use('alt')

# stockfish settings
s_lv = tk.IntVar()
dp = tk.IntVar()
gid = tk.StringVar()

gid.set('select game id')

# stockfish settings
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

boardimg0 = Image.open('./gfx/board_normal.png')
tk_board0 = ImageTk.PhotoImage(boardimg0)
boardimg1 = Image.open('./gfx/board_flipped.png')
tk_board1 = ImageTk.PhotoImage(boardimg1)

labelimg0 = tk.Label(root, image=tk_board0, border=0)
labelimg0.place(x=60, y=30)

board = tk.Label(root, text=stockfish.get_board_visual(), font='Consolas 17', fg='#ffffff', bg='#3c3936', justify='left', border=20, padx=10)
# board.place(x=60, y=30)

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
'''


qss = """
QMenuBar {
    background-color: #4b4847;
}
QMenuBar::item {
    spacing: 5px;
    padding: 2px 10px;
    background-color: #4b4847;
    color: white;
    border-radius: 1px;
}
QMenuBar::item:selected {
    background-color: #8bb24d;
}
QMenuBar::item:pressed {
    background: #537133;
}

/* ------------------------------- */

QMenu {
    background-color: #4b4847;
    border: 1px solid black;
    margin: 2px;
}
QMenu::item {
    background-color: #4b4847;
    color: white;
}
QMenu::item:selected {
    background-color: #8bb24d;
    color: white;
}
"""

dropdownss = """
QComboBox QAbstractItemView {
    selection-background-color: #8bb24d;
    selection-color: white;
    background-color: #4b4847;
    color: white;
}
QComboBox {
    background-color: #4b4847;
    color: white;
    border: 1px solid black;
    margin: 2px;
}
QComboBox::drop-down {
    width: 15px;
    color: white;
}
"""

buttonss = """
QPushButton {
    background-color: #8bb24d;
    color: white;
    border: 1px solid black;
    margin: 2px;
    width: 25px;
    height: 20px;
}
QPushButton::pressed {
    background-color: #537133;
    color: white;
}
"""

sliderss = """
QSlider::groove:horizontal {
    background-color: #4b4847;
    border: 1px solid black;
    height: 23px;
    margin: 0px;
}
QSlider::handle:horizontal {
    background-color: #8bb24d;
    border: 1px solid black;
    height: 10px;
    width: 10px;
    margin: 0px 0px;
}
"""

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def open_engine(self):
        self.engine_win_o.show()

    def open_archive(self):
        self.archive_win_o.show()

    def reset_board():
        moved.clear()
        stockfish.set_fen_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        if flipboard == True:
            board.config(text=stockfish.get_board_visual(False))
            labelimg0.config(image=tk_board1)
        else:
            board.config(text=stockfish.get_board_visual())
            labelimg0.config(image=tk_board0)
        alert1.config(text='Resetted board.')
        get_move()
        return

    def initUI(self):
        self.setWindowTitle('Stockfish Engine 15.1')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 1200, 1200)
        self.setStyleSheet("background-color:#312e2b;")

        menuBar = self.menuBar()
        archiveMenu = QMenu("&Options", self)
        new_game = QAction("New Game", self)
        new_game.triggered.connect(self.reset_board)

        o_archivewin = QAction("Open archive", self)
        o_archivewin.triggered.connect(self.open_archive)
        self.archive_win_o = archive_win()

        archiveMenu.addAction(o_archivewin)
        archiveMenu.addAction('Save current game')

        editMenu = QMenu("&Edit engine", self)
        o_enginewin = QAction("Edit", self)
        o_enginewin.triggered.connect(self.open_engine)
        self.engine_win_o = engine_win()

        editMenu.addAction(o_enginewin)

        menuBar.addMenu(archiveMenu)
        menuBar.addMenu(editMenu)

        self.label = QLabel('Stockfish-15.1@github.com/archisha69', self)
        self.label.setStyleSheet("color:#8bb24d;")
        self.label.setFont(QFont('Verdana', 8))
        self.label.move(0, 30)
        self.label.adjustSize()

        self.showMaximized()

class engine_win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget()

    def update_engine(self):
        stockfish.update_engine_parameters({'Skill Level':int(self.skill_lv.currentText()), "Threads":int(self.threads.currentText()), "Minimum Thinking Time":int(self.mtt.currentText()), "Move Overhead":int(self.moh.currentText()), "UCI_Elo":int(self.elo.value())})
        stockfish.set_depth(int(self._depth.currentText()))
        self.note.setText(json.dumps(stockfish.get_parameters(), indent=4))
        #alert2.config(text='Updated engine parameters successfully!\nPlease mind that the settings may affect engine performance.')
        self.close()
        #get_move()
        return

    def reset_engine(self):
        stockfish.reset_engine_parameters()
        self.skill_lv.setCurrentText(str(stockfish.get_parameters()["Skill Level"]))
        self._depth.setCurrentText('15')
        self.mtt.setCurrentText(str(stockfish.get_parameters()["Minimum Thinking Time"]))
        self.moh.setCurrentText(str(stockfish.get_parameters()["Move Overhead"]))
        self.elo.setValue(stockfish.get_parameters()["UCI_Elo"])
        self.threads.setCurrentText(str(stockfish.get_parameters()["Threads"]))
        self.note.setText(json.dumps(stockfish.get_parameters(), indent=4))
        #alert2.config(text='Resetted engine parameters.')
        self.close()
        return

    def valuechange(self):
        self.elo_label.setText(str(self.elo.value()))
        return

    def widget(self):
        self.setWindowTitle('Stockfish Settings')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 900, 500)
        self.setStyleSheet("background-color:#312e2b;")

        # stockfish settings
        self.skill_lv_label = QLabel('Stockfish Skill Level:', self)
        self.skill_lv_label.setStyleSheet("color:#ffffff;")
        self.skill_lv_label.setFont(QFont('Verdana', 10))
        self.skill_lv_label.move(10, 10)
        self.skill_lv_label.adjustSize()

        self.skill_lv = QComboBox(self)
        self.skill_lv.addItems(['10', '15', '20'])
        self.skill_lv.setStyleSheet(dropdownss)
        self.skill_lv.setFont(QFont('Verdana', 10))
        self.skill_lv.setCurrentText('20')
        self.skill_lv.move(300, 10)

        self.depth_label = QLabel('Stockfish Depth:', self)
        self.depth_label.setStyleSheet("color:#ffffff;")
        self.depth_label.setFont(QFont('Verdana', 10))
        self.depth_label.move(10, 60)
        self.depth_label.adjustSize()

        self._depth = QComboBox(self)
        self._depth.addItems(['10', '15', '20'])
        self._depth.setStyleSheet(dropdownss)
        self._depth.setFont(QFont('Verdana', 10))
        self._depth.setCurrentText('15')
        self._depth.move(300, 60)

        self.mtt_label = QLabel('Minimum Thinking Time:', self)
        self.mtt_label.setStyleSheet("color:#ffffff;")
        self.mtt_label.setFont(QFont('Verdana', 10))
        self.mtt_label.move(10, 110)
        self.mtt_label.adjustSize()

        self.mtt = QComboBox(self)
        self.mtt.addItems(['10', '20', '30', '40', '50', '60'])
        self.mtt.setStyleSheet(dropdownss)
        self.mtt.setFont(QFont('Verdana', 10))
        self.mtt.setCurrentText('20')
        self.mtt.move(300, 110)

        self.moh_label = QLabel('Move Overhead:', self)
        self.moh_label.setStyleSheet("color:#ffffff;")
        self.moh_label.setFont(QFont('Verdana', 10))
        self.moh_label.move(10, 160)
        self.moh_label.adjustSize()

        self.moh = QComboBox(self)
        self.moh.addItems(['10', '20', '30', '40'])
        self.moh.setStyleSheet(dropdownss)
        self.moh.setFont(QFont('Verdana', 10))
        self.moh.setCurrentText('10')
        self.moh.move(300, 160)

        self.uci_elo_label = QLabel('Stockfish UCI Elo:', self)
        self.uci_elo_label.setStyleSheet("color:#ffffff;")
        self.uci_elo_label.setFont(QFont('Verdana', 10))
        self.uci_elo_label.move(10, 210)
        self.uci_elo_label.adjustSize()

        self.elo = QSlider(Qt.Horizontal, self)
        self.elo.setMinimum(250)
        self.elo.setMaximum(3200)
        self.elo.setValue(1350)
        self.elo.setSingleStep(250)
        self.elo.setTickPosition(QSlider.TicksBelow)
        self.elo.setTickInterval(320)
        self.elo.setStyleSheet(sliderss)
        self.elo.move(300, 210)

        self.elo.valueChanged.connect(self.valuechange)

        self.elo_label = QLabel(str(self.elo.value()), self)
        self.elo_label.setStyleSheet("color:#ffffff;")
        self.elo_label.setFont(QFont('Verdana', 8))
        self.elo_label.move(420, 215)
        self.elo_label.adjustSize()

        self.threads_label = QLabel('Threads Usage:', self)
        self.threads_label.setStyleSheet("color:#ffffff;")
        self.threads_label.setFont(QFont('Verdana', 10))
        self.threads_label.move(10, 260)
        self.threads_label.adjustSize()

        self.threads = QComboBox(self)
        self.threads.addItems(['1', '2', '3', '4'])
        self.threads.setStyleSheet(dropdownss)
        self.threads.setFont(QFont('Verdana', 10))
        self.threads.setCurrentText('1')
        self.threads.move(300, 260)

        self._update = QPushButton('Update Engine', self)
        self._update.setGeometry(0, 190, 200, 50)
        self._update.setStyleSheet(buttonss)
        self._update.setFont(QFont('Verdana', 10))
        self._update.clicked.connect(self.update_engine)
        self._update.move(10, 310)

        self._reset = QPushButton('Reset Engine', self)
        self._reset.setGeometry(0, 190, 200, 50)
        self._reset.setStyleSheet(buttonss)
        self._reset.setFont(QFont('Verdana', 10))
        self._reset.clicked.connect(self.reset_engine)
        self._reset.move(250, 310)

        self.note0 = QLabel('Current Parameters:', self)
        self.note0.setStyleSheet("color:#ffffff;")
        self.note0.setFont(QFont('Verdana', 10))
        self.note0.move(500, 10)
        self.note0.adjustSize()

        self.note = QLabel(json.dumps(stockfish.get_parameters(), indent=4), self)
        self.note.setStyleSheet("color:#ffffff;")
        self.note.setFont(QFont('Verdana', 8))
        self.note.move(500, 60)
        self.note.adjustSize()

class archive_win(QMainWindow):
    ...


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qss)
    w = main()
    w.show()
    sys.exit(app.exec_())
