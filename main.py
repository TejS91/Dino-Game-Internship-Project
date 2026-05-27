"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, modified for scaling difficulty. 🤖
"""

import random
import pygame

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False

# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 300  # The Y-coordinate of the ground level
JUMP_GRAVITY_START_SPEED = -20  # The speed at which the player jumps
players_gravity_speed = 0  # The current speed at which the player falls

# --- DIFFICULTY & SPAWNING CONFIGURATION ---
BASE_SPEED = 5
game_speed = BASE_SPEED

# Custom event for obstacle spawning
OBSTACLE_TIMER = pygame.USEREVENT + 1
# Set the initial spawn timer (e.g., check for a spawn every 1200ms)
pygame.time.set_timer(OBSTACLE_TIMER, 1200)
# --------------------------------------------

# Load level assets
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert()
game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))

# Load sprite assets
player_surf = pygame.image.load("graphics/player/player_walk_1.png").convert_alpha()
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
egg_surf = pygame.image.load("graphics/egg/egg_1.png").convert_alpha()

# List to hold multiple active obstacles
obstacle_rect_list = []

start_time = 0
score = 0


# Helper function to handle obstacle movement and collisions
def handle_obstacles(obstacle_list, speed, player_rect):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            # Move obstacle based on current game speed
            obstacle_rect.x -= speed
            screen.blit(egg_surf, obstacle_rect)

            # Check for collision
            if player_rect.colliderect(obstacle_rect):
                return False

        # Keep only obstacles that are still on the screen
        obstacle_list[:] = [obs for obs in obstacle_list if obs.right > 0]

    return True


while running:
    # Poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif is_playing:
            # When player wants to jump
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= GROUND_Y:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED

            # Randomly decide to spawn an egg when the timer fires
            if event.type == OBSTACLE_TIMER:
                # 70% chance to spawn an egg, creating sporadic gaps
                if random.randint(0, 10) < 7:
                    # Spawn slightly off-screen with a bit of random offset variance
                    spawn_x = random.randint(900, 1100)
                    new_egg = egg_surf.get_rect(bottomleft=(spawn_x, GROUND_Y))

                    # Prevent spawning eggs directly on top of each other
                    if not obstacle_rect_list or (
                        new_egg.left - obstacle_rect_list[-1].right > 200
                    ):
                        obstacle_rect_list.append(new_egg)

        else:
            # When player wants to play again by pressing SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_playing = True
                obstacle_rect_list.clear()  # Clear old obstacles
                game_speed = BASE_SPEED  # Reset speed
                player_rect.bottom = GROUND_Y  # Reset player position
                players_gravity_speed = 0
                start_time = pygame.time.get_ticks()  # Reset score clock

    if is_playing:
        screen.fill("purple")

        # Calculate live score based on elapsed milliseconds
        current_time = pygame.time.get_ticks() - start_time
        score = int(current_time / 100)

        # --- SCALE DIFFICULTY ---
        # Increase speed by 1 unit for every 100 points scored, capped at speed 15
        game_speed = BASE_SPEED + min(score // 100, 10)

        # Generate the dynamic text surface and its matching rectangle
        score_surf = game_font.render(f"Score: {score}", False, "Black")
        score_rect = score_surf.get_rect(center=(400, 50))

        # Blit the level assets
        screen.blit(SKY_SURF, (0, 0))
        screen.blit(GROUND_SURF, (0, GROUND_Y))

        # Expand the background box slightly so the changing numbers don't clip
        pygame.draw.rect(screen, "#c0e8ec", score_rect.inflate(20, 10))
        pygame.draw.rect(screen, "#c0e8ec", score_rect.inflate(20, 10), 10)
        screen.blit(score_surf, score_rect)

        # Update and draw obstacles, check for collisions
        is_playing = handle_obstacles(obstacle_rect_list, game_speed, player_rect)

        # Adjust player's vertical location then blit it
        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
        screen.blit(player_surf, player_rect)

    # When game is over, display game over message and final score
    else:
        screen.fill("black")
        game_over_surf = game_font.render(f"Game Over! Score: {score}", False, "White")
        game_over_rect = game_over_surf.get_rect(center=(400, 200))
        retry_surf = game_font.render("Press SPACE to play again", False, "Gray")
        retry_rect = retry_surf.get_rect(center=(400, 280))
        screen.blit(game_over_surf, game_over_rect)
        screen.blit(retry_surf, retry_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()