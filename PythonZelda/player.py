import pygame
from entity import Entity
from settings import *
from support import *
from debug import debug

class Player(Entity):

    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)

        self.image = pygame.image.load('graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6,HITBOX_OFFSET['player'])

        #import player graphics
        self.import_player_assets()
        self.status = 'down'

        self.speed = 5
        self.attacking = False
        self.switch_duration_cooldown = 400
        self.attack_timer = None

        self.obstacle_sprites = obstacle_sprites

        #weapons
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None

        #magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magix_switch_time = None

        #stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed':100}
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 0
        self.speed = self.stats['speed']

        #damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerable_duration = 500

        #import sounds
        self.weapon_attack_sound = pygame.mixer.Sound('audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)

    def import_player_assets(self):
        character_path = 'graphics/player/'
        self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
        'right_idle':[], 'left_idle':[], 'up_idle':[], 'down_idle':[],
        'right_attack':[], 'left_attack':[], 'up_attack':[], 'down_attack':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            image_list = import_folder(full_path)
            self.animations[animation] = image_list

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.attacking:
            #move input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            #attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack() 
                self.weapon_attack_sound.play()   

            #magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                #Is this supposed to be more complicated? 
                style = self.magic
                strength = magic_data[style]['strength'] + self.stats['magic']
                cost = magic_data[style]['cost']

                self.create_magic(style, strength, cost)

            if self.can_switch_weapon:
                if keys[pygame.K_q]:
                    self.can_switch_weapon = False
                    self.weapon_switch_time = pygame.time.get_ticks()
                    self.weapon_index += 1
                
                if self.weapon_index > (len(list(weapon_data.keys())) - 1):
                    self.weapon_index = 0

                self.weapon = list(weapon_data.keys())[self.weapon_index]

            if self.can_switch_magic:
                if keys[pygame.K_e]:
                    self.can_switch_magic = False
                    self.magic_switch_time = pygame.time.get_ticks()
                    self.magic_index += 1
                
                if self.magic_index > (len(list(magic_data.keys())) - 1):
                    self.magic_index = 0

                self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):

        #idle
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status += '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status += '_attack'
        else:
            self.status = self.status.replace('_attack', '')

    def cooldown(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.switch_duration_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerable_duration:
                self.vulnerable = True

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        #flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):

        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        full_damage = base_damage + weapon_damage

        return full_damage

    def get_full_magic_damage(self):

        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        full_damage = base_damage + spell_damage

        return full_damage

    def get_value_by_index(self, index):
        
        return list(self.stats.values())[index]

    def get_cost_by_index(self, index):
        
        return list(self.upgrade_cost.values())[index]

    def energy_recovery(self):

        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def update(self):
        self.input()
        self.cooldown()
        self.animate()
        self.get_status()
        self.move(self.stats['speed'])
        self.energy_recovery()
        