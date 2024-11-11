# %% [markdown]
# Лаборатоная работа № 4
# 
# Шамсутдинов Рустам БВТ2201

# %%
import pygame
import random
import math

# random.seed(52)

# %% [markdown]
# Константы симуляции

# %%
# Set up display
width, height = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRID_COLOR = (200, 200, 200)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


TICKS_TIME = 30

# Speeds
CIRCLE_SPEED = 4
TRIANGLE_SPEED = 3  
STARS_SPEED = 0 

# Lifetime
ABSOLUTE_CIRCLE_LIFE_TIME = 10_000 
ABSOLUTE_TRIANGLE_LIFE_TIME = 10_000  
ABSOLUTE_STARS_LIFE_TIME = 100_000  

CIRCLE_LIFE_TIME_WITHOUT_FOOD = 1_000
TRIANGLE_LIFE_TIME_WITHOUT_FOOD = 1_000  
STARS_LIFE_TIME_WITHOUT_FOOD = ABSOLUTE_STARS_LIFE_TIME

# Stars parameters
STARS_REPRODUCE_TIME = 1_000
STARS_DAMAGE_FROM_BEING_EATEN = 1_000 # in ticks


# eating distance parameters
CIRCLE_EATING_DISTANCE = 5
TRIANGLE_EATING_DISTANCE = 5

# Reproduction parameters
CIRCLE_CHILDREN_COUNT = 1
TRIANGLE_CHILDREN_COUNT = 1
STARS_CHILDREN_COUNT = 1


# Growtime
CIRCLE_GROW_TIME = 100
TRIANGLE_GROW_TIME = 100
STAR_GROW_TIME = 100

# vision range
CIRCLE_VISIBLE_DISTANCE = 40
TRIANGLE_VISIBLE_DISTANCE = 60

# Size
CIRCLE_SIZE = 10
TRIANGLE_SIZE = 15
STARS_SIZE = 20

# %%
# Predator class
class Circle:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = RED  
        self.radius = CIRCLE_SIZE
        self.speed = CIRCLE_SPEED
        self.life_time = ABSOLUTE_CIRCLE_LIFE_TIME
        self.food_time = CIRCLE_LIFE_TIME_WITHOUT_FOOD
        self.grow_time = CIRCLE_GROW_TIME
        self.vision_range = CIRCLE_VISIBLE_DISTANCE
        self.children_count = CIRCLE_CHILDREN_COUNT


    
    def aging(self):
        self.life_time -= TICKS_TIME
    
    def hunger(self):
        self.food_time -= TICKS_TIME

    def growing(self):
        self.grow_time -= TICKS_TIME


    def is_dead(self):
        return self.life_time <= 0 or self.food_time <= 0


    def eat(self):
        self.food_time = CIRCLE_LIFE_TIME_WITHOUT_FOOD

    def reproduce(self):

        children = []

        for _ in range(self.children_count):
            new_circle = Circle()
            new_circle.x = self.x
            new_circle.y = self.y
            new_circle.color = self.color
            new_circle.speed = self.speed // 2
            new_circle.life_time = ABSOLUTE_CIRCLE_LIFE_TIME
            new_circle.food_time = CIRCLE_LIFE_TIME_WITHOUT_FOOD
            new_circle.grow_time = CIRCLE_GROW_TIME
            new_circle.vision_range = CIRCLE_VISIBLE_DISTANCE // 2
            new_circle.children_count = CIRCLE_CHILDREN_COUNT

            children.append(new_circle)

        return children

    def is_grown(self):
        return self.grow_time <= 0

    def grow(self):
        self.speed = CIRCLE_SPEED
        self.vision_range = CIRCLE_VISIBLE_DISTANCE


    def move(self, target=None):
        if target:
            dx, dy = target[0] - self.x, target[1] - self.y
            dist_to_target = math.sqrt(dx**2 + dy**2)

            # Move towards target
            if 0 < dist_to_target <= self.vision_range:
                self.x += int(self.speed * dx / dist_to_target)
                self.y += int(self.speed * dy / dist_to_target)

                
            # track the target
            elif dist_to_target > self.vision_range:
                self.x += int(self.speed * dx / dist_to_target) // 3
                self.y += int(self.speed * dy / dist_to_target) // 3


    def tick_iteration(self):
        self.aging()
        self.hunger()
        self.growing()

        is_dead = self.is_dead()

        if not is_dead:
            if self.is_grown():
                self.grow()

        return is_dead
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)


# %%
# Pray class
class Triangle:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = BLUE
        self.size = TRIANGLE_SIZE
        self.speed = TRIANGLE_SPEED
        self.life_time = ABSOLUTE_TRIANGLE_LIFE_TIME
        self.food_time = TRIANGLE_LIFE_TIME_WITHOUT_FOOD
        self.grow_time = TRIANGLE_GROW_TIME
        self.vision_range = TRIANGLE_VISIBLE_DISTANCE
        self.children_count = TRIANGLE_CHILDREN_COUNT
    
    def aging(self):
        self.life_time -= TICKS_TIME
    
    def hunger(self):
        self.food_time -= TICKS_TIME

    def growing(self):
        self.grow_time -= TICKS_TIME

    def is_dead(self):
        return self.life_time <= 0 or self.food_time <= 0


    def eat(self):
        self.food_time = TRIANGLE_LIFE_TIME_WITHOUT_FOOD

    def reproduce(self):

        children = []

        for _ in range(self.children_count):
            new_triangle = Triangle()
            new_triangle.x = self.x
            new_triangle.y = self.y
            new_triangle.color = self.color
            new_triangle.size = self.size
            new_triangle.speed = self.speed // 2
            new_triangle.life_time = ABSOLUTE_TRIANGLE_LIFE_TIME
            new_triangle.food_time = TRIANGLE_LIFE_TIME_WITHOUT_FOOD
            new_triangle.grow_time = TRIANGLE_GROW_TIME
            new_triangle.vision_range = TRIANGLE_VISIBLE_DISTANCE // 2
            new_triangle.children_count = self.children_count

            children.append(new_triangle)

        return children
    
    def is_grown(self):
        return self.grow_time <= 0


    def grow(self):
        self.speed = TRIANGLE_SPEED
        self.vision_range = TRIANGLE_VISIBLE_DISTANCE


    def move(self, threat=None, food=None):
        if threat:
            dx, dy = self.x - threat[0], self.y - threat[1]
            dist_to_threat = math.sqrt(dx**2 + dy**2)

            if 0 < dist_to_threat <= self.vision_range:
                self.x += int(self.speed * dx / dist_to_threat)
                self.y += int(self.speed * dy / dist_to_threat)

                # Keep within screen boundaries
                self.x = max(0, min(self.x, width))
                self.y = max(0, min(self.y, height))
                return None

        if food:
            dx, dy = food[0] - self.x, food[1] - self.y
            dist_to_food = math.sqrt(dx**2 + dy**2)
            
            # move to food
            if 0 < dist_to_food <= self.vision_range:
                self.x += int(self.speed * dx / dist_to_food)
                self.y += int(self.speed * dy / dist_to_food)

            # search for food
            elif dist_to_food > self.vision_range:
                self.x += int(self.speed * dx / dist_to_food) // 3
                self.y += int(self.speed * dy / dist_to_food) // 3

            # Keep within screen boundaries
            self.x = max(0, min(self.x, width))
            self.y = max(0, min(self.y, height))
    # def move(self, threat=None, food=None):
    #     move_x, move_y = 0, 0

    #     # Убегаем от угрозы
    #     if threat:
    #         dx_threat, dy_threat = self.x - threat[0], self.y - threat[1]
    #         dist_to_threat = math.sqrt(dx_threat ** 2 + dy_threat ** 2)

    #         if 0 < dist_to_threat <= self.vision_range:
    #             move_x += self.speed * dx_threat / dist_to_threat
    #             move_y += self.speed * dy_threat / dist_to_threat

    #     # Двигаемся к еде
    #     if food:
    #         dx_food, dy_food = food[0] - self.x, food[1] - self.y
    #         dist_to_food = math.sqrt(dx_food ** 2 + dy_food ** 2)

    #         if 0 < dist_to_food <= self.vision_range:
    #             move_x += self.speed * dx_food / dist_to_food
    #             move_y += self.speed * dy_food / dist_to_food

    #     # Нормализуем направление движения и обновляем координаты
    #     total_movement = math.sqrt(move_x ** 2 + move_y ** 2)
    #     if total_movement > 0:
    #         self.x += int(move_x / total_movement * self.speed)
    #         self.y += int(move_y / total_movement * self.speed)

    #     # Ограничиваем движение в пределах экрана
    #     self.x = max(0, min(self.x, width))
    #     self.y = max(0, min(self.y, height))

    def tick_iteration(self):
        self.aging()
        self.hunger()
        self.growing()

        is_dead = self.is_dead()

        if not is_dead:
            if self.is_grown():
                self.grow()

        return is_dead

                
    def draw(self, surface):
        points = [(self.x, self.y - self.size),
                  (self.x - self.size, self.y + self.size),
                  (self.x + self.size, self.y + self.size)]
        pygame.draw.polygon(surface, self.color, points)

# %%
# Tree class
class Star:
    def __init__(self):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.color = GREEN  
        self.size = STARS_SIZE
        self.speed = STARS_SPEED
        self.life_time = ABSOLUTE_STARS_LIFE_TIME
        self.food_time = STARS_LIFE_TIME_WITHOUT_FOOD
        self.grow_time = STAR_GROW_TIME
        self.children_count = STARS_CHILDREN_COUNT
        self.tite_to_reproduce = STARS_REPRODUCE_TIME
        self.damage_from_being_eaten = STARS_DAMAGE_FROM_BEING_EATEN



    def aging(self):
        self.life_time -= TICKS_TIME
    
    def hunger(self):
        self.food_time -= TICKS_TIME

    def growing(self):
        self.grow_time -= TICKS_TIME

    def is_dead(self):
        return self.life_time <= 0 or self.food_time <= 0


    def eat(self):
        return None

    def reproduce(self):
        self.tite_to_reproduce = STARS_REPRODUCE_TIME

        children = []

        for _ in range(self.children_count):
            new_star = Star()

            # flying seeds
            new_star.x = random.randint(0, width)
            new_star.y = random.randint(0, height)

            new_star.color = GREEN
            new_star.radius = STARS_SIZE
            new_star.speed = STARS_SPEED // 2
            new_star.life_time = ABSOLUTE_STARS_LIFE_TIME // 2
            new_star.food_time = STARS_LIFE_TIME_WITHOUT_FOOD // 2
            new_star.grow_time = STAR_GROW_TIME
            new_star.children_count = STARS_CHILDREN_COUNT
            new_star.tite_to_reproduce = STARS_REPRODUCE_TIME * 3


            children.append(new_star)

        return children

    def is_grown(self):
        return self.grow_time <= 0

    def grow(self):
        self.speed = STARS_SPEED
        self.tite_to_reproduce = STARS_REPRODUCE_TIME
        self.damage_from_being_eaten = STARS_DAMAGE_FROM_BEING_EATEN
        self.life_time = ABSOLUTE_STARS_LIFE_TIME
        self.food_time = STARS_LIFE_TIME_WITHOUT_FOOD


    def is_ready_to_reproduce(self):
        return self.tite_to_reproduce <= 0

    def beeing_eaten(self):
        self.life_time -= self.damage_from_being_eaten


    def tick_iteration(self):
        self.aging()
        self.hunger()
        self.growing()

        children = []

        is_dead = self.is_dead()

        if not is_dead:
            if self.is_grown():
                self.grow()

            if self.is_ready_to_reproduce():
                children = self.reproduce()


        return is_dead, children


    def draw(self, surface):
        # Drawing star shape
        points = [
            (self.x, self.y - self.size),  # Top point
            (self.x + self.size // 2, self.y - self.size // 4),
            (self.x + self.size, self.y - self.size // 4),
            (self.x + self.size * 2 // 3, self.y + self.size // 4),
            (self.x + self.size * 3 // 4, self.y + self.size),
            (self.x, self.y + self.size // 2),
            (self.x - self.size * 3 // 4, self.y + self.size),
            (self.x - self.size * 2 // 3, self.y + self.size // 4),
            (self.x - self.size, self.y - self.size // 4),
            (self.x - self.size // 2, self.y - self.size // 4)
        ]
        pygame.draw.polygon(surface, self.color, points)

# %%

# Initialize pygame
pygame.init()


window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Predator-Prey Game with Stars")



# Helper function to find the closest entity
def find_closest(creature, targets):
    closest_target = None
    min_dist = float('inf')
    for target in targets:
        dist = math.sqrt((target.x - creature.x) ** 2 + (target.y - creature.y) ** 2)
        if dist < min_dist:
            min_dist = dist
            closest_target = target
    return closest_target, min_dist


# Game variables
max_circles = 10  # Limit the number of circles in the game
creatures = {
    "circle": [Circle() for _ in range(3)],
    "triangle": [Triangle() for _ in range(5)],
    "star": [Star() for _ in range(3)]
}

game_over = False

# Main game loop
running = True
clock = pygame.time.Clock()
respawn_timer = 0  # Timer for triangle respawn

# Function to draw grid lines
def draw_grid(surface, grid_size=50):
    for x in range(0, width, grid_size):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height))
    for y in range(0, height, grid_size):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y))

while running:
    window.fill(WHITE)

    # Draw grid for easier tracking
    draw_grid(window)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw creatures
    for circle in creatures['circle'][:]:  # Copy to safely remove within loop

        is_dead = circle.tick_iteration()
        if is_dead:
            creatures['circle'].remove(circle)
            continue

        closest_triangle, min_dist = find_closest(circle, creatures['triangle'])



        if closest_triangle and min_dist < CIRCLE_EATING_DISTANCE:  # Eat triangle if close enough
            if closest_triangle in creatures['triangle']:  # Check if triangle is still present
                creatures['triangle'].remove(closest_triangle)

                creatures['circle'] += circle.reproduce()

        else:
            # Move towards the closest triangle
            circle.move((closest_triangle.x, closest_triangle.y) if closest_triangle else None)
        circle.draw(window)


    for triangle in creatures['triangle']:

        is_dead = triangle.tick_iteration()
        if is_dead:
            creatures['triangle'].remove(triangle)
            continue


        closest_circle, dist_to_circle = find_closest(triangle, creatures['circle'])
        closest_star, dist_to_star = find_closest(triangle, creatures['star'])

        if closest_star and dist_to_star < TRIANGLE_EATING_DISTANCE:
            if closest_star in creatures['star']: 
                closest_star.beeing_eaten()

                creatures['triangle'] += triangle.reproduce()
        else:
            triangle.move(threat=(closest_circle.x, closest_circle.y), food=(closest_star.x, closest_star.y))
        
        triangle.draw(window)

    # Draw stars
    for star in creatures['star']:

        is_dead, children = star.tick_iteration()
        if is_dead:
            creatures['star'].remove(star)
            continue
        else:
            if children:
                creatures['star'] += children

        
        star.draw(window)


    # Update display
    pygame.display.flip()
    clock.tick(TICKS_TIME)

pygame.quit()



