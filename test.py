import pygame
import sys
import random

# ----------------- Game Functions -----------------

def draw_floor():
    """Draws two floor surfaces to create a scrolling effect."""
    screen.blit(floor_surface, (floor_x_pos, 650))
    screen.blit(floor_surface, (floor_x_pos + 432, 650))

def create_pipe():
    """Creates a new pipe pair with a random height."""
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(500, random_pipe_pos - 200)) # 200 is the gap
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    """Moves all pipes in the list to the left."""
    for pipe in pipes:
        pipe.centerx -= 4 # Pipe speed
    # Filter out pipes that are no longer on the screen
    visible_pipes = [pipe for pipe in pipes if pipe.right > -50]
    return visible_pipes

def draw_pipes(pipes):
    """Draws all pipes in the list on the screen."""
    for pipe in pipes:
        if pipe.bottom >= 700: # It's a bottom pipe
            screen.blit(pipe_surface, pipe)
        else: # It's a top pipe, so we flip it
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    """Checks for collisions with pipes, floor, or ceiling."""
    # Collision with pipes
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            return False

    # Collision with top or bottom of the screen
    if bird_rect.top <= -50 or bird_rect.bottom >= 650:
        death_sound.play()
        return False

    return True

def pipe_score_check(pipes):
    """Checks if the bird has passed a pipe for scoring."""
    global score, can_score
    for pipe in pipes:
        if pipe.centerx == bird_rect.centerx and can_score:
            score += 1
            score_sound.play()
            can_score = False
    # Reset can_score when the bird moves past the last pipe
    if pipes and pipes[-1].centerx < bird_rect.centerx:
        can_score = True

def score_display(game_state):
    """Displays the current score or the final score."""
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)
    
    if game_state == 'game_over':
        # Final Score
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(216, 100))
        screen.blit(score_surface, score_rect)

        # High Score
        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(216, 600))
        screen.blit(high_score_surface, high_score_rect)
        
        # Restart message
        restart_surface = game_font.render('Press Space to Restart', True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(216, 350))
        screen.blit(restart_surface, restart_rect)

def update_score(score, high_score):
    """Updates the high score if the current score is greater."""
    if score > high_score:
        high_score = score
    return high_score

# ----------------- Pygame Initialization -----------------

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()

# Screen settings
screen_width = 432
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird by Lee(Gemini Pro)')

# Clock for controlling frame rate
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf' if pygame.font.match_font('04B_19') else None, 40)

# ----------------- Game Variables -----------------

# Physics
gravity = 0.20
bird_movement = 0
game_active = True

# Score
score = 0
high_score = 0
can_score = True

# ----------------- Loading Assets (using simple surfaces) -----------------

# Background
bg_surface = pygame.Surface((screen_width, screen_height))
bg_surface.fill((40, 150, 220)) # A nice sky blue

# Floor
floor_surface = pygame.Surface((432, 118))
floor_surface.fill((220, 200, 100)) # A sandy color

floor_x_pos = 0

# Bird
bird_surface = pygame.Surface((40, 30))
bird_surface.fill((255, 255, 0)) # Yellow
bird_rect = bird_surface.get_rect(center=(100, screen_height / 2))

# Pipes
pipe_surface = pygame.Surface((60, 400))
pipe_surface.fill((0, 180, 50)) # Green
pipe_list = []
pipe_height = [300, 400, 500]

# Custom event for spawning pipes
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200) # 1200 milliseconds = 1.2 seconds

# Custom event for scoring
PASSPIPE = pygame.USEREVENT + 1

# Sounds (using simple generated sounds if files not found)
try:
    flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
    death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
except pygame.error:
    print("Sound files not found, using dummy sounds.")
    # Dummy sound class if files are missing
    class DummySound:
        def play(self): pass
    flap_sound = death_sound = score_sound = DummySound()
    
# ----------------- Main Game Loop -----------------

while True:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0 # Reset gravity effect
                bird_movement -= 7 # Flap upwards
                flap_sound.play()
            
            if event.key == pygame.K_SPACE and not game_active:
                # Reset the game
                game_active = True
                pipe_list.clear()
                bird_rect.center = (100, screen_height / 2)
                bird_movement = 0
                score = 0
                can_score = True

        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        
        if event.type == PASSPIPE:
            score += 1
            score_sound.play()

    # --- Drawing the Background ---
    screen.blit(bg_surface, (0, 0))

    if game_active:
        # --- Game Logic ---
        # Bird movement
        bird_movement += gravity
        bird_rect.centery += int(bird_movement)
        
        # Pipe movement
        pipe_list = move_pipes(pipe_list)
        
        # Collision check
        game_active = check_collision(pipe_list)

        # Scoring
        pipe_score_check(pipe_list)

        # --- Drawing Game Elements ---
        draw_pipes(pipe_list)
        screen.blit(bird_surface, bird_rect)
        score_display('main_game')
    
    else: # Game Over Screen
        high_score = update_score(score, high_score)
        score_display('game_over')

    # --- Drawing the Floor ---
    floor_x_pos -= 1 # Move floor to the left
    draw_floor()
    if floor_x_pos <= -432: # Reset floor position to create infinite scroll
        floor_x_pos = 0

    # --- Update the Display ---
    pygame.display.update()
    
    # --- Control Frame Rate ---
    clock.tick(120) # Limit the game to 120 frames per second