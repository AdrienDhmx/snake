from direction import Direction
from random import randint
from action import Action

class ShortSnake:
    def __init__(self,taille,longueur=1):
        self.taille = taille
        self.longueur = longueur
        self.grille = []

        self.snake_pos = (taille // 2, taille // 2)
        self.snake_dir = Direction.EAST
        self.snake_tail = None
        if longueur == 2:
            self.snake_tail = (taille // 2 - 1, taille // 2)
        self._generer_fruit()
        self.score = 0

    def _update_grille(self):
        self.grille = []
        for i in range(self.taille):
            self.grille.append([])
            for j in range(self.taille):
                if (j, i) == self.snake_pos:
                    self.grille[i].append(str(self.snake_dir))
                elif (j, i) == self.snake_tail:
                    self.grille[i].append("o")
                elif (j, i) == self.fruit_pos:
                    self.grille[i].append("F")
                else:
                    self.grille[i].append(" ")

    def _generer_fruit(self):
        self.fruit_pos = self.snake_pos
        while(self.fruit_pos == self.snake_pos or self.fruit_pos == self.snake_tail):
            self.fruit_pos = (randint(0, self.taille - 1), randint(0, self.taille - 1))


    def move(self, action: Action):
        x, y = self.snake_pos

        match action:
            case Action.RIGHT:
                match self.snake_dir:
                    case Direction.NORTH : self.snake_dir = Direction.EAST
                    case Direction.EAST : self.snake_dir = Direction.SOUTH
                    case Direction.SOUTH : self.snake_dir = Direction.WEST
                    case Direction.WEST : self.snake_dir = Direction.NORTH
            case Action.LEFT:
                match self.snake_dir:
                    case Direction.NORTH : self.snake_dir = Direction.WEST
                    case Direction.EAST : self.snake_dir = Direction.NORTH
                    case Direction.SOUTH : self.snake_dir = Direction.EAST
                    case Direction.WEST : self.snake_dir = Direction.SOUTH

        match self.snake_dir:
            case Direction.WEST:  x -= 1
            case Direction.EAST:  x += 1
            case Direction.NORTH: y -= 1
            case Direction.SOUTH: y += 1

        if x < 0:
            self.score -= 10
            x = self.taille - 1
        elif x >= self.taille:
            self.score -= 10
            x = 0
        elif y < 0:
            self.score -= 10
            y = self.taille - 1
        elif y >= self.taille:
            self.score -= 10
            y = 0
        
        if self.longueur == 2:
            self.snake_tail = self.snake_pos

        self.snake_pos = (x, y)

        x_fruit, y_fruit = self.fruit_pos
        if(x ==x_fruit and y==y_fruit) :
            self.score += 10
            self._generer_fruit()


    def save_state(self):
        return (self.snake_pos, self.snake_tail, self.snake_dir, self.fruit_pos)

    def restore_state(self, state):
        self.snake_pos, self.snake_tail, self.snake_dir, self.fruit_pos = state

    def __str__(self):
        self._update_grille()

        affichage ="\n"
        for ligne in self.grille:
            affichage += "|" + "|".join(ligne) + "|\n"

        affichage += "Score : " + str(self.score)
        return affichage