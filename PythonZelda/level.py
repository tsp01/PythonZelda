import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import Ui
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

class Level:
    """
    Class controls the map, and spawn locations
    Class also serves as secondary game loop calling almost all other classes
    """
    def __init__(self):

        #get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        #sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #attack sprite
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        #sprite setup
        self.create_map()

        #user interface
        self.ui = Ui()
        self.upgrade = Upgrade(self.player)

        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

        #player death
        self.player_dead = False

    #loads the sprites onto the map
    def create_map(self):

        # loads all map files for spawn locations and ground
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('map/map_Grass.csv'),
            'object': import_csv_layout('map/map_Objects.csv'),
            'entities': import_csv_layout('map/map_Entities.csv')
        }

        # loads images for grass and stationary objects
        graphics = {
            'grass': import_folder('graphics/grass'),
            'objects': import_folder('graphics/objects'),
        }
        
        # loops go through each square in each map table
        # and spawn in the apropriate tile or entity
        for style,layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        # creates boundary around areas the player can not cross
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')

                        # spawns cuttable grass
                        if style == 'grass':
                            grass_type = choice(graphics['grass'])
                            Tile(
                                (x,y),
                                [self.visible_sprites,self.obstacle_sprites, self.attackable_sprites],
                                'grass',
                                grass_type)

                        # spawns non interactable objects 
                        if style == 'object':
                            object_surf = graphics['objects'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object', object_surf)
                        
                        # spawns the player and enemies
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    (x,y),
                                    [self.visible_sprites], 
                                    self.obstacle_sprites, 
                                    self.create_attack, 
                                    self.destroy_attack, 
                                    self.create_magic)

                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name = 'raccoon'
                                if col == '393': monster_name = 'squid'
                                Enemy(
                                    monster_name, 
                                    (x,y), 
                                    [self.visible_sprites, self.attackable_sprites], 
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp)
        
    def create_attack(self):
        """
        Creates an attack from the players current weapon
        """
        
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        """
        Creates magic spells
        """
        
        if style == 'heal':
            self.magic_player.heal(strength, cost, self.player, [self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(strength, cost, self.player, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        """
        Destroys an attack after it finshes
        """

        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        """
        makes sure enemies are damaged and grass is cut by attacks
        """

        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0,75)
                            for leaf in range(randint(3,6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        elif target_sprite.sprite_type == 'enemy':
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        """
        Decreases the players health and checks if player has died
        """

        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

        if self.player.health < 0:
            self.player_dead = True

    def trigger_death_particles(self, pos, particle_type):
        """
        causes short animations upond death of enemies or player
        """

        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

    def add_exp(self, amount):
        """
        Increases the players EXP
        """

        self.player.exp += amount

    def toggle_menu(self):
        """
        Allows player to pause via an upgrade menu
        """

        self.game_paused = not self.game_paused

    def run(self):
        """
        updates level and calls other functions in proper order
        """

        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused and not self.player_dead:
            self.upgrade.display()
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
        
            #debug(self.player.status)

# to help control the camera
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        #general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #creating the floor
        self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

    def custom_draw(self, player):
        """
        moves the camera via offsets and draws the floor
        """

        #getting offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        #draw the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        #for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        """
        updates enemies
        """

        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']

        for enemy in enemy_sprites:
            enemy.enemy_update(player)