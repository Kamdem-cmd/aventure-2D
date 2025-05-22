import pygame
import pytmx
import pyscroll
import time
from player import Player

class Game:

    def __init__(self):
        # Initialisation de pygame
        pygame.init()
        
        # Paramètres de la fenêtre
        self.screen_width, self.screen_height = 800, 600
        self.fullscreen = False
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Adventure-Game prototype")
        
        # Charger l'image de fond
        self.background = pygame.image.load("background.jpeg").convert()
        
        # Police pour les menus
        self.font = pygame.font.Font(None, 36)
        
        # Initialisation des éléments du jeu
        self.init_game()

        # Ajout du compte à rebours
        self.countdown_time = 30  # Secondes
        self.start_time = 0
        self.game_over = False
        self.level_completed = False
        self.current_map = "map.tmx" # Pour suivre la carte actuelle

        # Initialisation audio
        pygame.mixer.init()
        self.volume = 0.5  # Volume par défaut (50%)
        self.background_music = None
        self.load_music()
        
        # Chargement des paramètres
        self.load_settings()

    def load_music(self):
        """Charge la musique avec le volume actuel"""
        try:
            # Essayez d'abord .ogg puis .wav
            try:
                self.background_music = pygame.mixer.Sound("sounds/background.ogg")
            except:
                self.background_music = pygame.mixer.Sound("sounds/background.wav")
            self.background_music.set_volume(self.volume)
        except Exception as e:
            print(f"Erreur chargement musique: {e}")
            self.background_music = None

    def play_background_music(self):
        """Joue la musique en boucle"""
        if self.background_music:
            self.background_music.play(loops=-1)  # -1 = boucle infinie


    def show_options_menu(self):
        """Menu options avec contrôle du volume"""
        options_active = True
        selected = 0
        options = [
            f"Musique: {'ON' if self.background_music else 'OFF'}",
            f"Volume: [{'=' * int(self.volume * 10)}{' ' * (10 - int(self.volume * 10))}]",
            "Plein écran",
            "Retour"
        ]
         
        while options_active:
            self.screen.fill((60, 30, 50))
            
            # Affichage titre
            title = self.font.render("OPTIONS", True, (255, 255, 255))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # Affichage options
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 200 + i*40))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_active = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_LEFT:
                        if selected == 0:  # Activer/désactiver musique
                            if self.background_music:
                                self.background_music.stop()
                                self.background_music = None
                            else:
                                self.load_music()
                                self.play_background_music()
                        elif selected == 1:  # Diminuer volume
                            self.update_volume(self.volume - 0.1)
                    elif event.key == pygame.K_RIGHT:
                        if selected == 0:  # Activer/désactiver musique
                            if not self.background_music:
                                self.load_music()
                                self.play_background_music()
                        elif selected == 1:  # Augmenter volume
                            self.update_volume(self.volume + 0.1)
                    elif event.key == pygame.K_RETURN:
                        if selected == 2:  # Plein écran
                            self.toggle_fullscreen()
                        elif selected == 3:  # Retour
                            options_active = False
                    elif event.key == pygame.K_ESCAPE:
                        options_active = False
                    
                    # Mise à jour de l'affichage
                    options = [
                        f"Musique: {'ON' if self.background_music else 'OFF'}",
                        f"Volume: [{'=' * int(self.volume * 10)}{' ' * (10 - int(self.volume * 10))}]",
                        "Plein écran",
                        "Retour"
                    ]

    def save_settings(self):
        """Sauvegarde les paramètres"""
        with open('settings.ini', 'w') as f:
            f.write(f"volume={self.volume}\n")

    def load_settings(self):
        """Charge les paramètres"""
        try:
            with open('settings.ini', 'r') as f:
                for line in f:
                    if line.startswith('volume='):
                        self.volume = float(line.split('=')[1])
        except:
            pass  # Fichier non trouvé, on garde les valeurs par défaut

    def init_game(self):
        """Initialise les éléments du jeu"""
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("map.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        # generer le joueur
        player_position = tmx_data.get_object_by_name("positionInit")
        self.player = Player(player_position.x, player_position.y)

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)
        self.group.add(self.player)

        # Definir le rectangle de collision pour aller au level1
        enter_l1 = tmx_data.get_object_by_name('enter_l1')
        self.enter_l1_rect = pygame.Rect(enter_l1.x, enter_l1.y, enter_l1.width, enter_l1.height)

        # Démarrer le compte à rebours lorsque le jeu commence (ou le niveau)
        self.start_time = time.time()

    def toggle_fullscreen(self):
        """Basculer entre plein écran et fenêtré"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def show_main_menu(self):
        """Affiche le menu principal"""
        menu_active = True
        selected = 0
        options = ["Jouer", "Options", "Quitter"]
        
        while menu_active:
            self.screen.fill((60, 30, 50))
            self.screen.blit(self.background, (150, 150))
            
            # Titre
            title = self.font.render("ADVENTURE GAME", True, (255, 255, 255))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # Options du menu
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 250 + i*50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:  # Jouer
                            return True
                        elif selected == 1:  # Options
                            self.show_options_menu()
                        elif selected == 2:  # Quitter
                            return False
                    elif event.key == pygame.K_ESCAPE:
                        return False

        return True

    def show_options_menu(self):
        """Affiche le menu des options"""
        options_active = True
        selected = 0
        options = ["Plein écran", "Retour"]
        
        while options_active:
            self.screen.fill((60, 30, 50))
            
            # Titre
            title = self.font.render("OPTIONS", True, (255, 255, 255))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
            
            # Options
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 250 + i*50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_active = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:  # Plein écran
                            self.toggle_fullscreen()
                        elif selected == 1:  # Retour
                            options_active = False
                    elif event.key == pygame.K_ESCAPE:
                        options_active = False

    def show_pause_menu(self):
        """Affiche le menu pause"""
        pause_active = True
        selected = 0
        options = ["Reprendre", "Options", "Quitter"]
        
        while pause_active:
            # Créer une surface semi-transparente
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            # Titre
            title = self.font.render("PAUSE", True, (255, 255, 255))
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 200))
            
            # Options du menu
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (self.screen_width//2 - text.get_width()//2, 300 + i*50))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0:  # Reprendre
                            return True
                        elif selected == 1:  # Options
                            self.show_options_menu()
                        elif selected == 2:  # Quitter
                            return False
                    elif event.key == pygame.K_ESCAPE:
                        return True

        return True


    def handle_input(self):
        pressed = pygame.key.get_pressed()
        
        # Réinitialise l'état de mouvement
        self.player.moving = False
        
        if pressed[pygame.K_UP]:
            self.player.move_up()
        elif pressed[pygame.K_DOWN]:
            self.player.move_down()
        elif pressed[pygame.K_LEFT]:
            self.player.move_left()
        elif pressed[pygame.K_RIGHT]:
            self.player.move_right()
        else:
            # Si aucune touche de mouvement n'est pressée
            self.player.stop_moving()

    def switch_level(self):
        # charger la carte (tmx)
        tmx_data = pytmx.util_pygame.load_pygame("level1.tmx")
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 1.5

        tmx_data = pytmx.util_pygame.load_pygame("level1.tmx") # Assurez-vous que c'est bien level1.tmx
        self.current_map = "level1.tmx" # Mettre à jour la carte actuelle
        self.start_time = time.time()  # Réinitialiser le timer pour le nouveau niveau
        self.level_completed = False # Réinitialiser le drapeau

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)
        self.group.add(self.player)

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

        tmx_data = pytmx.util_pygame.load_pygame("map.tmx")
        self.current_map = "map.tmx" # Mettre à jour la carte actuelle
        self.start_time = time.time() # Réinitialiser le timer
        self.game_over = False
        self.level_completed = False

        # Definir la liste de rectangle de collision
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessinner le groupe de calque
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)
        self.group.add(self.player)

        # Definir le rectangle de collision pour revenir à la map
        enter_l1 = tmx_data.get_object_by_name('enter_l1')
        self.enter_l1_rect = pygame.Rect(enter_l1.x, enter_l1.y, enter_l1.width, enter_l1.height)

        # Recuperation des points de spawn
        spawn_point = tmx_data.get_object_by_name('spawn_map')
        self.player.position[0] = spawn_point.x
        self.player.position[1] = spawn_point.y + 5

    def draw_text(self, text, color, x, y):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def update(self):
        if self.game_over or self.level_completed:
            return # Ne rien mettre à jour si le jeu est terminé ou le niveau est complet

        self.group.update()

        # Calcul du temps écoulé
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0, self.countdown_time - int(elapsed_time))

        # Vérifier le passage au niveau1
        if self.current_map == "map.tmx" and self.player.feet.colliderect(self.enter_l1_rect):
            self.switch_level()
            return # Sortir après le changement de niveau

        # Vérifier le passage à la map (depuis level1.tmx)
        # Assurez-vous que 'exit_level' est le nom de l'objet dans level1.tmx qui ramène à la carte principale
        # et que 'enter_l1_rect' est réaffecté correctement dans switch_level
        if self.current_map == "level1.tmx" and self.player.feet.colliderect(self.enter_l1_rect):
            self.level_completed = True # Le joueur a atteint l'objectif
            return # Sortir pour afficher "Niveau Terminé"


        # Vérification du temps écoulé
        if remaining_time <= 0 and self.current_map == "level1.tmx" and not self.level_completed:
            self.game_over = True

        # Verification de la collision
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

    def run(self):
        if not self.show_main_menu():
            self.save_settings() # Sauvegarder les paramètres avant de quitter
            pygame.quit()
            return

        clock = pygame.time.Clock()
        running = True
        self.play_background_music()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.show_pause_menu():
                            running = False

            if running and not self.game_over and not self.level_completed:
                self.player.save_location()
                self.handle_input()
                self.update()
                self.group.draw(self.screen)
                self.group.center(self.player.rect)

                # Afficher le compte à rebours uniquement sur level1.tmx
                if self.current_map == "level1.tmx":
                    elapsed_time = time.time() - self.start_time
                    remaining_time = max(0, self.countdown_time - int(elapsed_time))
                    self.draw_text(f"Temps: {remaining_time}", (255, 255, 255), self.screen_width - 100, 30)

                pygame.display.flip()
                clock.tick(60)
            elif self.game_over:
                self.screen.fill((0, 0, 0)) # Fond noir
                self.draw_text("GAME OVER", (255, 0, 0), self.screen_width // 2, self.screen_height // 2)
                pygame.display.flip()
                for event in pygame.event.get(): # Permettre de quitter le jeu
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
            elif self.level_completed:
                self.screen.fill((0, 0, 0)) # Fond noir
                self.draw_text("Niveau 1 Terminé !", (0, 255, 0), self.screen_width // 2, self.screen_height // 2)
                pygame.display.flip()
                for event in pygame.event.get(): # Permettre de quitter le jeu
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
            else: # Si le jeu n'est pas en cours (par exemple, après avoir quitté un menu)
                running = False


        self.save_settings() # Sauvegarder les paramètres avant de quitter
        if self.background_music:
            self.background_music.stop()

        pygame.quit()


        