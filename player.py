import pygame

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('Player.png') # recuperer le lot de sprite à utiliser pour le player
        self.image = self.get_image(0, 0)                   # recueil le morceau d'image de position (0, 0)
        self.image.set_colorkey([0, 0, 0])                  # retirer le background du sprite
        self.rect = self.image.get_rect()                   # rectangle pour la position du personnage
        self.position = [x, y]                              # position du player
        self.images ={
            'down': self.get_image(0, 0),
            'left': self.get_image(0, 48),
            'right': self.get_image(0, 96),
            'up': self.get_image(0, 145)
        }
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.speed = 3                                      # vitesse de deplacement

    def save_location(self): self.old_position = self.position.copy()

    def change_animation(self, name): 
        self.image = self.images[name]
        self.image.set_colorkey([0, 0, 0])
    # deplacement du joueur
    def move_right(self): self.position[0] += self.speed

    def move_left(self): self.position[0] -= self.speed

    def move_up(self): self.position[1] -= self.speed

    def move_down(self): self.position[1] += self.speed

    def update(self) :
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        image = pygame.Surface([40, 48])    # delimite la taille du sprite d'image
        image.blit(self.sprite_sheet, (0, 0), (x, y, 40, 48))
        return image
    
