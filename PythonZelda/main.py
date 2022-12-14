"""
This File is the first file to be executed and begins all game process's
File contains Game class to run game loop
"""
import pygame
import sys
from settings import *
from level import Level

class Game:
    """
    Game class initializes the game screen, 
    and runs the main game loop
    """
    def __init__(self):

        # initializing Game window
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Zelda')
        self.clock = pygame.time.Clock()

        self.level = Level()

        # initializes and plays background music infinitely
        main_sound = pygame.mixer.Sound('audio/main.ogg')
        main_sound.set_volume(0.5)
        main_sound.play(-1)

        #death screen setup
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        self.text_surf = self.font.render("Haha loser", False, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center = (WIDTH / 2, HEIGHT / 2))
        self.restart_message = self.font.render("Press Enter to restart", False, TEXT_COLOR)
        self.restart_rect = self.restart_message.get_rect(center = (WIDTH / 2, HEIGHT - 100))
        self.would_like_to_restart = False
        
    def run(self):
        """
        This function runs the main game loop
        """
        
        #The game loop that continues so long as the user does not die
        #or click on the exit button
        while not self.level.player_dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()
                  
            self.screen.fill(WATER_COLOR)
            self.level.run()
            pygame.display.update()
            self.clock.tick(FPS)
        
        # loop runs after player dies and has not reset or exited
        while not self.would_like_to_restart:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER:
                        self.would_like_to_restart = True
            
            self.screen.fill('Blue')
            self.screen.blit(self.text_surf, self.text_rect)
            self.screen.blit(self.restart_message, self.restart_rect)
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':

    #loop allows the user to reset the game without exiting and restarting
    while True:
        game = Game()
        game.run()


