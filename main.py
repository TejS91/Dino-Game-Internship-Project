"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, modified for scaling difficulty. 🤖
"""

import random
import pygame
import os

# Initialize Pygame and create a window
pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
running = True  # Pygame main loop, kills pygame when False


# Game state variables
is_playing = True  # Whether in game or in menu
GROUND_Y = 350  # Positions feet perfectly onto the brick floor top edge


# --- TUNED JUMP PHYSICS ---
JUMP_GRAVITY_START_SPEED = -19.5  # Increased jump height as requested
gravity_acceleration = 0.85       # gravity speed
players_gravity_speed = 0         # The current speed at which the player falls


# --- DIFFICULTY & SPAWNING CONFIGURATION ---
BASE_SPEED = 5
game_speed = BASE_SPEED

# Track the current timer delay so we only update it when it actually changes
current_spawn_delay = 1200 

# Custom event for obstacle spawning
OBSTACLE_TIMER = pygame.USEREVENT + 1
pygame.time.set_timer(OBSTACLE_TIMER, current_spawn_delay)
# --------------------------------------------


# --- HIGH SCORE SYSTEM ---
HIGHSCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as file:
                return int(file.read().strip())
        except ValueError:
            return 0
    return 0

def save_high_score(new_high_score):
    with open(HIGHSCORE_FILE, "w") as file:
        file.write(str(new_high_score))

high_score = load_high_score()
# -------------------------


# Load the image 
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
bg_x = 0
floor_x = 0


# --- FONTS SETUP ---
game_font = pygame.font.Font(pygame.font.get_default_font(), 40)
pb_font = pygame.font.Font(pygame.font.get_default_font(), 25) # Smaller font for PB


# Load sprite assets (ANIMATION FRAMES)
player_walk_1 = pygame.image.load("graphics/player/scuba_swim_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/scuba_swim_2.png").convert_alpha()
player_jump = pygame.image.load("graphics/player/scuba_jump_1.png").convert_alpha()


# Overrides uneven file crops and sizes to align their footprints
player_walk_1 = pygame.transform.scale(player_walk_1, (130, 95))
player_walk_2 = pygame.transform.scale(player_walk_2, (130, 80))
player_jump = pygame.transform.scale(player_jump, (110, 110))


player_frames = [player_walk_1, player_walk_2]
player_index = 0


player_surf = player_frames[player_index]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))


# --- ADJUSTED OBSTACLE SIZES ---
coral_surf = pygame.image.load("graphics/egg/CoralCluster.png").convert_alpha()
coral_surf = pygame.transform.scale(coral_surf, (100, 100))

mine_surf = pygame.image.load("graphics/egg/UnderwaterMine.png").convert_alpha()
mine_surf = pygame.transform.scale(mine_surf, (75, 75))


# List to hold multiple active obstacles. Stores dictionaries containing both the rect and type.
obstacle_list = []


start_time = 0
score = 0


# Helper function to handle obstacle movement and collisions
def handle_obstacles(obstacles, speed, player_rect):
   if obstacles:
       for obstacle in obstacles:
           # Move obstacle based on current game speed
           obstacle["rect"].x -= speed
           
           # Blit the appropriate surface based on the obstacle type
           if obstacle["type"] == "coral":
               screen.blit(coral_surf, obstacle["rect"])
           else:
               screen.blit(mine_surf, obstacle["rect"])

           # --- BETTER COLLISION CHECKING ---
           player_hitbox = player_rect.inflate(-20, -15)
           
           if obstacle["type"] == "coral":
               obstacle_hitbox = obstacle["rect"].inflate(-30, -20)
           else:
               obstacle_hitbox = obstacle["rect"].inflate(-25, -25)

           if player_hitbox.colliderect(obstacle_hitbox):
               return False

       # Keep only obstacles that are still on the screen
       obstacles[:] = [obs for obs in obstacles if obs["rect"].right > 0]

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
                   
                   # Choose a random asset and create its rect
                   obstacle_type = random.choice(["coral", "mine"])
                   chosen_surf = coral_surf if obstacle_type == "coral" else mine_surf
                   
                   # --- POSITION ADJUSTMENT ---
                   if obstacle_type == "coral":
                       new_rect = chosen_surf.get_rect(bottomleft=(spawn_x, GROUND_Y + 30))
                   else:
                       new_rect = chosen_surf.get_rect(bottomleft=(spawn_x, GROUND_Y))

                   # --- DYNAMIC MINIMUM GAP DISTANCE ---
                   min_gap = max(220 - (score // 5), 140)

                   # Check if space permits spawning a new obstacle
                   if not obstacle_list or (
                       new_rect.left - obstacle_list[-1]["rect"].right > min_gap
                   ):
                       obstacle_list.append({"rect": new_rect, "type": obstacle_type})

       else:
           # When player wants to play again by pressing SPACE
           if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
               is_playing = True
               obstacle_list.clear()  # Clear old obstacles
               game_speed = BASE_SPEED  # Reset speed
               player_rect.bottom = GROUND_Y  # Reset player position
               players_gravity_speed = 0
               player_index = 0
               bg_x = 0         # Reset background scroll position
               floor_x = 0      # Reset floor scroll position
               current_spawn_delay = 1200
               pygame.time.set_timer(OBSTACLE_TIMER, current_spawn_delay) # Reset timer rate
               start_time = pygame.time.get_ticks()  # Reset score clock

   if is_playing:
       screen.fill("#1d3354")

       # Calculate live score based on elapsed milliseconds
       current_time = pygame.time.get_ticks() - start_time
       score = int(current_time / 100)

       # Update live high score check
       if score > high_score:
           high_score = score

       # --- SCALE SPEED DIFFICULTY ---
       game_speed = BASE_SPEED + min(score // 100, 10)

       # --- SCALE SPAWN DIFFICULTY ---
       target_delay = max(1200 - ((score // 100) * 75), 600)
       if target_delay != current_spawn_delay:
           current_spawn_delay = target_delay
           pygame.time.set_timer(OBSTACLE_TIMER, current_spawn_delay)


       # --- UPDATE AND DRAW MOVING BACKGROUND (PARALLAX EFFECT) ---
       bg_x -= game_speed * 0.2
       if bg_x <= -bg_width:
           bg_x = 0

       screen.blit(UNDERWATER_BG, (bg_x, 0))
       screen.blit(UNDERWATER_BG, (bg_x + bg_width, 0))


       # --- UPDATE AND DRAW MOVING BRICK FLOOR ---
       floor_x -= game_speed
       if floor_x <= -800:
           floor_x = 0

       screen.blit(BRICK_FLOOR, (floor_x, bg_height))
       screen.blit(BRICK_FLOOR, (floor_x + 800, bg_height))


       # --- DYNAMIC SCOREBOARD WITH PB ---
       score_surf = game_font.render(f"Score: {score}", False, "Black")
       pb_surf = pb_font.render(f"  PB: {high_score}", False, "#4a4a4a") # Slightly muted grey color

       # Create a unified box containing both surfaces next to each other
       total_width = score_surf.get_width() + pb_surf.get_width()
       max_height = max(score_surf.get_height(), pb_surf.get_height())
       
       scoreboard_rect = pygame.Rect(0, 0, total_width, max_height)
       scoreboard_rect.center = (400, 50) # Keep it centered at the top

       # Draw background banner
       pygame.draw.rect(screen, "#c0e8ec", scoreboard_rect.inflate(30, 15))
       pygame.draw.rect(screen, "#c0e8ec", scoreboard_rect.inflate(30, 15), 10)

       # Blit the surfaces side-by-side inside the box
       screen.blit(score_surf, (scoreboard_rect.left, scoreboard_rect.top))
       screen.blit(pb_surf, (scoreboard_rect.left + score_surf.get_width(), scoreboard_rect.top + (score_surf.get_height() - pb_surf.get_height()) // 2))


       # Update and draw obstacles, check for collisions
       is_playing = handle_obstacles(obstacle_list, game_speed, player_rect)
       
       # If a crash just occurred, immediately commit high score to permanent file
       if not is_playing:
           save_high_score(high_score)

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
           
           # Recalculate rect dimensions to prevent frame-shaking on the ground
           player_rect = player_surf.get_rect(bottomleft=player_rect.bottomleft)
       else:
           # Show the jump sprite if the player is mid-air
           player_surf = player_jump
           
           # Recalculate rect dimensions for the airborne frame
           player_rect = player_surf.get_rect(bottomleft=player_rect.bottomleft)

       screen.blit(player_surf, player_rect)

   # When game is over, display game over message and final score
   else:
       screen.fill("black")
       game_over_surf = game_font.render(f"Game Over! Score: {score}", False, "White")
       game_over_rect = game_over_surf.get_rect(center=(400, 180))
       
       pb_display_surf = pb_font.render(f"Your Personal Best: {high_score}", False, "Gold")
       pb_display_rect = pb_display_surf.get_rect(center=(400, 240))
       
       retry_surf = game_font.render("Press SPACE to play again", False, "Gray")
       retry_rect = retry_surf.get_rect(center=(400, 310))
       
       screen.blit(game_over_surf, game_over_rect)
       screen.blit(pb_display_surf, pb_display_rect)
       screen.blit(retry_surf, retry_rect)

   pygame.display.flip()
   clock.tick(60)

pygame.quit()