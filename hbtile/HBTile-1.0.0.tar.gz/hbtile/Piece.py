import hexy as hx

class PieceTemplate(hx.HexTile):
    '''
    Internal class to hold basic information
    about piece types. Generated when importing
    from settings file.
    '''
    def __init__(self, health, movement_d, attack_d, power):
        self.max_health = health
        self.movement_d = movement_d
        self.attack_d = attack_d
        self.power = power

EmptyTemplate = PieceTemplate(0, 0, 0, 0)

class Piece:
    '''
    Holds information about a piece on the board.
    Stores coordinates, piece type, owner, and 
    the PlayerTemplate it is based on.
    '''
    def __init__ (self, p_type, player, direction, template = EmptyTemplate):
        self.p_type = p_type
        self.player = player
        self.health = template.max_health
        self.direction = direction
        self.template = template

    def get_max_health(self):
        return self.template.max_health

    def get_movement_distance(self):
        return self.template.movement_d

    def get_attack_distance(self):
        return self.template.attack_d

    def get_power(self):
        return self.template.power
    
EmptyPiece = Piece(0, 0, "", EmptyTemplate)
