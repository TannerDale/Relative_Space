# GAME where time slows by bodies and direction is pulled

import pygame
import random


class GAME:
    """GAME setup; window, obstacle, and time variance assignments.
    Game ends if the player collides with an obstacle, or a gate reaches the bottom of the screen
    without colliding with the player."""

    # Game Parameters #

    image_path = r'C:\Users\tanne\Documents\Relative_Space_Assets\Edited_Images\Object_Models'
    running = True
    end_reason = None

    screen_width = 700
    screen_height = 1000

    # Overall GAME Speed #

    game_speed = 0.75
    constant_speed_increase = 0.01
    speed_increase_timer = 100

    move_map = {
        pygame.K_LEFT: pygame.Vector2(-0.1, 0),
        pygame.K_RIGHT: pygame.Vector2(0.1, 0),
        pygame.K_UP: pygame.Vector2(0, -0.1),
        pygame.K_DOWN: pygame.Vector2(0, 0.1)
    }

    # Obstacle and Gate Parameters #

    gate_velocity = 5
    gravity_obstacle_velocity = 8
    random_obstacle_velocity = 11

    gate_spawn_timer = 2500
    gravity_obstacle_spawn_timer = 900
    random_obstacle_spawn_timer = 500

    # Time Variance Parameters #

    min_distance = 250
    dividing_factor = 100
    min_change_percent = 0.25

    # Sprite Groups #

    gravity_group = pygame.sprite.Group()
    obstacle_group = pygame.sprite.Group()
    gate_group = pygame.sprite.Group()
    non_player_group = pygame.sprite.Group()
    dirty_group_bot = pygame.sprite.LayeredDirty()
    dirty_group_top = pygame.sprite.LayeredDirty()

    def __init__(self):
        """Display settings."""

        self.screen = pygame.display.set_mode([self.screen_width, self.screen_height], pygame.DOUBLEBUF)
        self.background = pygame.image.load(GAME.image_path + r'\background.png')
        self.background = self.background.convert()

        self.dirty_group_bot.clear(self.screen, self.background)
        self.dirty_group_top.clear(self.screen, self.background)


class Score(pygame.sprite.DirtySprite):
    """Score counter in top-left of screen."""
    def __init__(self):
        super(Score, self).__init__()
        pygame.font.init()
        self.total_score = 0
        self.score_font = pygame.font.Font('freesansbold.ttf', 25)
        self.image = self.score_font.render('Score = {}'.format(self.total_score), True, 'white')
        self.rect = self.image.get_rect()
        self.rect.topleft = (25, 25)

        GAME.dirty_group_top.add(self)

    def update(self, time):
        self.total_score = (time // 500) + (Gate.passed_gates * 50)
        self.image = self.score_font.render('Score = {}'.format(self.total_score), True, 'white')
        self.dirty = 1


class GravityObstacle(pygame.sprite.DirtySprite):
    """Large obstacle that slows the game speed based on distance between itself and the player.
    Game ends if a collision occurs between itself and the player."""
    spawn_timer_init = GAME.gravity_obstacle_spawn_timer
    spawn_timer = spawn_timer_init
    velocity_constant = GAME.gravity_obstacle_velocity
    vel_init = pygame.Vector2(0, velocity_constant)
    size_options = [150, 175, 200]

    def __init__(self):
        super(GravityObstacle, self).__init__()
        """Assigns size, image, and location of gravity obstacle objects."""
        self.size = random.choice(self.size_options)
        self.radius = (self.size / 2)
        self.pos = pygame.Vector2(self.get_random_start(), -self.size)
        self.vel = self.vel_init
        self.delta_t = self.size_options.index(self.size)

        self.image = pygame.image.load(GAME.image_path + r'\earth_{}.png'.format(self.size)).convert_alpha()
        self.rect = self.image.get_rect()
        self.center = (self.rect.x + self.radius, self.rect.y + self.radius)

        self.mask = pygame.mask.from_surface(self.image, 254)

        GAME.gravity_group.add(self)
        GAME.obstacle_group.add(self)
        GAME.non_player_group.add(self)
        GAME.dirty_group_bot.add(self)

    def get_random_start(self):
        """Creates random starting point along screen top edge."""
        pos_x = random.randrange(0, GAME.screen_width - self.size // 2)

        return pos_x

    def update(self, time_multi):
        """Move until it is off-screen; then removes it from sprite groups."""
        vel_x, vel_y = self.vel_init
        vel_y *= time_multi
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.pos += self.vel
        if self.pos[1] < GAME.screen_height:
            self.rect.x, self.rect.y = self.pos
            self.center = (self.rect.x + self.radius, self.rect.y + self.radius)
            self.dirty = 1
        else:
            self.kill()


class RandomObstacle(pygame.sprite.DirtySprite):
    """Small obstacle that has no impact on game speed.
    Game ends if a collision occurs between itself and the player."""
    spawn_timer_init = GAME.random_obstacle_spawn_timer
    spawn_timer = spawn_timer_init
    velocity_constant = GAME.random_obstacle_velocity

    def __init__(self):
        """Assigns size, starting location, and velocity to random obstacle objects."""
        super(RandomObstacle, self).__init__()
        self.color = 'darkgray'
        self.size = 15
        self.radius = self.size / 2
        self.pos = self.start_position()
        self.vel_init = self.initial_velocity()
        self.vel = self.vel_init

        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.set_colorkey('green')
        self.rect = self.image.get_rect()

        self.center = (self.rect.x + self.radius, self.rect.y + self.radius)
        pygame.draw.circle(self.image, self.color, self.center, self.radius)
        self.mask = pygame.mask.from_surface(self.image, 253)

        GAME.obstacle_group.add(self)
        GAME.non_player_group.add(self)
        GAME.dirty_group_bot.add(self)

    def start_position(self):
        """Create random starting point along screen lateral edges."""
        x_pos = random.choice([(0 - self.size), GAME.screen_width])
        y_pos = random.randrange(50, GAME.screen_height - 50, 10)
        pos = pygame.Vector2(x_pos, y_pos)

        return pos

    def initial_velocity(self):
        """Create random initial velocity."""
        if self.pos[0] > 1:
            direction = -1
        else:
            direction = 1

        x_vel = random.randrange(2, 15) * direction
        y_vel = random.randrange(2, 15) * random.randrange(-1, 2)
        vel = pygame.Vector2(x_vel, y_vel)
        normalize_vector(vel)
        vel *= GAME.random_obstacle_velocity

        return vel

    def update(self, time_multi):
        """Move until it is off-screen; then remove it from sprite groups."""
        self.vel = self.vel_init * time_multi
        self.pos += self.vel

        if 0 < (self.pos[0] + self.size):
            if self.pos[0] < SPACE.screen_width:
                if self.pos[1] < SPACE.screen_height:
                    if 0 < self.pos[1] + self.size:
                        self.rect.x, self.rect.y = self.pos
                        self.center = (self.rect.x + self.radius, self.rect.y + self.radius)
                        self.dirty = 1
                    else:
                        self.kill()
                else:
                    self.kill()
            else:
                self.kill()
        else:
            self.kill()


class Gate(pygame.sprite.DirtySprite):
    """Rectangular object that must be hit to advance gameplay.
    Game ends if a gate reaches the bottom of screen without being hit.
    Disappears upon player collision."""
    spawn_timer_init = GAME.gate_spawn_timer
    spawn_timer = spawn_timer_init
    velocity_constant = GAME.gate_velocity
    vel_init = pygame.Vector2(0, velocity_constant)
    vel = vel_init
    passed_gates = 0

    def __init__(self):
        """Assigns size and location to gate objects."""
        super(Gate, self).__init__()
        self.width = 50
        self.height = 7.5
        self.color = 'gold1'
        self.size = (self.width, self.height)

        self.pos = pygame.Vector2(self.get_random_start(), 0 - self.width)
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.center = (self.rect.x + self.width, self.rect.y + self.height)

        GAME.gate_group.add(self)
        GAME.non_player_group.add(self)
        GAME.dirty_group_top.add(self)

    def get_random_start(self):
        """Create random starting point along screen top edge."""
        pos_x = random.randrange(0, GAME.screen_width - self.width)

        return pos_x

    def update(self, time_multi):
        """Move until it is off-screen; then remove it from sprite groups."""
        vel_x, vel_y = self.vel_init
        vel_y *= time_multi
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.pos += self.vel
        if self.pos[1] < GAME.screen_height:
            self.rect.x, self.rect.y = self.pos
            self.center = (self.rect.x + self.width, self.rect.y + self.height)
            self.dirty = 1
        else:
            self.kill()
            GAME.running = False
            GAME.end_message = 'You missed a gate! '


class Player(pygame.sprite.DirtySprite):
    """User controlled object. Movement is based on arrow-key presses and limited to the screen dimensions."""
    def __init__(self):
        super(Player, self).__init__()
        self.width = 10
        self.height = 25
        self.speed = 5.5
        self.color = 'white'
        self.pos = pygame.Vector2(GAME.screen_width // 2, GAME.screen_width // 2)

        self.image = pygame.Surface((self.width, self.height))
        self.image.set_colorkey('black')
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

        self.center = (self.rect.x + self.width, self.rect.y + self.height)
        self.mask = pygame.mask.from_surface(self.image)

        GAME.dirty_group_top.add(self)

    def update(self, move):
        """Updates the position of Player body based move movement commands."""
        normalize_vector(move)

        move *= self.speed
        self.pos += move

        if 1 > self.pos[0] + move[0]:
            self.pos[0] = 1
        if self.pos[0] > (GAME.screen_width - self.width):
            self.pos[0] = (GAME.screen_width - self.width) - 1
        if 1 > self.pos[1]:
            self.pos[1] = 1
        if self.pos[1] > (GAME.screen_height - self.height):
            self.pos[1] = (GAME.screen_height - self.height) - 1

        self.rect.x, self.rect.y = self.pos
        self.center = (self.rect.x + self.width / 2, self.rect.y + self.height / 2)
        self.dirty = 1


# Velocity Vector Normalization #


def normalize_vector(vec):
    """Ensures diagonal speed and linear speed are equal."""
    if vec.length() > 0:
        vec.normalize_ip()


# Distance Calculation #


def get_point_distance(pos_1, pos_2):
    """Calculates the distance between points player.center and obs.center."""
    delta_x = pos_1[0] - pos_2[0]
    delta_y = pos_1[1] - pos_2[1]
    delta_x = abs(delta_x)
    delta_y = abs(delta_y)
    distance = ((delta_x ** 2) + (delta_y ** 2)) ** (1 / 2)

    return distance


# Time Manipulation #


def check_distance(player, obs):
    """Uses distance between player and obstacle obs to find time modifier."""
    dist = get_point_distance(player.center, obs.center) - obs.radius
    if dist < GAME.min_distance:
        return dist, obs.delta_t
    else:
        return None, None


def get_time_multiplier():
    """Creates multiplier for timing and velocity changes."""
    obs_distances = [check_distance(player_1, obs) for obs in GAME.gravity_group]
    multi = 1
    for distance in obs_distances:
        if distance[0] is not None:
            curr_multi = (distance[0] / GAME.dividing_factor)
            if curr_multi < multi:
                multi = curr_multi

    if multi < GAME.min_change_percent:
        multi = GAME.min_change_percent

    multi *= GAME.game_speed

    GravityObstacle.spawn_timer = GravityObstacle.spawn_timer_init / multi
    RandomObstacle.spawn_timer = RandomObstacle.spawn_timer_init / multi

    return multi


# Main #


def main():
    clock = pygame.time.Clock()
    pygame.init()
    pygame.display.set_caption('Relative Space')

    current_time = 0
    while GAME.running:
        clock.tick(60)

        # Check for QUIT Events #

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME.running = False
                GAME.end_message = ''

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_ESCAPE]:
            GAME.end_message = ''
            GAME.running = False

        # Get Time Multiplier and Adjust Spawn Times #

        time_multiplier = get_time_multiplier()

        # Spawn Obstacles #

        current_time = pygame.time.get_ticks()

        if current_time > GAME.gate_spawn_timer:
            GAME.gate_spawn_timer = current_time + Gate.spawn_timer
            gate = Gate()

        if current_time > GAME.gravity_obstacle_spawn_timer:
            GAME.gravity_obstacle_spawn_timer = current_time + GravityObstacle.spawn_timer
            planet = GravityObstacle()

        if current_time > GAME.random_obstacle_spawn_timer:
            GAME.random_obstacle_spawn_timer = current_time + RandomObstacle.spawn_timer
            asteroid = RandomObstacle()

        # Check for Player Input #

        player_move_vector = pygame.Vector2(0, 0)
        for vector in (GAME.move_map[key] for key in GAME.move_map if pressed_keys[key]):
            player_move_vector += vector

        # Update Sprite Positions #

        player_1.update(player_move_vector)
        GAME.non_player_group.update(time_multiplier)

        # Check Gates #

        for gate in GAME.gate_group:
            if pygame.Rect.colliderect(player_1.rect, gate.rect):
                gate.kill()
                Gate.passed_gates += 1

        # Check for Obstacle Collisions #

        for obstacle in GAME.obstacle_group:
            if pygame.sprite.collide_mask(player_1, obstacle):
                GAME.running = False
                GAME.end_message = 'Kaboom!! You are dead. '
                break

        the_score.update(current_time)
        if not GAME.running:
            print('{}Your final score is {} points! You passed {} gates!'.format(
                GAME.end_message, the_score.total_score, Gate.passed_gates))
            break

        rects = GAME.dirty_group_bot.draw(SPACE.screen) + GAME.dirty_group_top.draw(SPACE.screen)

        pygame.display.update(rects)

        if current_time > GAME.speed_increase_timer:
            GAME.game_speed += GAME.constant_speed_increase
            GAME.speed_increase_timer += GAME.speed_increase_timer

    pygame.quit()


if __name__ == '__main__':
    SPACE = GAME()
    the_score = Score()
    player_1 = Player()
    main()
