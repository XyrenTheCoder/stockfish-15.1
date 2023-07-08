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

'''
style = ttk.Style(root)
style.theme_use('alt')

# stockfish settings
s_lv = tk.IntVar()
dp = tk.IntVar()
gid = tk.StringVar()

gid.set('select game id')

# stockfish settings
alert2 = tk.Label(root, font='Verdana 8', fg='#b23330', bg='#312e2b', justify='left')
alert2.place(x=800, y=130)

# gameplay
eval2 = tk.Label(root, font='Verdana 10', fg='#ffffff', bg='#3c3936', justify='left')
eval2.place(x=600, y=70)


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

evalbarss = """
QProgressBar {
    background-color: #403d39;
    border: 0px;
}
QProgressBar::chunk {
    background-color: #f9fbfb;
}
"""

flipboardss = """
QPushButton {
    background-image: url(./gfx/btn-flip.png);
    background-color: #4b4847;
    border: 1px solid black;
}
QPushButton::pressed {
    background-image: url(./gfx/btn-flip-pressed.png);
    background-color: #3c3936;
}
"""

sharegamess = """
QPushButton {
    background-image: url(./gfx/btn-share.png);
    background-color: #4b4847;
    border: 1px solid black;
}
QPushButton::pressed {
    background-image: url(./gfx/btn-share-pressed.png);
    background-color: #3c3936;
}
"""

copyfenss = """
QPushButton {
    background-image: url(./gfx/btn-copy.png);
    background-color: #4b4847;
    border: 1px solid black;
}
QPushButton::pressed {
    background-image: url(./gfx/btn-copy-pressed.png);
    background-color: #3c3936;
}
"""
class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setFont(QFont('Verdana', 10))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.resize(350, 550)
        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

    def setFont(self, font):
        self.label.setFont(font)

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.get_move()

    # variables and functions
    global moved
    board2 = chess.Board()
    moved = []
    flipboard = False

    def set_board(self, fen):
        for k in range(1, 65):
            a = getattr(self, ("sq%2d" % k).replace(" ", ""))
            a.clear()
        square = 0
        fenshort = str(fen.split()[0].replace('/', ''))
        if self.flipboard == False:
            for i in fenshort:
                square += 1
                if i.isdigit():
                    for j in range(fenshort.find(i)+1, int(i)):
                        eval(f'self.sq{j}.setPixmap(self.empty)')
                    square += int(i)-1
                else:
                    eval(f'self.sq{square}.setPixmap(self.{i})')
        else:
            fenflipped = fenshort[::1]
            for i in fenflipped:
                square += 1
                if i.isdigit():
                    for j in range(fenflipped.find(i), int(i)):
                        eval(f'self.sq{j}.setPixmap(self.empty)')
                    square += int(i)-1
                else:
                    eval(f'self.sq{square}.setPixmap(self.{i})')

    def open_engine(self):
        self.engine_win_o.show()

    def open_share(self):
        self.share_win_o.show()
        self.share_win_o.pgnbox.clear()
        self.share_win_o.fenbox.setText(stockfish.get_fen_position())
        self.share_win_o.pgnbox.insertPlainText(share_win.get_pgn(self))

    def open_archive(self):
        self.archive_win_o.show()
        self.archive_win_o.archlist.setText('\n'.join(self.archive_win_o.get_archive()))
        self.archive_win_o.gamelist.clear()
        self.archive_win_o.gamelist.addItems(self.archive_win_o.get_archive())
        self.archive_win_o.gamelist.setCurrentText('-- Select ID --')
        self.archive_win_o.vis.clear()

    def save_game(self):
        a = string.ascii_letters + string.ascii_letters
        gameid = '@'
        for i in range(9):
            gameid += random.choice(a)
        if gameid in archive:
            return self.save_game()
        else:
            archive[gameid] = stockfish.get_fen_position()
            with open('./archive.json', 'w') as f:
                json.dump(archive, f, indent=4)
            f.close()
        self.mainStatusBar.showMessage(f"Saved game {gameid} to archive!", 2000)
        return

    def reset_board(self):
        moved.clear()
        stockfish.set_fen_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.check_flip()
        self.get_move()
        game_start.play()
        self.mainStatusBar.showMessage('Resetted board.', 2000)
        return

    def check_flip(self):
        if self.flipboard == True:
            self.board_placeholder.setPixmap(self.boardb)
            self.set_board(stockfish.get_fen_position().split()[0][::-1])
        else:
            self.board_placeholder.setPixmap(self.boardw)
            self.set_board(stockfish.get_fen_position())

    def flip_board(self):
        if self.flipboard != True:
            self.flipboard = True
            self.board_placeholder.setPixmap(self.boardb)
            self.set_board(stockfish.get_fen_position().split()[0][::-1])
        else:
            self.flipboard = False
            self.set_board(stockfish.get_fen_position())
            self.board_placeholder.setPixmap(self.boardw)
        return

    def rt_moves(self):
        p = ''
        pgn = share_win.get_pgn(self).split(']\n')[7]
        grouped = list(zip(*[iter(pgn.split())]*3))
        for i in grouped:
            p += '      '.join(i)+'\n'
        self.movelist.setText(p)

    def get_move(self):
        self.confirm.setEnabled(True)
        self.movepiece.setReadOnly(False)
        self.confirm.setStyleSheet(buttonss)
        self.alert.clear()
        play_move = self.movepiece.text().strip()

        if len(play_move) == 0:
            self.mainStatusBar.showMessage('Generated new best moves.', 2000)
        elif stockfish.is_move_correct(play_move) and play_move != '':
            if self.board2.gives_check(chess.Move.from_uci(play_move)):
                piece_check.play()
            elif play_move == 'e1g1' or play_move == 'e1c1' or play_move == 'e8g8' or play_move == 'e8c8':
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

            stockfish.make_moves_from_current_position([play_move])
            self.board2.push(chess.Move.from_uci(play_move))
            moved.append(chess.Move.from_uci(play_move))
            self.rt_moves()
        else:
            self.alert.setText(f'Move {play_move} is an illegal move or is not an UCI move.')

        if stockfish.get_fen_position().split()[1] == 'b':
            self.to_move.setText('Black To Move:')
        else:
            self.to_move.setText('White To Move:')

        self.movepiece.clear()
        self.check_flip()

        # get top 3 engine moves
        top_moves = ''
        num = 1
        for i in stockfish.get_top_moves(3):
            if i['Centipawn'] == None:
                top_moves += f"{num}. {i['Move']} ======== {i['Mate']}\n"
                num = num + 1
            else:
                top_moves += f"{num}. {i['Move']} -------- {i['Centipawn'] / 100}\n"
                num = num + 1
        self.eval2.setText(top_moves)

        # stockfish evaluation
        evaluation = stockfish.get_evaluation()
        evalpos = evaluation['value']
        if evaluation['type'] == 'cp':
            self.evalnum.setText(str(evalpos / 100)) #centipawn
            scale = evalpos + 1000 #max 2000, min 0, w -1000, b -1000
            self.evalbar.setValue(scale)
        else:
            if evalpos > 0: #white mate in x
                self.evalnum.setText(f"M{evaluation['value']}")
                self.evalbar.setValue(2000)
            elif evalpos < 0: #black mate in x
                self.evalnum.setText(f"M{evaluation['value']}")
                self.evalbar.setValue(0)
            else: #mate in 0, checkmated
                if stockfish.get_fen_position().split(' ')[1] == 'w':
                    self.evalnum.setText("0-1")
                    self.evalbar.setValue(0)
                else:
                    self.evalnum.setText("1-0")
                    self.evalbar.setValue(2000)
                self.confirm.setEnabled(False)
                self.movepiece.setReadOnly(True)
                self.confirm.setStyleSheet("background-color:#537133;")
                self.eval2.setText('')
                pygame.time.delay(500)
                game_end.play()
                return
        return

    def initUI(self):
        self.setWindowTitle('Stockfish Engine 15.1')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 1200, 1200)
        self.setStyleSheet("background-color:#312e2b;")

        self.mainStatusBar = QStatusBar(self)
        self.setStatusBar(self.mainStatusBar)
        self.mainStatusBar.setStyleSheet("background-color: #4b4847; color: white;")
        self.mainStatusBar.setFont(QFont('Verdana', 8))

        # top menubar
        menuBar = self.menuBar()

        # Options tab
        optionMenu = QMenu("&Game Options", self)

        new_game = QAction("New Game", self)
        new_game.triggered.connect(self.reset_board)

        o_archivewin = QAction("Open Archive", self)
        o_archivewin.triggered.connect(self.open_archive)
        self.archive_win_o = archive_win()

        save_g = QAction("Save Game To Archive", self)
        save_g.triggered.connect(self.save_game)

        optionMenu.addAction(new_game)
        optionMenu.addAction(o_archivewin)
        optionMenu.addAction(save_g)

        # Edit engine tab
        editMenu = QMenu("&Edit Engine", self)

        o_enginewin = QAction("Edit", self)
        o_enginewin.triggered.connect(self.open_engine)
        self.engine_win_o = engine_win()

        editMenu.addAction(o_enginewin)

        menuBar.addMenu(optionMenu)
        menuBar.addMenu(editMenu)

        # top label, this does nothing
        self.label = QLabel('Stockfish-15.1@github.com/archisha69', self)
        self.label.setStyleSheet("color:#8bb24d;")
        self.label.setFont(QFont('Verdana', 8))
        self.label.move(0, 30)
        self.label.adjustSize()

        # stockfish eval bar
        self.evalnum = QLabel(self)
        self.evalnum.setStyleSheet("color:white;")
        self.evalnum.setFont(QFont('Verdana', 10))
        self.evalnum.move(20, 60)

        self.evalbar = QProgressBar(self)
        self.evalbar.setGeometry(23, 100, 30, 800)
        self.evalbar.setRange(0, 2000) #max 2000, min 0, w -1000, b -1000
        self.evalbar.setValue(1000)
        self.evalbar.setStyleSheet(evalbarss)
        self.evalbar.setTextVisible(False)
        self.evalbar.setOrientation(Qt.Vertical)

        # board
        self.boardw = QPixmap('./gfx/board_normal.png')
        self.boardb = QPixmap('./gfx/board_flipped.png')
        self.board_placeholder = QLabel(self)
        self.board_placeholder.move(60, 100)
        self.board_placeholder.setPixmap(self.boardw)
        self.board_placeholder.resize(self.boardw.width(), self.boardw.height())

        # pieces
        x = 0
        y = 1
        for i in range(1, 65):
            setattr(self, ("sq%2d" % i).replace(" ", ""), QLabel(self))
            a = getattr(self, ("sq%2d" % i).replace(" ", ""))
            a.move(60+100*x, 100*y)
            a.resize(100, 100)
            a.setAttribute(Qt.WA_TranslucentBackground)
            x += 1
            if i % 8 == 0:
                x = 0
                y += 1

        self.P = QPixmap('./gfx/piece-pw.png')
        self.R = QPixmap('./gfx/piece-rw.png')
        self.N = QPixmap('./gfx/piece-nw.png')
        self.B = QPixmap('./gfx/piece-bw.png')
        self.Q = QPixmap('./gfx/piece-qw.png')
        self.K = QPixmap('./gfx/piece-kw.png')
        self.p = QPixmap('./gfx/piece-pb.png')
        self.r = QPixmap('./gfx/piece-rb.png')
        self.n = QPixmap('./gfx/piece-nb.png')
        self.b = QPixmap('./gfx/piece-bb.png')
        self.q = QPixmap('./gfx/piece-qb.png')
        self.k = QPixmap('./gfx/piece-kb.png')
        self.empty = QPixmap('./gfx/piece-empty.png')

        self.to_eval = QLabel("Analysis:", self)
        self.to_eval.setStyleSheet("color:white;")
        self.to_eval.setFont(QFont('Verdana', 10))
        self.to_eval.move(900, 100)
        self.to_eval.adjustSize()

        self.eval2 = QLabel(self)
        self.eval2.setStyleSheet("color:white; background-color:#3c3936; padding-left:20px; padding-top:5px;")
        self.eval2.setFont(QFont('Verdana', 10))
        self.eval2.resize(350, 100)
        self.eval2.move(900, 140)

        self.movelist = ScrollLabel(self)
        self.movelist.setStyleSheet("color:white; background-color: #3c3936;")
        self.movelist.resize(350, 550)
        self.movelist.move(900, 240)

        # move pieces
        self.to_move = QLabel("White To Move:", self)
        self.to_move.setStyleSheet("color:white;")
        self.to_move.setFont(QFont('Verdana', 10))
        self.to_move.move(900, 800)
        self.to_move.adjustSize()

        self.movepiece = QLineEdit(self)
        self.movepiece.setStyleSheet("color:white; background-color: #4b4847;")
        self.movepiece.setFont(QFont('Verdana', 8))
        self.movepiece.move(1100, 800)
        self.movepiece.resize(100, 30)

        self.confirm = QPushButton('Move', self)
        self.confirm.setGeometry(1250, 790, 100, 50)
        self.confirm.setStyleSheet(buttonss)
        self.confirm.setFont(QFont('Verdana', 10))
        self.confirm.clicked.connect(self.get_move)

        self.alert = QLabel(self)
        self.alert.setStyleSheet("color:#b23330;")
        self.alert.setFont(QFont('Verdana', 8))
        self.alert.resize(900, 30)
        self.alert.move(900, 840)

        # flip board
        self.flip = QPushButton(self)
        self.flip.setGeometry(60, 900, 50, 50)
        self.flip.setToolTip('Flip Board')
        self.flip.setStyleSheet(flipboardss)
        self.flip.clicked.connect(self.flip_board)

        # share game
        self.share = QPushButton(self)
        self.share.setGeometry(110, 900, 50, 50)
        self.share.setToolTip('Share Game')
        self.share.setStyleSheet(sharegamess)
        self.share.clicked.connect(self.open_share)
        self.share_win_o = share_win()

        self.showMaximized()

class share_win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget()

    def get_pgn(self):
        today = date.today()
        game = chess.pgn.Game()
        #game.headers["Event"] = "Stockfish Engine 15.1"
        game.headers["Site"] = "https://github.com/archisha69/stockfish-15.1"
        game.headers["Date"] = today.strftime("%Y.%m.%d")
        #game.headers["Round"] = "0"
        game.headers["White"] = "Stockfish Engine 15.1"
        game.headers["Black"] = "Stockfish Engine 15.1"
        try:
            node = game.add_variation(moved[0])
            for m in moved[1:]:
                node = node.add_variation(m)
        except IndexError:
            #alert1.config(text='PGN empty!')
            pass
        finally:
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn = game.accept(exporter)
        return pgn

    def copy_fen(self):
        pyperclip.copy(stockfish.get_fen_position())
        self.mainStatusBar.showMessage('Copied FEN from current position!', 2000)
        return

    def copy_pgn(self):
        pyperclip.copy(self.get_pgn())
        self.mainStatusBar.showMessage('Copied PGN from current position!', 2000)
        return

    def widget(self):
        self.setWindowTitle('Share Game')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 700, 800)
        self.setStyleSheet("background-color:#312e2b;")

        self.mainStatusBar = QStatusBar(self)
        self.setStatusBar(self.mainStatusBar)
        self.mainStatusBar.setStyleSheet("background-color: #4b4847; color: white;")
        self.mainStatusBar.setFont(QFont('Verdana', 8))

        self.fenlabel = QLabel("FEN", self)
        self.fenlabel.setStyleSheet("color:white;")
        self.fenlabel.setFont(QFont('Verdana', 10))
        self.fenlabel.move(10, 10)

        self.fenbox = QLineEdit(self)
        self.fenbox.setStyleSheet("color:white; background-color: #4b4847;")
        self.fenbox.setFont(QFont('Verdana', 8))
        self.fenbox.setReadOnly(True)
        self.fenbox.move(10, 50)
        self.fenbox.resize(600, 40)
        self.fenbox.setText(stockfish.get_fen_position())

        self.copyfen = QPushButton(self)
        self.copyfen.setGeometry(610, 45, 50, 50)
        self.copyfen.setStyleSheet(copyfenss)
        self.copyfen.clicked.connect(self.copy_fen)

        self.pgnlabel = QLabel("PGN", self)
        self.pgnlabel.setStyleSheet("color:white;")
        self.pgnlabel.setFont(QFont('Verdana', 10))
        self.pgnlabel.move(10, 100)

        self.pgnbox = QPlainTextEdit(self)
        self.pgnbox.setStyleSheet("color:white; background-color: #4b4847;")
        self.pgnbox.setFont(QFont('Verdana', 8))
        self.pgnbox.setReadOnly(True)
        self.pgnbox.move(10, 140)
        self.pgnbox.resize(600, 500)
        self.pgnbox.insertPlainText(self.get_pgn())

        self.copypgn = QPushButton(self)
        self.copypgn.setGeometry(610, 140, 50, 50)
        self.copypgn.setStyleSheet(copyfenss)
        self.copypgn.clicked.connect(self.copy_pgn)

class engine_win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget()

    def update_engine(self):
        stockfish.update_engine_parameters({'Skill Level':int(self.skill_lv.currentText()), "Threads":int(self.threads.currentText()), "Minimum Thinking Time":int(self.mtt.currentText()), "Move Overhead":int(self.moh.currentText()), "UCI_Elo":int(self.elo.value())})
        stockfish.set_depth(int(self._depth.currentText()))
        self.note.setText(json.dumps(stockfish.get_parameters(), indent=4))
        self.close()
        w.mainStatusBar.showMessage('Updated engine parameters successfully!', 2000)
        w.get_move()
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
        self.close()
        w.mainStatusBar.showMessage('Resetted engine parameters.', 2000)
        w.get_move()
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

        # action buttons
        self._update = QPushButton('Update Engine', self)
        self._update.setGeometry(10, 310, 200, 50)
        self._update.setStyleSheet(buttonss)
        self._update.setFont(QFont('Verdana', 10))
        self._update.clicked.connect(self.update_engine)

        self._reset = QPushButton('Reset Engine', self)
        self._reset.setGeometry(260, 310, 200, 50)
        self._reset.setStyleSheet(buttonss)
        self._reset.setFont(QFont('Verdana', 10))
        self._reset.clicked.connect(self.reset_engine)

        # show parameters
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
    def __init__(self):
        super().__init__()
        self.widget()
        self.mainStatusBar.showMessage("Type in dropdown to search ID!")

    def get_archive(self):
        with open('./archive.json', 'r') as f:
            archive = json.load(f)
        f.close()
        g = list(archive)
        return g

    def show_preview(self):
        self.vis.setText(str(chess.Board(archive[self.gamelist.currentText()])))
        return

    def confirm_open(self):
        if self.gamelist.currentText() == "-- Select ID --":
            self.mainStatusBar.showMessage("No game selected.", 2000)
            return
        else:
            self.retrieve_win_o.warn.setText(f"Are you sure to open game {self.gamelist.currentText()}?\nThe current game will be lost if not saved.")
            self.retrieve_win_o.confirm.clicked.connect(self.retrieve_win_o.retrieve_game)
            self.retrieve_win_o.show()

    def confirm_delete(self):
        if self.gamelist.currentText() == "-- Select ID --":
            self.mainStatusBar.showMessage("No game selected.", 2000)
            return
        else:
            self.retrieve_win_o.warn.setText(f"Are you sure to delete game {self.gamelist.currentText()}?\nThis action cannot be recovered.")
            self.retrieve_win_o.confirm.clicked.connect(self.retrieve_win_o.delete_game)
            self.retrieve_win_o.show()

    def widget(self):
        self.setWindowTitle('Game Archive')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 700, 800)
        self.setStyleSheet("background-color:#312e2b;")

        self.mainStatusBar = QStatusBar(self)
        self.setStatusBar(self.mainStatusBar)
        self.mainStatusBar.setStyleSheet("background-color: #4b4847; color: white;")
        self.mainStatusBar.setFont(QFont('Verdana', 8))

        self.label = QLabel("Game List", self)
        self.label.setStyleSheet("color:white;")
        self.label.setFont(QFont('Verdana', 10))
        self.label.move(10, 10)
        self.label.adjustSize()

        self.archlist = ScrollLabel(self)
        self.archlist.setFont(QFont('Verdana', 8))
        self.archlist.setStyleSheet("color:white; background-color: #3c3936;")
        self.archlist.resize(190, 490)
        self.archlist.move(10, 50)

        self.selectlabel = QLabel("Select Game:", self)
        self.selectlabel.setStyleSheet("color:white;")
        self.selectlabel.setFont(QFont('Verdana', 10))
        self.selectlabel.move(210, 50)
        self.selectlabel.adjustSize()

        self.gamelist = QComboBox(self)
        self.gamelist.setEditable(True)
        self.gamelist.setStyleSheet(dropdownss)
        self.gamelist.setFont(QFont('Verdana', 10))
        self.gamelist.resize(170, 30)
        self.gamelist.move(410, 50)
        self.gamelist.activated.connect(self.show_preview)

        # search
        line_edit = self.gamelist.lineEdit()
        line_edit.setFont(QFont('Verdana', 10))

        self.gamelist.setInsertPolicy(QComboBox.NoInsert)
        self.gamelist.completer().setCompletionMode(QCompleter.PopupCompletion)

        # game preview
        self.arrow = QLabel('Preview', self)
        self.arrow.setStyleSheet("color:white;")
        self.arrow.setFont(QFont('Verdana', 8))
        self.arrow.move(210, 90)

        self.vis = QLabel(self)
        self.vis.setStyleSheet("color:#8bb24d; background-color:#4b4847;")
        self.vis.setFont(QFont('Consolas', 18))
        self.vis.setAlignment(Qt.AlignCenter)
        self.vis.resize(370, 370)
        self.vis.move(210, 120)

        # action buttons
        self.open = QPushButton('Open Game', self)
        self.open.setGeometry(210, 500, 150, 50)
        self.open.setStyleSheet(buttonss)
        self.open.setFont(QFont('Verdana', 10))
        self.open.clicked.connect(self.confirm_open)

        self.delete = QPushButton('Delete Game', self)
        self.delete.setGeometry(430, 500, 150, 50)
        self.delete.setStyleSheet(buttonss)
        self.delete.setFont(QFont('Verdana', 10))
        self.delete.clicked.connect(self.confirm_delete)
        self.retrieve_win_o = confirm_win()

class confirm_win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget()

    def retrieve_game(self):
        gameid = w.archive_win_o.gamelist.currentText()
        fen = archive[f'{gameid}']
        stockfish.set_fen_position(fen)
        w.set_board(stockfish.get_fen_position())
        w.mainStatusBar.showMessage(f"Opened game {gameid} from archive!")
        w.get_move()
        self.destroy()
        w.archive_win_o.destroy()
        return

    def delete_game(self):
        gameid = w.archive_win_o.gamelist.currentText()
        if gameid in archive:
            del archive[gameid]
            with open('./archive.json', 'w') as f:
                json.dump(archive, f, indent=4)
            f.close()
            w.mainStatusBar.showMessage(f"Deleted game {gameid} from archive!")
            w.get_move()
            self.destroy()
            w.archive_win_o.destroy()
            return
        else:
            w.archive_win_o.mainStatusBar.showMessage(f'Game {gameid} does not exist.')

    def widget(self):
        self.setWindowTitle('Confirm')
        self.setWindowIcon(QIcon('./gfx/stockfish.ico'))
        self.setGeometry(100, 100, 570, 400)
        self.setFixedSize(570, 150)
        self.setStyleSheet("background-color:#312e2b;")

        self.mainStatusBar = QStatusBar(self)
        self.setStatusBar(self.mainStatusBar)
        self.mainStatusBar.setStyleSheet("background-color: #4b4847; color: white;")
        self.mainStatusBar.setFont(QFont('Verdana', 8))

        self.warn = QLabel(self)
        self.warn.setStyleSheet("color:white;background-color:#bbbbbb;")
        self.warn.setFont(QFont('Verdana', 10))
        self.warn.setAlignment(Qt.AlignCenter)
        self.warn.resize(550, 70)
        self.warn.move(10, 20)

        self.confirm = QPushButton('Confirm', self)
        self.confirm.setGeometry(240, 100, 100, 50)
        self.confirm.setToolTip('Confirm')
        self.confirm.setStyleSheet(buttonss)
        self.confirm.setFont(QFont('Verdana', 10))

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qss)
    w = main()
    w.show()
    sys.exit(app.exec_())
