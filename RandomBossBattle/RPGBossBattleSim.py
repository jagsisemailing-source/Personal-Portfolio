import pygame
import random as rand
import math
import os


pygame.init()

WIDTH, HEIGHT = 1200, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG Battle")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

script_dir = os.path.dirname(__file__)
image_path = os.path.join(script_dir, 'RPGBGimage.png')

background_image = pygame.image.load(image_path).convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)
LARGE_FONT = pygame.font.Font(None, 72)

class PlayerSprite:
    #Ai, changed it by adding the different phases
    def __init__(self):
        self.sprite_sheet = self.create_placeholder_sprite_sheet()
        self.frame_width = 96
        self.frame_height = 96
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.state = "idle"
        self.flipped = False
        self.animation_frames = {
            "idle": 4,
            "attack": 6,
            "defend": 3,
            "special": 8
        }
        self.x = 200
        self.y = 400
        
    def create_placeholder_sprite_sheet(self):
        sheet_width = 96 * 6
        sheet_height = 96 * 4
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        colors = {
            "idle": [(100, 150, 255), (120, 170, 255), (80, 130, 255), (140, 190, 255)],
            "attack": [(255, 100, 100), (255, 150, 150), (255, 200, 200), (255, 120, 120), (255, 180, 180), (255, 140, 140)],
            "defend": [(100, 255, 100), (150, 255, 150), (200, 255, 200)],
            "special": [(255, 255, 100), (255, 255, 150), (255, 255, 200), (255, 255, 120), 
                       (255, 255, 180), (255, 255, 140), (255, 255, 160), (255, 255, 130)]
        }
        frame_size = 96
        for state_index, (state, color_list) in enumerate(colors.items()):
            for frame_index, color in enumerate(color_list):
                x = frame_index * frame_size
                y = state_index * frame_size
                pygame.draw.rect(sheet, color, (x, y, frame_size-2, frame_size-2))
                pygame.draw.rect(sheet, BLACK, (x, y, frame_size-2, frame_size-2), 1)
        return sheet
    
    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.animation_timer = 0
    
    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % self.animation_frames[self.state]
    
    def draw(self, surface):
        state_index = list(self.animation_frames.keys()).index(self.state)
        src_x = self.current_frame * self.frame_width
        src_y = state_index * self.frame_height
        src_rect = pygame.Rect(src_x, src_y, self.frame_width, self.frame_height)
        frame_surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surface.blit(self.sprite_sheet, (0, 0), src_rect)
        if self.flipped:
            frame_surface = pygame.transform.flip(frame_surface, True, False)
        surface.blit(frame_surface, (self.x - self.frame_width // 2, self.y - self.frame_height // 2))

class Enemy:
    #Ai, changed it by the positioning, adding the purple attack warning
    def __init__(self):
        self.radius = 240
        self.x = WIDTH -100
        self.y = HEIGHT // 2 - 50
        self.color = (200, 50, 50)
        self.hit_flash_timer = 0
        self.hit_flash_duration = 0.3
        self.attack_warning_timer = 0
        self.attack_warning_duration = 0.2
        
    def start_attack_warning(self):
        self.attack_warning_timer = self.attack_warning_duration
        
    def take_damage(self):
        self.hit_flash_timer = self.hit_flash_duration
        
    def update(self, dt):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.attack_warning_timer > 0:
            self.attack_warning_timer -= dt
            
    def draw(self, surface):
        if self.hit_flash_timer > 0:
            color = (255, 255, 255)
        elif self.attack_warning_timer > 0:
            color = PURPLE
        else:
            color = self.color
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), self.radius, 5)
        eye_width = 40
        eye_height = 35
        eye_y = self.y - 30
        pygame.draw.rect(surface, (50, 50, 50), (self.x - 180, eye_y, eye_width, eye_height))
        pygame.draw.rect(surface, (50, 50, 50), (self.x - 110, eye_y, eye_width, eye_height))
        pupil_size = 18
        pygame.draw.rect(surface, (20, 20, 20), (self.x - 165, eye_y + 5, pupil_size, pupil_size))
        pygame.draw.rect(surface, (20, 20, 20), (self.x - 95, eye_y + 5, pupil_size, pupil_size))

class Projectile:
    #Ai, changed it by changing the speed, the size, and adding the collisions then damage
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 8
        self.radius = 20
        self.reached_target = False
        self.damage_dealt = False
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
        
    def check_collision(self, enemy_x, enemy_y, enemy_radius):
        distance = math.sqrt((enemy_x - self.x) ** 2 + (enemy_y - self.y) ** 2)
        return distance < (self.radius + enemy_radius)
        
    def update(self, enemy_x, enemy_y, enemy_radius):
        self.x += self.vx
        self.y += self.vy
        if not self.damage_dealt and self.check_collision(enemy_x, enemy_y, enemy_radius):
            self.damage_dealt = True
            self.reached_target = True
            return True, True
        distance_to_target = math.sqrt((self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2)
        if distance_to_target < 30 and not self.reached_target:
            self.reached_target = True
            return True, False
        return False, False
        
    def draw(self, surface):
        pygame.draw.circle(surface, (100, 150, 255), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (50, 100, 255), (int(self.x), int(self.y)), self.radius - 5)
        pygame.draw.circle(surface, (150, 200, 255), (int(self.x), int(self.y)), self.radius - 10)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_health_bar(surface, x, y, width, height, current_hp, max_hp, color_full, color_empty):
    pygame.draw.rect(surface, color_empty, (x, y, width, height))
    health_percentage = max(0, current_hp) / max_hp
    fill_width = int(width * health_percentage)
    pygame.draw.rect(surface, color_full, (x, y, fill_width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)

def draw_options(surface, x, y, width, height):
    pygame.draw.rect(surface, WHITE, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 5)

class Button:
    def __init__(self, rect, text, callback, bg=GRAY, fg=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.fg = fg
        self.hover = False

    def draw(self, surf):
        color = tuple(min(255, c + 30) for c in self.bg) if self.hover else self.bg
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, 2)
        txt = FONT.render(self.text, True, self.fg)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

def battle_screen():
    running = True
    player_hp = 100
    player_max_hp = 100
    enemy_hp = 500
    enemy_max_hp = 500
    items = 10
    options_x = 50
    options_y = 530
    options_w = WIDTH - 100
    options_h = 100
    padding = 20
    btn_w = int((options_w - padding * 5) / 4)
    btn_h = options_h - padding * 2
    btn_y = options_y + padding
    btn_x = options_x + padding
    game_phase = "player_turn"
    last_action_msg = ""
    attack_phase = "idle"   
    wait_timer = 0.0
    wait_delay = 0.5       
    red_radius = 0.0
    green_radius = 0.0
    circle_min = 10.0
    circle_max = 120.0     
    circle_speed = 180.0   
    attack_base_min = 0     
    attack_base_max = 40    
    special_phase = "idle"
    special_circles = []
    special_circle_radius = 30
    special_duration = 3.0
    special_start_time = 0
    special_current_charge = 0
    special_circles_hit = 0
    special_damage_per_circle = 10
    special_last_spawn_time = 0
    special_spawn_interval = 0.15
    special_animation_phase = "collecting"
    special_collected_circles = []
    special_shooting_circles = []
    special_animation_timer = 0
    enemy_attack_phase = "idle"
    enemy_charge_timer = 0
    enemy_charge_duration = rand.uniform(1.0, 2.5)
    exclamation_timer = 0
    exclamation_duration = 0.5
    player_defense_result = None
    defense_click_time = 0
    game_over = False
    game_won = False
    player_sprite = PlayerSprite()
    player_sprite.x = 200
    player_sprite.y = 400
    player_sprite.flipped = True
    enemy = Enemy()
    projectiles = []
    block = 0
    special_charge = 0

    def start_player_attack():
        nonlocal attack_phase, wait_timer, red_radius, green_radius, game_phase
        game_phase = "player_attacking"
        attack_phase = "waiting"
        wait_timer = wait_delay
        red_radius = 0.0
        green_radius = 0.0
        player_sprite.set_state("attack")

    def attack():
        nonlocal last_action_msg
        if game_phase == "player_turn":
            last_action_msg = "Prepare your attack..."
            start_player_attack()

    def complete_player_attack(damage=0, accuracy=0):
        nonlocal enemy_hp, last_action_msg, game_phase, special_charge, projectiles
        if damage > 0:
            projectiles.append(Projectile(
                player_sprite.x, player_sprite.y,
                enemy.x, enemy.y
            ))
            last_action_msg = f"Attack launched (accuracy {accuracy:.2f})"
            special_charge = min(100, special_charge + 5)
        else:
            last_action_msg = "Attack missed..."
        player_sprite.set_state("idle")
        game_phase = "enemy_turn"
        start_enemy_turn()

    def start_enemy_turn():
        nonlocal game_phase, enemy_attack_phase, enemy_charge_timer, enemy_charge_duration, last_action_msg
        if enemy_hp <= 0:
            return
        game_phase = "enemy_attacking"
        enemy_attack_phase = "charging"
        enemy_charge_duration = rand.uniform(1.0, 2.5)
        enemy_charge_timer = enemy_charge_duration
        last_action_msg = "Enemy is preparing an attack..."

    def process_enemy_attack():
        nonlocal player_hp, last_action_msg, player_defense_result, defense_click_time, game_phase, enemy_hp
        base_damage = rand.randint(15, 30)
        if player_defense_result == "parry":
            counter_damage = int(base_damage * 0.1)
            enemy_hp = max(0, enemy_hp - counter_damage)
            last_action_msg = f"Parry! Dealt {counter_damage} back!"
            enemy.take_damage()
        elif player_defense_result == "dodge":
            dmg = int(base_damage * 0.5)
            player_hp = max(0, player_hp - dmg)
            last_action_msg = f"Dodged! Took {dmg} damage."
        elif player_defense_result == "block":
            dmg = int(base_damage * 0.75)
            player_hp = max(0, player_hp - dmg)
            last_action_msg = f"Blocked! Took {dmg} damage."
        else:
            dmg = base_damage
            player_hp = max(0, player_hp - dmg)
            last_action_msg = f"Failed to defend! Took {dmg} damage!"
        player_defense_result = None
        defense_click_time = 0
        player_sprite.set_state("idle")
        game_phase = "player_turn"

    def defend_callback():
        nonlocal player_defense_result, defense_click_time, exclamation_timer, enemy_attack_phase
        if enemy_attack_phase == "attacking":
            reaction_time = exclamation_duration - exclamation_timer
            if reaction_time <= 0.1:
                player_defense_result = "parry"
            elif reaction_time <= 0.25:
                player_defense_result = "dodge"
            elif reaction_time <= 0.5:
                player_defense_result = "block"
            else:
                player_defense_result = None
            defense_click_time = reaction_time
            enemy_attack_phase = "resolved"
            player_sprite.set_state("defend")
            process_enemy_attack()

    def defend():
        nonlocal last_action_msg, block, special_charge, game_phase, player_hp
        if game_phase == "player_turn":
            base_damage = rand.randint(15, 30)
            reduced_damage = int(base_damage * 0.75)
            player_hp = max(0, player_hp - reduced_damage)
            block = reduced_damage
            last_action_msg = f"Defended! Took {reduced_damage} damage."
            special_charge = min(100, special_charge + 20)
            player_sprite.set_state("defend")
            game_phase = "player_turn"

    def item():
        nonlocal player_hp, last_action_msg, items, game_phase
        if game_phase != "player_turn":
            return
        if items <= 0:
            last_action_msg = "No items left!"
            return
        heal = 50
        player_hp = min(player_max_hp, player_hp + heal)
        items -= 1
        last_action_msg = f"Used item: healed {heal} HP. ({items} left)"
        game_phase = "enemy_turn"
        start_enemy_turn()

        #AI, related to the other special circle code, where i detailed how i changed it
    def special():
        nonlocal special_phase, special_charge, last_action_msg, game_phase, special_start_time, special_current_charge, special_circles_hit, special_last_spawn_time, special_animation_phase
        if game_phase != "player_turn":
            return
        if special_charge < 100:
            last_action_msg = f"Special not ready! {special_charge:.0f}% charged"
            return
        special_phase = "active"
        special_animation_phase = "collecting"
        special_current_charge = 100
        special_charge = 0
        special_start_time = pygame.time.get_ticks() / 1000.0
        special_last_spawn_time = special_start_time
        special_circles_hit = 0
        special_circles.clear()
        special_collected_circles.clear()
        special_shooting_circles.clear()
        game_phase = "player_attacking"
        player_sprite.set_state("special")
        last_action_msg = "Special: Click circles rapidly! Charge drains over time."

    def spawn_special_circle():
        nonlocal special_circles, special_last_spawn_time
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - special_last_spawn_time >= special_spawn_interval and special_animation_phase == "collecting":
            angle = rand.uniform(0, 2 * math.pi)
            distance = rand.uniform(80, 150)
            x = enemy.x + math.cos(angle) * distance
            y = enemy.y + math.sin(angle) * distance
            special_circles.append({
                'pos': [x, y],
                'clicked': False,
                'suck_progress': 0.0,
                'shoot_progress': 0.0
            })
            special_last_spawn_time = current_time

    def check_special_circle_click(pos):
        nonlocal special_circles, special_circles_hit, last_action_msg, special_collected_circles
        current_time = pygame.time.get_ticks() / 1000.0
        for circle in special_circles[:]:
            if circle['clicked']:
                continue
            distance = math.hypot(pos[0] - circle['pos'][0], pos[1] - circle['pos'][1])
            if distance <= special_circle_radius:
                circle['clicked'] = True
                special_circles_hit += 1
                collected_circle = circle.copy()
                collected_circle['original_pos'] = circle['pos'][:]
                special_collected_circles.append(collected_circle)
                last_action_msg = f"Special hit! {special_circles_hit} circles hit!"
                return True
        return False

    def update_special_attack():
        nonlocal special_phase, special_current_charge, special_circles, game_phase, enemy_hp, last_action_msg, special_animation_phase, special_collected_circles, special_shooting_circles, special_animation_timer
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - special_start_time
        if special_animation_phase == "collecting":
            special_current_charge = max(0, 100 - (elapsed / special_duration) * 100)
            spawn_special_circle()
            for circle in special_collected_circles:
                circle['suck_progress'] = min(1.0, circle['suck_progress'] + 0.05)
                progress = circle['suck_progress']
                circle['pos'][0] = circle['original_pos'][0] + (player_sprite.x - circle['original_pos'][0]) * progress
                circle['pos'][1] = circle['original_pos'][1] + (player_sprite.y - circle['original_pos'][1]) * progress
            if special_current_charge <= 0:
                special_animation_phase = "sucking"
                special_animation_timer = 1.0
                last_action_msg = "Gathering energy..."
        elif special_animation_phase == "sucking":
            special_animation_timer -= dt
            for circle in special_collected_circles:
                circle['suck_progress'] = min(1.0, circle['suck_progress'] + 0.05)
                progress = circle['suck_progress']
                circle['pos'][0] = circle['original_pos'][0] + (player_sprite.x - circle['original_pos'][0]) * progress
                circle['pos'][1] = circle['original_pos'][1] + (player_sprite.y - circle['original_pos'][1]) * progress
            if special_animation_timer <= 0:
                special_animation_phase = "shooting"
                for circle in special_collected_circles:
                    shooting_circle = {
                        'pos': [player_sprite.x, player_sprite.y],
                        'target_pos': [enemy.x + rand.uniform(-50, 50), enemy.y + rand.uniform(-50, 50)],
                        'shoot_progress': 0.0
                    }
                    special_shooting_circles.append(shooting_circle)
                special_collected_circles.clear()
                last_action_msg = "Firing!"
        elif special_animation_phase == "shooting":
            all_done = True
            for circle in special_shooting_circles:
                circle['shoot_progress'] = min(1.0, circle['shoot_progress'] + 0.08)
                progress = circle['shoot_progress']
                circle['pos'][0] = player_sprite.x + (circle['target_pos'][0] - player_sprite.x) * progress
                circle['pos'][1] = player_sprite.y + (circle['target_pos'][1] - player_sprite.y) * progress
                if circle['shoot_progress'] < 1.0:
                    all_done = False
            if all_done:
                special_animation_phase = "done"
                total_damage = special_circles_hit * special_damage_per_circle
                enemy_hp = max(0, enemy_hp - total_damage)
                enemy.take_damage()
                special_phase = "idle"
                special_circles = []
                special_collected_circles = []
                special_shooting_circles = []
                player_sprite.set_state("idle")
                last_action_msg = f"Special finished! {special_circles_hit} energy spheres dealt {total_damage} damage!"
                game_phase = "enemy_turn"
                start_enemy_turn()

    buttons = []
    def update_buttons():
        nonlocal buttons, special_charge, items, game_phase
        buttons = []
        buttons_enabled = (game_phase == "player_turn")
        labels = [
            ("Attack", attack if buttons_enabled else lambda: None), 
            ("Defend", defend if buttons_enabled else lambda: None),
            (f"Item ({items})", item if buttons_enabled else lambda: None), 
            (f"Special: {special_charge:.0f}%", special if buttons_enabled else lambda: None)
        ]
        cur_x = btn_x
        for label, cb in labels:
            btn_color = (200, 200, 200) if buttons_enabled else (100, 100, 100)
            buttons.append(Button((cur_x, btn_y, btn_w, btn_h), label, cb, bg=btn_color))
            cur_x += btn_w + padding
    
    update_buttons()

    clock = pygame.time.Clock()
    while running:
        dt = clock.tick(60) / 1000.0

        if player_hp <= 0 and not game_over and not game_won:
            game_over = True
        if enemy_hp <= 0 and not game_won and not game_over:
            game_won = True

        if game_over or game_won:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            SCREEN.blit(background_image, (0, 0))
            if game_over:
                text_surface = LARGE_FONT.render("YOU LOST", True, RED)
                text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
                SCREEN.blit(text_surface, text_rect)
            else:
                text_surface = LARGE_FONT.render("YOU WIN!", True, GREEN)
                text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
                SCREEN.blit(text_surface, text_rect)
            pygame.display.flip()
            continue

        player_sprite.update(dt)
        enemy.update(dt)
        projectiles_to_remove = []
        damage_to_deal = 0
        for projectile in projectiles:
            reached_target, hit_enemy = projectile.update(enemy.x, enemy.y, enemy.radius)
            if reached_target:
                projectiles_to_remove.append(projectile)
                if hit_enemy:
                    damage = rand.randint(attack_base_min, attack_base_max)
                    damage_to_deal += damage
                    enemy.take_damage()
        if damage_to_deal > 0:
            enemy_hp = max(0, enemy_hp - damage_to_deal)
            last_action_msg = f"Projectile hit! Dealt {damage_to_deal} damage!"
        for projectile in projectiles_to_remove:
            projectiles.remove(projectile)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for b in buttons:
                b.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if game_phase == "player_attacking" and attack_phase == "green":
                    center_x, center_y = WIDTH // 2, HEIGHT // 2
                    dist = math.hypot(mx - center_x, my - center_y)
                    if dist <= green_radius:
                        if green_radius == circle_max * 1.5:
                            complete_player_attack(0, 0)
                        elif red_radius > 0:
                            accuracy = max(0.0, 1.0 - abs(green_radius - red_radius) / red_radius)
                            dmg = int(attack_base_min + accuracy * (attack_base_max - attack_base_min))
                            complete_player_attack(dmg, accuracy)
                        else:
                            complete_player_attack(0, 0)     
                    else:
                        last_action_msg = "Attack missed (clicked outside the green meter)."
                        complete_player_attack(0, 0)
                    attack_phase = "idle"
                    red_radius = 0.0
                    green_radius = 0.0
                elif game_phase == "player_attacking" and special_phase == "active" and special_animation_phase == "collecting":
                    check_special_circle_click((mx, my))
                elif game_phase == "enemy_attacking" and enemy_attack_phase == "attacking":
                    defend_callback()

        if game_phase == "player_attacking" and attack_phase == "waiting":
            circle_speed = rand.uniform(100, 200)
            wait_timer -= dt
            if wait_timer <= 0.0:
                attack_phase = "red"
                red_radius = circle_min
        elif game_phase == "player_attacking" and attack_phase == "red":
            red_radius += circle_speed // 2 * dt
            if red_radius >= circle_max:
                red_radius = circle_max
                attack_phase = "green"
                green_radius = circle_min
        elif game_phase == "player_attacking" and attack_phase == "green":
            green_radius += circle_speed * dt
            if green_radius > circle_max * 1.5:
                green_radius = circle_max * 1.5
                complete_player_attack(0, 0)
                attack_phase = "idle"

        if game_phase == "enemy_attacking":
            if enemy_attack_phase == "charging":
                enemy_charge_timer -= dt
                if enemy_charge_timer <= 0.2 and enemy_charge_timer > 0:
                    enemy.start_attack_warning()
                elif enemy_charge_timer <= 0:
                    enemy_attack_phase = "attacking"
                    exclamation_timer = exclamation_duration
                    last_action_msg = "Enemy attacks! Click to defend NOW!"
            elif enemy_attack_phase == "attacking":
                exclamation_timer -= dt
                if exclamation_timer <= 0:
                    enemy_attack_phase = "resolved"
                    process_enemy_attack()

        if game_phase == "player_attacking" and special_phase == "active":
            update_special_attack()

        SCREEN.blit(background_image, (0, 0))
        enemy.draw(SCREEN)
        player_sprite.draw(SCREEN)
        for projectile in projectiles:
            projectile.draw(SCREEN)
        draw_text("Player HP", FONT, BLACK, SCREEN, 50, 50)
        draw_health_bar(SCREEN, 50, 80, 200, 20, player_hp, player_max_hp, GREEN, RED)
        draw_text(f"{player_hp}/{player_max_hp}", FONT, BLACK, SCREEN, 260, 80)
        draw_text("Enemy HP", FONT, BLACK, SCREEN, WIDTH - 170, 50)
        draw_health_bar(SCREEN, WIDTH - 250, 80, 200, 20, enemy_hp, enemy_max_hp, GREEN, RED)
        draw_text(f"{enemy_hp}/{enemy_max_hp}", FONT, BLACK, SCREEN, WIDTH - 280, 105)
        draw_text(f"Special Charge: {special_charge:.0f}%", FONT, BLACK, SCREEN, 50, 120)
        turn_text = "Your Turn" if game_phase == "player_turn" else "Enemy's Turn"
        turn_color = GREEN if game_phase == "player_turn" else RED
        draw_text(f"Phase: {turn_text}", FONT, turn_color, SCREEN, WIDTH // 2 - 80, 20)
        draw_text("Options", FONT, BLACK, SCREEN, options_x, options_y - 30)
        draw_options(SCREEN, options_x, options_y, options_w, options_h)
        update_buttons()
        for b in buttons:
            b.draw(SCREEN)

        if game_phase == "player_attacking" and attack_phase in ("red", "green"):
            center_x, center_y = WIDTH // 2, HEIGHT // 2
            max_draw_r = int(max(red_radius, green_radius, circle_max) + 24)
            surf_size = max(64, max_draw_r * 2)
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            surf_center = (surf.get_width() // 2, surf.get_height() // 2)
            if red_radius > 0:
                r_alpha = 140
                pygame.draw.circle(surf, (220, 40, 40, r_alpha), surf_center, max(1, int(red_radius)))
                pygame.draw.circle(surf, (200, 30, 30, 220), surf_center, int(circle_max), 3)
            if attack_phase == "green" and green_radius > 0:
                g_alpha = 120
                pygame.draw.circle(surf, (60, 200, 80, g_alpha), surf_center, max(1, int(green_radius)))
                pygame.draw.circle(surf, (40, 160, 60, 220), surf_center, max(1, int(green_radius)), 2)
            if attack_phase == "green":
                shake_x = rand.uniform(-10, 10)
                shake_y = rand.uniform(-10, 10)
            else:
                shake_x = rand.uniform(-2, 2)
                shake_y = rand.uniform(-2, 2)
            SCREEN.blit(surf, (center_x - surf_center[0] + shake_x, center_y - surf_center[1] + shake_y))

        elif game_phase == "player_attacking" and special_phase == "active":
            # AI, changed it by making the circles slightly transparent
            if special_animation_phase == "collecting":
                charge_width = 200
                charge_height = 20
                charge_x = enemy.x - charge_width // 2
                charge_y = enemy.y - 200
                fill_width = int(charge_width * (special_current_charge / 100))
                pygame.draw.rect(SCREEN, RED, (charge_x, charge_y, charge_width, charge_height))
                pygame.draw.rect(SCREEN, YELLOW, (charge_x, charge_y, fill_width, charge_height))
                pygame.draw.rect(SCREEN, BLACK, (charge_x, charge_y, charge_width, charge_height), 2)
                draw_text(f"SPECIAL: {special_current_charge:.0f}%", FONT, BLACK, SCREEN, charge_x, charge_y - 25)
                draw_text(f"Circles Hit: {special_circles_hit}", FONT, BLACK, SCREEN, charge_x, charge_y + 25)
            for circle in special_circles:
                if not circle['clicked']:
                    circle_surf = pygame.Surface((special_circle_radius * 2, special_circle_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surf, (255, 215, 0, 180), (special_circle_radius, special_circle_radius), special_circle_radius)
                    pygame.draw.circle(circle_surf, (200, 150, 0, 220), (special_circle_radius, special_circle_radius), special_circle_radius, 2)
                    SCREEN.blit(circle_surf, (int(circle['pos'][0]) - special_circle_radius, int(circle['pos'][1]) - special_circle_radius))
            for circle in special_collected_circles:
                circle_surf = pygame.Surface((special_circle_radius * 2, special_circle_radius * 2), pygame.SRCALPHA)
                alpha = int(180 * (1.0 - circle['suck_progress']))
                pygame.draw.circle(circle_surf, (0, 255, 0, alpha), (special_circle_radius, special_circle_radius), special_circle_radius)
                pygame.draw.circle(circle_surf, (0, 200, 0, alpha), (special_circle_radius, special_circle_radius), special_circle_radius, 2)
                SCREEN.blit(circle_surf, (int(circle['pos'][0]) - special_circle_radius, int(circle['pos'][1]) - special_circle_radius))
            for circle in special_shooting_circles:
                circle_surf = pygame.Surface((special_circle_radius * 2, special_circle_radius * 2), pygame.SRCALPHA)
                alpha = int(255 * (1.0 - circle['shoot_progress'] * 0.5))
                pygame.draw.circle(circle_surf, (255, 255, 0, alpha), (special_circle_radius, special_circle_radius), special_circle_radius)
                pygame.draw.circle(circle_surf, (255, 200, 0, alpha), (special_circle_radius, special_circle_radius), special_circle_radius, 2)
                SCREEN.blit(circle_surf, (int(circle['pos'][0]) - special_circle_radius, int(circle['pos'][1]) - special_circle_radius))

        if game_phase == "enemy_attacking" and enemy_attack_phase == "attacking":
            #Also Ai, but changed it by changing the colors and changing the positioning of the exclamation marks
            exclamation_color = (255, 0, 0)
            pygame.draw.rect(SCREEN, exclamation_color, (player_sprite.x - 4, player_sprite.y - 80, 8, 16))
            pygame.draw.rect(SCREEN, exclamation_color, (player_sprite.x - 4, player_sprite.y - 60, 8, 4))
            timer_width = 80
            timer_height = 6
            timer_x = player_sprite.x - timer_width // 2
            timer_y = player_sprite.y - 100
            fill_width = int(timer_width * (exclamation_timer / exclamation_duration))
            pygame.draw.rect(SCREEN, RED, (timer_x, timer_y, timer_width, timer_height))
            pygame.draw.rect(SCREEN, GREEN, (timer_x, timer_y, fill_width, timer_height))
            pygame.draw.rect(SCREEN, BLACK, (timer_x, timer_y, timer_width, timer_height), 1)
            draw_text("CLICK NOW!", SMALL_FONT, RED, SCREEN, player_sprite.x - 40, player_sprite.y - 120)

        draw_text(last_action_msg, FONT, BLACK, SCREEN, options_x, options_y - 60)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    battle_screen()