class Piece:
    def __init__(self, hauteur, largeur, matrice, pos_i, pos_j, number):
        self.hauteur = hauteur
        self.largeur = largeur
        self.matrice = matrice
        self.pos_i = pos_i
        self.pos_j = pos_j
        self.number = number

    def get_hauteur(self):
        return self.hauteur

    def get_largeur(self):
        return self.largeur

    def get_matrice(self):
        return self.matrice

    def get_pos_i(self):
        return self.pos_i

    def get_pos_j(self):
        return self.pos_j

    def get_number(self):
        return self.number

    def rotate(self):
        self.matrice = [list(row) for row in zip(*self.matrice[::-1])]
        self.hauteur, self.largeur = self.largeur, self.hauteur

    def left(self):
        self.pos_j -= 1

    def right(self):
        self.pos_j += 1

    def down(self):
        self.pos_i += 1

    def play_possible(self, x, y, grille, hauteur_grille, largeur_grille):
        for i in range(self.hauteur):
            for j in range(self.largeur):
                if self.matrice[i][j] != 0:
                    if not self.in_board(x + i, y + j, grille, hauteur_grille, largeur_grille):
                        return False
        return True

    def in_board(self, x, y, grille, hauteur_grille, largeur_grille):
        if 0 <= x < hauteur_grille and 0 <= y < largeur_grille:
            if grille[x][y] == 0 or grille[x][y] == self.number:
                return True
        return False

    def rotate_possible(self, grille, hauteur_grille, largeur_grille):
        for i in range(self.largeur):
            for j in range(self.hauteur):
                if not self.in_board(self.pos_i + i, self.pos_j + j, grille, hauteur_grille, largeur_grille):
                    return False
        return True
