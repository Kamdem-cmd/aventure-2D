import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Chargement de la feuille de sprites
        self.sprite_sheet = pygame.image.load('Player.png')
        
        # Paramètres d'animation
        self.animation_frames = {
            'down': [],
            'left': [],
            'right': [],
            'up': []
        }
        self.animation_speed = 0.15  # Vitesse de l'animation
        self.current_frame = 0
        self.animation_timer = 0
        self.current_direction = 'down'
        
        # Initialisation des animations
        self.load_animations()
        self.image = self.animation_frames['down'][0]
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]
        
        # Pour les collisions
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.speed = 3
        self.moving = False  # Pour savoir si le joueur est en mouvement

    def load_animations(self):
        """Charge toutes les frames d'animation pour chaque direction"""
        # Chaque direction a 3 frames d'animation (0, 1, 2)
        for i in range(3):
            # Animation vers le bas
            frame = self.get_image(i * 48, 0)
            self.animation_frames['down'].append(frame)
            
            # Animation vers la gauche
            frame = self.get_image(i * 48, 48)
            self.animation_frames['left'].append(frame)
            
            # Animation vers la droite
            frame = self.get_image(i * 48, 96)
            self.animation_frames['right'].append(frame)
            
            # Animation vers le haut
            frame = self.get_image(i * 48, 144)  # Note: 145 corrigé en 144 pour l'alignement
            self.animation_frames['up'].append(frame)

    def animate(self, direction):
        """Gère l'animation dans la direction donnée"""
        self.current_direction = direction
        self.animation_timer += self.animation_speed
        
        if self.moving:  # Animation seulement si le joueur bouge
            if self.animation_timer >= 1:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames[direction])
                self.animation_timer = 0
        else:
            self.current_frame = 0  # Revenir à la frame de base quand immobile
        
        self.image = self.animation_frames[direction][self.current_frame]
        self.image.set_colorkey([0, 0, 0])

    def save_location(self): 
        self.old_position = self.position.copy()

    def move_right(self): 
        self.position[0] += self.speed
        self.moving = True
        self.animate('right')

    def move_left(self): 
        self.position[0] -= self.speed
        self.moving = True
        self.animate('left')

    def move_up(self): 
        self.position[1] -= self.speed
        self.moving = True
        self.animate('up')

    def move_down(self): 
        self.position[1] += self.speed
        self.moving = True
        self.animate('down')

    def stop_moving(self):
        """Arrête l'animation et reste sur la première frame"""
        self.moving = False
        self.animate(self.current_direction)

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        """Extrait une image de la feuille de sprites"""
        image = pygame.Surface([40, 48], pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 40, 48))
        return image