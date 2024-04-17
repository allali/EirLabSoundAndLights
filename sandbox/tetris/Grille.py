class Grille:
    def __init__(self):
        self.hauteur_grille = 9
        self.largeur_grille = 6
        self.matrice = [[0] * self.largeur_grille for _ in range(self.hauteur_grille)]
        self.game = False

    def get_game(self):
        return self.game

    def set_game(self, game):
        self.game = game

    def add_piece(self, piece):
        if piece.play_possible(piece.get_pos_i(), piece.get_pos_j(), self.matrice, self.hauteur_grille, self.largeur_grille):
            for i in range(piece.get_hauteur()):
                for j in range(piece.get_largeur()):
                    if piece.get_matrice()[i][j] != 0:
                        self.matrice[i + piece.get_pos_i()][j + piece.get_pos_j()] = piece.get_matrice()[i][j]
            return True

        return False

    def piece_down(self, piece):
        if piece.play_possible(piece.get_pos_i() + 1, piece.get_pos_j(), self.matrice, self.hauteur_grille, self.largeur_grille):
            self.refresh(piece)
            piece.down()
            self.add_piece(piece)
            return True

        return False

    def piece_left(self, piece):
        if piece.play_possible(piece.get_pos_i(), piece.get_pos_j() - 1, self.matrice, self.hauteur_grille, self.largeur_grille):
            self.refresh(piece)
            piece.left()
            self.add_piece(piece)
            return True

        return False

    def piece_right(self, piece):
        if piece.play_possible(piece.get_pos_i(), piece.get_pos_j() + 1, self.matrice, self.hauteur_grille, self.largeur_grille):
            self.refresh(piece)
            piece.right()
            self.add_piece(piece)
            return True

        return False

    def piece_rotate(self, piece):
        if piece.rotate_possible(self.matrice, self.hauteur_grille, self.largeur_grille):
            self.refresh(piece)
            piece.rotate()
            self.add_piece(piece)
            return True

        return False

    def refresh(self, piece):
        for i in range(piece.get_hauteur()):
            for j in range(piece.get_largeur()):
                if self.matrice[piece.get_pos_i() + i][piece.get_pos_j() + j] == piece.get_number():
                    self.matrice[piece.get_pos_i() + i][piece.get_pos_j() + j] = 0

    def stuck_piece(self, piece):
        for i in range(piece.get_hauteur()):
            for j in range(piece.get_largeur()):
                if self.matrice[piece.get_pos_i() + i][piece.get_pos_j() + j] == piece.get_number():
                    self.matrice[piece.get_pos_i() + i][piece.get_pos_j() + j] += 8

    def complete_row(self):
        nb_down = 0

        for i in range(self.hauteur_grille):
            complete = all(self.matrice[i][j] != 0 for j in range(self.largeur_grille))
            if complete:
                nb_down += 1
                self.refresh_row(i)
                self.grid_down(i)

    def refresh_row(self, hauteur):
        self.matrice[hauteur] = [0] * self.largeur_grille

    def grid_down(self, hauteur):
        for i in range(hauteur, 0, -1):
            self.matrice[i] = self.matrice[i-1][:]

        self.matrice[0] = [0] * self.largeur_grille
