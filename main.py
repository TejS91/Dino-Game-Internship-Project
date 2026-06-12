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
GROUND_Y = 350  # Positions feet perfectly onto the brick floor top edge


# --- TUNED JUMP PHYSICS ---
JUMP_GRAVITY_START_SPEED = -18.5  # jump height
gravity_acceleration = 0.85       # gravity speed
players_gravity_speed = 0         # The current speed at which the player falls


# --- DIFFICULTY & SPAWNING CONFIGURATION ---
BASE_SPEED = 5
game_speed = BASE_SPEED


# Custom event for obstacle spawning
OBSTACLE_TIMER = pygame.USEREVENT + 1
# Set the initial spawn timer (e.g., check for a spawn every 1200ms)
pygame.time.set_timer(OBSTACLE_TIMER, 1200)
# --------------------------------------------


# Load the image with alpha support
UNDERWATER_BG = pygame.image.load("graphics/level/underwaterbg.png").convert_alpha()

# Scale background to accurately fit the top 350px
bg_height = 350
bg_width = 800
UNDERWATER_BG = pygame.transform.scale(UNDERWATER_BG, (bg_width, bg_height))


# --- PROCEDURAL UNDERWATER BRICK RUNWAY ---
floor_height = 400 - bg_height
BRICK_FLOOR = pygame.Surface((800, floor_height))
BRICK_FLOOR.fill("#1d3354")  # Deep blue-grey brick base

for y in range(0, floor_height, 25):
    # Horizontal grout lines
    pygame.draw.line(BRICK_FLOOR, "#0f1b2d", (0, y), (800, y), 2)
    # Staggered vertical grout lines
    shift = 20 if (y // 25) % 2 == 0 else 0
    for x in range(shift, 800, 40):
        pygame.draw.line(BRICK_FLOOR, "#0f1b2d", (x, y), (x, y + 25), 2)
        # Subtle pixel art highlight on each brick
        pygame.draw.line(BRICK_FLOOR, "#28446e", (x + 2, y + 2), (x + 38, y + 2), 1)


# --- NEW: SCROLLING POSITION VARIABLES ---
# Track horizontal positions for background and floor independently
bg_x = 0
floor_x = 0


game_font = pygame.font.Font(pygame.font.get_default_font(), 50)
score_surf = game_font.render("SCORE?", False, "Black")
score_rect = score_surf.get_rect(center=(400, 50))


# Load sprite assets (ANIMATION FRAMES)
player_walk_1 = pygame.image.load("graphics/player/scuba_swim_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/scuba_swim_2.png").convert_alpha()
player_jump = pygame.image.load("graphics/player/player_jump.png").convert_alpha()


player_frames = [player_walk_1, player_walk_2]
player_index = 0


player_surf = player_frames[player_index]
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
           if (
               (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
               or event.type == pygame.MOUSEBUTTONDOWN
           ) and player_rect.bottom >= GROUND_Y:
               players_gravity_speed = JUMP_GRAVITY_START_SPEED

           if event.type == OBSTACLE_TIMER:
               if random.randint(0, 10) < 7:
                   spawn_x = random.randint(900, 1100)
                   new_egg = egg_surf.get_rect(bottomleft=(spawn_x, GROUND_Y))

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
               player_index = 0
               bg_x = 0         # Reset background scroll position
               floor_x = 0      # Reset floor scroll position
               start_time = pygame.time.get_ticks()  # Reset score clock

   if is_playing:
       screen.fill("#1d3354")

       # Calculate live score based on elapsed milliseconds
       current_time = pygame.time.get_ticks() - start_time
       score = int(current_time / 100)

       # --- SCALE DIFFICULTY ---
       game_speed = BASE_SPEED + min(score // 100, 10)

       # Generate the dynamic text surface and its matching rectangle
       score_surf = game_font.render(f"Score: {score}", False, "Black")
       score_rect = score_surf.get_rect(center=(400, 50))


       # --- NEW: UPDATE AND DRAW MOVING BACKGROUND (PARALLAX EFFECT) ---
       # Moving the background at 20% of game speed makes the distant ruins feel far away!
       bg_x -= game_speed * 0.2
       if bg_x <= -bg_width:
           bg_x = 0

       # Stitch two background images side-by-side so there are no seams when moving
       screen.blit(UNDERWATER_BG, (bg_x, 0))
       screen.blit(UNDERWATER_BG, (bg_x + bg_width, 0))


       # --- NEW: UPDATE AND DRAW MOVING BRICK FLOOR ---
       # Moving the floor at 100% speed matches the movement of the incoming obstacles
       floor_x -= game_speed
       if floor_x <= -800:
           floor_x = 0

       # Stitch two floor surfaces side-by-side to make the line seamless
       screen.blit(BRICK_FLOOR, (floor_x, bg_height))
       screen.blit(BRICK_FLOOR, (floor_x + 800, bg_height))


       # Expand the background box slightly so the changing numbers don't clip
       pygame.draw.rect(screen, "#c0e8ec", score_rect.inflate(20, 10))
       pygame.draw.rect(screen, "#c0e8ec", score_rect.inflate(20, 10), 10)
       screen.blit(score_surf, score_rect)

       # Update and draw obstacles, check for collisions
       is_playing = handle_obstacles(obstacle_rect_list, game_speed, player_rect)

       # Apply the gravity step
       players_gravity_speed += gravity_acceleration
       player_rect.y += players_gravity_speed
      
       # Reset gravity velocity to 0 when landing so it doesn't build up infinite speed downward
       if player_rect.bottom >= GROUND_Y:
           player_rect.bottom = GROUND_Y
           players_gravity_speed = 0
          
           # --- ANIMATION LOGIC ---
           player_index += 0.1
           if player_index >= len(player_frames):
               player_index = 0
           player_surf = player_frames[int(player_index)]
       else:
           # Show the jump sprite if the player is mid-air
           player_surf = player_jump

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