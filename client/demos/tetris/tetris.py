import sys
from os import path
MAIN_FOLDER = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
sys.path.append(MAIN_FOLDER)
import light
import tty
import time
import random
import termios
import keyboard
import threading
import tkinter as tk


from Piece import *
from Grille import *

nbLights = 54
interfaceName = "TkinterDisplayer" # "FT232R" "TkinterDisplayer"
player = light.StaticLightsPlayer(54, interfaceName)
frame = light.YamlReader.file_to_frame(MAIN_FOLDER + "/files/yamls/reset.yaml", nbLights)
#yr.load_file(r"./light/yamls/test.yaml", player, 1000)
frame.push(player, light.MergeType.MAX, light.OffsetType.ABSOLUTE, 0)
player.start()
time.sleep(2)

grille = Grille()
pieces = []
i = 1

color_mapping = {
    0: [200,200,200,200], #ok
    1: [0,255,0,0],
    2: [255,0,255,0], #ok
    3: [255,0,0,0],
    4: [255,255,0,0], #ok
    5: [0,0,255,0],
    6: [255,128,0,0],
    7: [0,255,255,0] #ok
}

def update_grille(grille):
    for i in range(54):
        player.add(i, player.get_time() + 270, color_mapping[(grille.matrice[int(i/grille.largeur_grille)][i%grille.largeur_grille])%8], 0, 0)

def init_pieces():
    global pieces
    pieces.append(Piece(2, 3,[[6,0,0],[6,6,6]], 0, 0, 6)) #J
    pieces.append(Piece(2, 3,[[1,1,0],[0,1,1]], 0, 2, 1)) #Z
    pieces.append(Piece(2, 3,[[5,5,5],[5,0,0]], 0, 1, 5)) #L
    pieces.append(Piece(4, 1,[[7],[7],[7],[7]], 0, 4, 7)) #I
    pieces.append(Piece(3, 2,[[2,0],[2,2],[2,0]], 0, 0, 2)) #T
    pieces.append(Piece(2, 2,[[4,4],[4,4]], 0, 2, 4)) #O
    pieces.append(Piece(3, 2,[[3,0],[3,3],[0,3]], 0, 0, 3)) #S
    pieces.append(Piece(2, 3,[[0,0,5],[5,5,5]], 0, 2, 5)) #L
    pieces.append(Piece(2, 3,[[0,3,3],[3,3,0]], 0, 2, 3)) #S
    pieces.append(Piece(4, 1,[[7],[7],[7],[7]], 0, 5, 7)) #I
    pieces.append(Piece(2, 3,[[2,2,2],[0,2,0]], 0, 0, 2)) #T
    pieces.append(Piece(4, 1,[[7],[7],[7],[7]], 0, 5, 7)) #I

def random_move(grille, piece):
    move = random.randint(0, 3)

    if move == 0:
        grille.piece_rotate(piece)
    elif move == 1:
        grille.piece_left(piece)
    elif move == 2:
        grille.piece_right(piece)



init_pieces()
current_piece = pieces[0]
grille.add_piece(current_piece)

while True:
    if (i == 13):
        grille = Grille()
        pieces = []
        i = 1
        init_pieces()
        current_piece = pieces[0]
        grille.add_piece(current_piece)

    update_grille(grille)

    if not grille.piece_down(current_piece):
        grille.stuck_piece(current_piece)
        current_piece = pieces[i%12]
        i += 1
        grille.complete_row()
        grille.add_piece(current_piece)
    time.sleep(0.5)