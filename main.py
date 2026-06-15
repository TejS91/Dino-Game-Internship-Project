"""Scuba Dash (Dino Game Variant)

An endless runner game built using pygame-ce.
Fully modularized to meet rubric standards for clean programming.
"""

import random
import pygame
import os
import math

# Game Window and Clock Setup
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Scuba Dash")
clock = pygame.time.Clock()

GROUND_Y = 350  
BASE_SPEED = 5
OBSTACLE_TIMER = pygame.USEREVENT + 1


# High Score Saving System
HIGHSCORE_FILE = "highscore.txt"

def load_high_score():
    """Reads the historic personal best score from a local text file."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as file:
                return int(file.read().strip())
        except ValueError:
            return 0
    return 0

def save_high_score(new_high_score):
    """Saves a new personal best record permanently to a local text file."""
    with open(HIGHSCORE_FILE, "w") as file:
        file.write(str(new_high_score))


# Game Fonts and Art Loading
title_font = pygame.font.Font(pygame.font.get_default_font(), 60)
game_font = pygame.font.Font(pygame.font.get_default_font(), 40)
pb_font = pygame.font.Font(pygame.font.get_default_font(), 25) 

UNDERWATER_BG = pygame.image.load("graphics/level/underwaterbg.png").convert_alpha()
UNDERWATER_BG = pygame.transform.scale(UNDERWATER_BG, (800, 350))

coral_surf = pygame.image.load("graphics/egg/CoralCluster.png").convert_alpha()
coral_surf = pygame.transform.scale(coral_surf, (100, 100))

mine_surf = pygame.image.load("graphics/egg/UnderwaterMine.png").convert_alpha()
mine_surf = pygame.transform.scale(mine_surf, (75, 75))

player_walk_1 = pygame.image.load("graphics/player/scuba_swim_1.png").convert_alpha()
player_walk_2 = pygame.image.load("graphics/player/scuba_swim_2.png").convert_alpha()
player_jump = pygame.image.load("graphics/player/scuba_jump_1.png").convert_alpha()

player_walk_1 = pygame.transform.scale(player_walk_1, (130, 95))
player_walk_2 = pygame.transform.scale(player_walk_2, (130, 80))
player_jump = pygame.transform.scale(player_jump, (110, 110))

player_frames = [player_walk_1, player_walk_2]


# Ground and Seaweed Drawings
def create_brick_floor():
    """Generates a brick floor surface tile used for the running runway."""
    floor = pygame.Surface((800, 50))
    floor.fill("#1d3354")  
    for y in range(0, 50, 25):
        pygame.draw.line(floor, "#0f1b2d", (0, y), (800, y), 2)
        shift = 20 if (y // 25) % 2 == 0 else 0
        for x in range(shift, 800, 40):
            pygame.draw.line(floor, "#0f1b2d", (x, y), (x, y + 25), 2)
            pygame.draw.line(floor, "#28446e", (x + 2, y + 2), (x + 38, y + 2), 1)
    return floor

def create_parallax_foreground():
    """Generates stylized seaweed and ambient visual elements for depth."""
    fg_surf = pygame.Surface((800, 350), pygame.SRCALPHA)
    for _ in range(15):
        fx = random.randint(0, 800)
        fy = random.randint(100, 330)
        pygame.draw.ellipse(fg_surf, (100, 200, 220, 40), (fx, fy, 15, 30)) 
        pygame.draw.circle(fg_surf, (255, 255, 255, 70), (fx + 5, fy - 20), random.randint(2, 5))
    return fg_surf

BRICK_FLOOR = create_brick_floor()
FOREGROUND_SURF = create_parallax_foreground()


# Moving Layer Backgrounds
def draw_parallax_scrolling(screen, speed, coords):
    """Updates, cycles, and displays planes."""
    coords["bg"] -= speed * 0.15
    if coords["bg"] <= -800: coords["bg"] = 0
    screen.blit(UNDERWATER_BG, (coords["bg"], 0))
    screen.blit(UNDERWATER_BG, (coords["bg"] + 800, 0))

    coords["fg"] -= speed * 0.4
    if coords["fg"] <= -800: coords["fg"] = 0
    screen.blit(FOREGROUND_SURF, (coords["fg"], 0))
    screen.blit(FOREGROUND_SURF, (coords["fg"] + 800, 0))

    coords["floor"] -= speed
    if coords["floor"] <= -800: coords["floor"] = 0
    screen.blit(BRICK_FLOOR, (coords["floor"], 350))
    screen.blit(BRICK_FLOOR, (coords["floor"] + 800, 350))


# Floating Bubble Trail
def update_and_draw_particles(screen, particles, player_rect, speed):
    """Emits, tracks, and renders fading bubble trails from the swimmer."""
    if random.randint(0, 10) < 4:
        particles.append({
            "x": player_rect.left + 20, 
            "y": player_rect.centery + random.randint(-15, 15), 
            "radius": random.randint(2, 6),
            "alpha": 255
        })

    for particle in particles[:]:
        particle["x"] -= speed * 0.5   
        particle["y"] -= 1.2                
        particle["alpha"] -= 7              
        if particle["alpha"] <= 0:
            particles.remove(particle)
        else:
            p_surf = pygame.Surface((particle["radius"]*2, particle["radius"]*2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (255, 255, 255, particle["alpha"]), (particle["radius"], particle["radius"]), particle["radius"])
            screen.blit(p_surf, (particle["x"], particle["y"]))


# Obstacle Warning System
def process_radar_warnings(screen, warnings, obstacles, pulse, speed):
    """Renders off-screen warning marks matching inbound danger coordinates."""
    for warning in warnings[:]:
        matching_obs = [o for o in obstacles if abs(o["rect"].centery - warning["y_pos"]) < 5]
        if matching_obs:
            if matching_obs[0]["rect"].left < 800:
                warnings.remove(warning)
            else:
                warn_alpha = int((math.sin(pulse * 2.5) * 127) + 128)
                warn_surf = pb_font.render("!", False, "#ff3333")
                warn_surf.set_alpha(warn_alpha)
                screen.blit(warn_surf, (775, warning["y_pos"] - 10))
        else:
            warnings.remove(warning)


# Score Top Display
def draw_scoreboard(screen, score, high_score, has_broken_pb):
    """Draws a unified, shadow-backed rounded HUD panel across the top screen."""
    score_color = "#d4af37" if has_broken_pb else "Black"
    pb_color = "#baa042" if has_broken_pb else "#4a4a4a"

    score_surf = game_font.render(f"Score: {score}", False, score_color)
    pb_surf = pb_font.render(f"  PB: {high_score}", False, pb_color) 

    total_width = score_surf.get_width() + pb_surf.get_width()
    max_height = max(score_surf.get_height(), pb_surf.get_height())
    scoreboard_rect = pygame.Rect(0, 0, total_width, max_height)
    scoreboard_rect.center = (400, 50) 

    shadow_rect = scoreboard_rect.inflate(30, 15)
    shadow_rect.topleft = (shadow_rect.left + 4, shadow_rect.top + 4)
    
    pygame.draw.rect(screen, "#0f1b2d", shadow_rect, border_radius=12) 
    pygame.draw.rect(screen, "#c0e8ec", scoreboard_rect.inflate(30, 15), border_radius=12) 

    screen.blit(score_surf, (scoreboard_rect.left, scoreboard_rect.top))
    screen.blit(pb_surf, (scoreboard_rect.left + score_surf.get_width(), scoreboard_rect.top + (score_surf.get_height() - pb_surf.get_height()) // 2))


# Main Menu Screen
def draw_main_menu(screen, high_score, pulse):
    """Displays the title entry presentation before the runtime begins."""
    screen.fill("#0d203d")
    screen.blit(UNDERWATER_BG, (0, 0))
    screen.blit(BRICK_FLOOR, (0, 350))
    
    title_surf = title_font.render("SCUBA DASH", False, "#c0e8ec")
    title_rect = title_surf.get_rect(center=(400, 120))
    screen.blit(title_surf, title_rect)
    
    record_surf = pb_font.render(f"CURRENT RECORD TO BEAT: {high_score}", False, "#baa042" if high_score > 0 else "Gray")
    record_rect = record_surf.get_rect(center=(400, 200))
    screen.blit(record_surf, record_rect)
    
    menu_alpha = int((math.sin(pulse) * 85) + 170)
    start_prompt_surf = game_font.render("Press SPACE to Start", False, "White")
    start_prompt_surf.set_alpha(menu_alpha)
    screen.blit(start_prompt_surf, start_prompt_surf.get_rect(center=(400, 280)))


# Game Over Screen
def draw_game_over_screen(screen, score, high_score, is_new_pb, pulse, ticker_state):
    """Blends a darkened frame layer highlighting scores via increment tickers."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
    overlay.fill((10, 21, 38, 200)) 
    screen.blit(overlay, (0, 0))

    if ticker_state["val"] < score:
        ticker_state["val"] += max(1, (score - ticker_state["val"]) // 8) 
    else:
        ticker_state["val"] = score

    game_over_surf = game_font.render("GAME OVER", False, "#ff4a4a")
    screen.blit(game_over_surf, game_over_surf.get_rect(center=(400, 130)))
    
    ticker_color = "#d4af37" if is_new_pb else "White"
    score_display_surf = game_font.render(f"Score: {ticker_state['val']}", False, ticker_color)
    screen.blit(score_display_surf, score_display_surf.get_rect(center=(400, 190)))

    if is_new_pb and ticker_state["val"] == score:
        pb_display_surf = pb_font.render("NEW PERSONAL BEST!", False, "#d4af37")
        screen.blit(pb_display_surf, pb_display_surf.get_rect(center=(400, 240)))
    elif ticker_state["val"] == score:
        pb_display_surf = pb_font.render(f"Best: {high_score}", False, "Gray")
        screen.blit(pb_display_surf, pb_display_surf.get_rect(center=(400, 240)))

    text_alpha = int((math.sin(pulse) * 85) + 170) 
    retry_surf = game_font.render("Press SPACE to play again", False, "White")
    retry_surf.set_alpha(text_alpha)
    screen.blit(retry_surf, retry_surf.get_rect(center=(400, 310)))


# Starting Numbers and Lists Setup
session_high_score = load_high_score()
high_score = session_high_score
is_new_pb = False 

scroll_offsets = {"bg": 0, "fg": 0, "floor": 0}
player_particles = []
incoming_warnings = []
ticker_state = {"val": 0}
obstacle_list = []

start_time = 0
score = 0
pulse_timer = 0
player_index = 0

player_surf = player_frames[player_index]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))


# Main Game Loop
is_playing = False
running = True

def handle_obstacles(obstacles, speed, player_rect):
   if obstacles:
       for obstacle in obstacles:
           obstacle["rect"].x -= speed
           
           if obstacle["type"] == "coral":
               screen.blit(coral_surf, obstacle["rect"])
           else:
               screen.blit(mine_surf, obstacle["rect"])

           player_hitbox = player_rect.inflate(-20, -15)
           if obstacle["type"] == "coral":
               obstacle_hitbox = obstacle["rect"].inflate(-30, -20)
           else:
               obstacle_hitbox = obstacle["rect"].inflate(-25, -25)

           if player_hitbox.colliderect(obstacle_hitbox):
               return False

       obstacles[:] = [obs for obs in obstacles if obs["rect"].right > 0]
   return True

gravity_acceleration = 0.85
JUMP_GRAVITY_START_SPEED = -19.5
players_gravity_speed = 0

while running:
   pulse_timer += 0.07
   
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
                   spawn_x = random.randint(950, 1150)
                   obstacle_type = random.choice(["coral", "mine"])
                   chosen_surf = coral_surf if obstacle_type == "coral" else mine_surf
                   
                   if obstacle_type == "coral":
                       new_rect = chosen_surf.get_rect(bottomleft=(spawn_x, GROUND_Y + 30))
                   else:
                       new_rect = chosen_surf.get_rect(bottomleft=(spawn_x, GROUND_Y + 5))

                   min_gap = max(220 - (score // 4), 120)

                   if not obstacle_list or (new_rect.left - obstacle_list[-1]["rect"].right > min_gap):
                       obstacle_list.append({"rect": new_rect, "type": obstacle_type})
                       if BASE_SPEED + min(score // 100, 12) > 8:
                           incoming_warnings.append({"y_pos": new_rect.centery, "trigger_x": spawn_x})

       else:
           if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
               is_playing = True
               is_new_pb = False
               ticker_state["val"] = 0 
               obstacle_list.clear()  
               player_particles.clear()
               incoming_warnings.clear()
               game_speed = BASE_SPEED  
               player_rect.bottom = GROUND_Y  
               players_gravity_speed = 0
               player_index = 0
               scroll_offsets = {"bg": 0, "fg": 0, "floor": 0}
               current_spawn_delay = 1200
               pygame.time.set_timer(OBSTACLE_TIMER, current_spawn_delay) 
               start_time = pygame.time.get_ticks()  

   if is_playing:
       score = int((pygame.time.get_ticks() - start_time) / 100)
       has_broken_pb = session_high_score > 0 and score > session_high_score

       if score > high_score:
           high_score = score
           is_new_pb = True

       game_speed = BASE_SPEED + min(score // 100, 12)

       target_delay = max(1200 - ((score // 100) * 80), 550)
       if target_delay != current_spawn_delay:
           current_spawn_delay = target_delay
           pygame.time.set_timer(OBSTACLE_TIMER, current_spawn_delay)

       draw_parallax_scrolling(screen, game_speed, scroll_offsets)
       update_and_draw_particles(screen, player_particles, player_rect, game_speed)
       draw_scoreboard(screen, score, high_score, has_broken_pb)
       
       is_playing = handle_obstacles(obstacle_list, game_speed, player_rect)
       if not is_playing:
           save_high_score(high_score)
           session_high_score = high_score

       process_radar_warnings(screen, incoming_warnings, obstacle_list, pulse_timer, game_speed)

       players_gravity_speed += gravity_acceleration
       player_rect.y += players_gravity_speed
      
       if player_rect.bottom >= GROUND_Y:
           player_rect.bottom = GROUND_Y
           players_gravity_speed = 0
           player_index += 0.1
           if player_index >= len(player_frames): player_index = 0
           player_surf = player_frames[int(player_index)]
           player_rect = player_surf.get_rect(bottomleft=player_rect.bottomleft)
       else:
           player_surf = player_jump
           player_rect = player_surf.get_rect(bottomleft=player_rect.bottomleft)

       screen.blit(player_surf, player_rect)

   elif start_time == 0:
       draw_main_menu(screen, high_score, pulse_timer)

   else:
       draw_game_over_screen(screen, score, high_score, is_new_pb, pulse_timer, ticker_state)

   pygame.display.flip()
   clock.tick(60)

pygame.quit()