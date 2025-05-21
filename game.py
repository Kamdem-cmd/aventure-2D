import pygame
import pytmx
import pyscroll
from player import Player

class Game:

    def __init__(self):
        # creation de la fenetre de jeu
        self.screen = pygame.display.set_mode((800, 600))     # (largeur, hauteur)
        pygame.display.set_caption("Adventure-Game prototype") # "titre à l'entête de la fenetre"

        self.background = pygame.image.load("background.jpeg").convert()
        
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("map.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        # generer le joueur
        player_position = tmx_data.get_object_by_name ("positionInit")
        self.player = Player(player_position.x, player_position.y)

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer= map_layer, default_layer = 4)
        self.group.add(self.player)                                                     # Ajout du player au groupe d'affichage (sur la map)

        # Definir le rectangle de collision pour aller au level1
        enter_l1 = tmx_data.get_object_by_name('enter_l1')
        self.enter_l1_rect = pygame.Rect(enter_l1.x, enter_l1.y, enter_l1.width, enter_l1.height)


    def handle_input(self):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_UP]:
            self.player.move_up()
            self.player.change_animation('up')
        elif pressed[pygame.K_DOWN]:
            self.player.move_down()
            self.player.change_animation('down')
        elif pressed[pygame.K_LEFT]:
            self.player.move_left()
            self.player.change_animation('left')
        elif pressed[pygame.K_RIGHT]:
            self.player.move_right()
            self.player.change_animation('right')

        if pressed[pygame.K_SPACE]:
            menu = False

    def switch_level(self):
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("level1.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer= map_layer, default_layer = 4)
        self.group.add(self.player)                                                     # Ajout du player au groupe d'affichage (sur la map)

        # Definir le rectangle de collision pour revenir à la map
        enter_l1 = tmx_data.get_object_by_name('exit_level')
        self.enter_l1_rect = pygame.Rect(enter_l1.x, enter_l1.y, enter_l1.width, enter_l1.height)

        # Recuperation des points de spawn
        spawn_point = tmx_data.get_object_by_name('spawn_player')
        self.player.position[0] = spawn_point.x
        self.player.position[1] = spawn_point.y + 5

    def switch_map(self):
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("map.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer= map_layer, default_layer = 4)
        self.group.add(self.player)                                                     # Ajout du player au groupe d'affichage (sur la map)

        # Definir le rectangle de collision pour revenir à la map
        enter_l1 = tmx_data.get_object_by_name('enter_l1')
        self.enter_l1_rect = pygame.Rect(enter_l1.x, enter_l1.y, enter_l1.width, enter_l1.height)

        # Recuperation des points de spawn
        spawn_point = tmx_data.get_object_by_name('spawn_map')
        self.player.position[0] = spawn_point.x
        self.player.position[1] = spawn_point.y + 5



    def update(self):
        self.group.update()

        # Verifier le passage au niveau1
        if self.player.feet.colliderect(self.enter_l1_rect):
            self.switch_level()
            
        
        # Verifier le passage à la map
        if self.player.feet.colliderect(self.enter_l1_rect):
            self.switch_map()
           

        # Verification de la collision
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()


    def accueil(self, running, menu):
        running = False
        while (menu != False):
                pressed = pygame.key.get_pressed()

                if pressed[pygame.K_SPACE]:
                    
                    menu = False
                    return True

                if pressed[pygame.K_ESCAPE]:
                    menu = False
                    return False

                self.screen.fill((60, 30, 50))
                self.screen.blit(self.background, (150,150))
                pygame.display.flip()
                for event in pygame.event.get():
                    if(menu ==False or event.type == pygame.QUIT):
                        running = True
                        return running
        

    def run(self):

        clock = pygame.time.Clock()

        # creation de la boucle de jeu
        running = True
        menu = True

        while (running):

            self.player.save_location()             # Sauvegarde la position actuelle du joueur pour gerer les collisions
            self.handle_input()                     # Recuperation de l'input de joueur
            self.update()                           # actualisation du groupe
            self.group.draw(self.screen)            # affichage du groupe
            self.group.center(self.player.rect)     # centrer la camera sur le joueur
            pygame.display.flip()                   # raffraichissement de la carte

            # condition de sortis du jeu
            for event in pygame.event.get():
                if(event.type == pygame.QUIT):
                    running = False            
            
            clock.tick(60)

        pygame.quit()     # sortis de la boucle de jeu