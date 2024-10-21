import pygame
import math
import heapq
import time

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1200, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('AI Assignment 2')

# Define colors 
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
purple = (128, 0, 128)
orange = (255, 165, 0)
grey = (128, 128, 128)
blue = (0, 0, 255)
red = (255, 0, 0)
light_grey = (211, 211, 211)

# Define hexagon parameters
hex_size = 30  # Radius of the circumcircle
hex_height = math.sqrt(3) * hex_size 
hex_width = 2 * hex_size

# Define energy and steps cost
energy_cost_per_step = 1
step_cost_per_step = 1

# Function to calculate the vertices of a hexagon
def calculate_hexagon_vertices(center_x, center_y, size): 
    vertices = []
    for i in range(6):
        angle = math.radians(60 * i)  # Convert degrees to radians
        x = center_x + size * math.cos(angle)
        y = center_y + size * math.sin(angle)
        vertices.append((x, y))
    return vertices

# Calculate positions of hexagons in a 6x10 grid
def calculate_hexagon_positions(rows, cols, size):
    positions = []
    for row in range(rows):
        for col in range(cols):
            x = col * (3/2 * size)
            if col % 2 == 0:
                y = row * (math.sqrt(3) * size)
            else:
                y = row * (math.sqrt(3) * size) - (math.sqrt(3) / 2 * size)
            positions.append((x, y))
    return positions

# Define grid with cell types (obstacle, rewards, traps, empty spots)
grid = [
    ['start', 'empty_spot', 'empty_spot', 'empty_spot', 'reward1', 'empty_spot', 'empty_spot', 'empty_spot', 'empty_spot', 'empty_spot'],
    ['empty_spot', 'trap2', 'empty_spot', 'trap4', 'treasure', 'empty_spot', 'trap3', 'empty_spot', 'obstacle', 'empty_spot'],
    ['empty_spot', 'empty_spot', 'obstacle', 'empty_spot', 'obstacle', 'empty_spot', 'empty_spot', 'reward2', 'trap1', 'empty_spot'],
    ['obstacle', 'reward1', 'empty_spot', 'obstacle', 'empty_spot', 'trap3', 'obstacle', 'treasure', 'empty_spot', 'treasure'],
    ['empty_spot', 'empty_spot', 'trap2', 'treasure', 'obstacle', 'empty_spot', 'obstacle', 'obstacle', 'empty_spot', 'empty_spot'],
    ['empty_spot', 'empty_spot', 'green', 'empty_spot', 'empty_spot', 'reward2', 'empty_spot', 'empty_spot', 'empty_spot', 'empty_spot']
]




# A* algorithm function with Octile Distance heuristic
def astar(start, goal, grid, hexagon_positions):
    def heuristic(a, b):
        x1, y1 = a
        x2, y2 = b
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)
    
    def get_neighbors(pos):
        neighbors = []
        directions = [(+1, 0), (-1, 0), (0, +1), (0, -1), (+1, -1), (-1, +1)]
        for dir in directions:
            neighbor_pos = (pos[0] + dir[0], pos[1] + dir[1])
            if 0 <= neighbor_pos[0] < len(grid) and 0 <= neighbor_pos[1] < len(grid[0]):
                if grid[neighbor_pos[0]][neighbor_pos[1]] != 'obstacle' and not grid[neighbor_pos[0]][neighbor_pos[1]].startswith('trap'):
                    neighbors.append(neighbor_pos)
        return neighbors
    
    start_pos = start
    goal_pos = goal
    
    open_list = [(0, start_pos)]
    heapq.heapify(open_list)
    came_from = {}
    cost_so_far = {start_pos: 0}
    nodes_explored = 0  # Track nodes explored
    
    while open_list:
        nodes_explored += 1  # Increment nodes explored
        current_cost, current_pos = heapq.heappop(open_list)
        
        if current_pos == goal_pos:
            print(f"Nodes explored: {nodes_explored}")
            break
        
        for next_pos in get_neighbors(current_pos):
            new_cost = cost_so_far[current_pos] + 1  # Assuming uniform cost for now
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + heuristic(next_pos, goal_pos)  # Using heuristic for sorting
                heapq.heappush(open_list, (priority, next_pos))
                came_from[next_pos] = current_pos
    
    # Reconstruct path to goal
    path = []
    if goal_pos in came_from:
        pos = goal_pos
        while pos != start_pos:
            path.append(pos)
            pos = came_from[pos]
        path.append(start_pos)
        path.reverse()
    else:
        print(f"No path found to goal {goal_pos}")
    
    return path

# Function to draw the hexagons and grid
def draw_grid():
    for index, pos in enumerate(hexagon_positions):
        row = index // 10
        col = index % 10
        hexagon_vertices = calculate_hexagon_vertices(pos[0] + offset_x + hex_size, pos[1] + offset_y + hex_size, hex_size)
        
        # Determine color based on grid cell type
        if grid[row][col] == 'empty_spot':
            color = white
        elif grid[row][col] == 'reward1' or grid[row][col] == 'reward2':
            color = green
        elif grid[row][col].startswith('trap'):
            color = purple
        elif grid[row][col] == 'obstacle':
            color = grey
        elif grid[row][col] == 'treasure':
            color = orange
        elif grid[row][col] == 'start':
            color = red

        pygame.draw.polygon(window, color, hexagon_vertices, 0)  # Draw filled hexagon
        pygame.draw.polygon(window, black, hexagon_vertices, 1)  # Draw outline
        
        # Add labels for traps and rewards
        if grid[row][col].startswith('trap'):
            label = grid[row][col][-1]  # Get the trap number (e.g., '1' for 'trap1')
            font = pygame.font.Font(None, 24)
            text = font.render(f"t{label}", True, black)
            text_rect = text.get_rect(center=(pos[0] + offset_x + hex_size, pos[1] + offset_y + hex_size))
            window.blit(text, text_rect)
        elif grid[row][col].startswith('reward'):
            label = grid[row][col][-1]  # Get the reward number (e.g., '1' for 'reward1')
            font = pygame.font.Font(None, 24)
            text = font.render(f"r{label}", True, black)
            text_rect = text.get_rect(center=(pos[0] + offset_x + hex_size, pos[1] + offset_y + hex_size))
            window.blit(text, text_rect)

# Function to draw the path
def draw_path(path, color=blue):
    for i in range(len(path) - 1):
        start_center_x, start_center_y = hexagon_positions[path[i][0] * 10 + path[i][1]]
        end_center_x, end_center_y = hexagon_positions[path[i + 1][0] * 10 + path[i + 1][1]]
        pygame.draw.line(window, color, (start_center_x + offset_x + hex_size, start_center_y + offset_y + hex_size), (end_center_x + offset_x + hex_size, end_center_y + offset_y + hex_size), 3)

# Function to draw the information table
def draw_info_table(current_position, energy_level, treasures_collected, last_movement_direction, steps_taken):
    table_x = width - 300
    table_y = 20
    table_width = 280
    table_height = 550  # Increased height to accommodate steps taken
    table_bg_color = (220, 220, 220)
    table_border_color = black
    pygame.draw.rect(window, table_bg_color, (table_x, table_y, table_width, table_height))
    pygame.draw.rect(window, table_border_color, (table_x, table_y, table_width, table_height), 2)
    
    font = pygame.font.Font(None, 24)
    info_text = [
        f"Stats",
        f"---------------------------------",
        f"Current Position: {current_position}",
        f"Energy Level: {energy_level}",
        f"Treasures Collected: {treasures_collected}",
        f"Steps Taken: {steps_taken}",
        f"",
        f"Traps and Rewards",
        f"---------------------------------",
        f"Trap t1 : +2 energy",
        f"Trap t2 : +2 steps",
        f"Trap t3 : 2 steps back",
        f"Trap t4 : All treasures removed",
        f"Reward r1 : -0.5 energy",
        f"Reward r2 : -0.5 steps",
    ]
    
    for i, info in enumerate(info_text):
        text = font.render(info, True, black)
        text_rect = text.get_rect(left=table_x + 20, top=table_y + 20 + i * 30)
        window.blit(text, text_rect)

# Function to draw buttons
def draw_buttons():
    button_color = light_grey
    button_text_color = black
    button_font = pygame.font.Font(None, 24)
    
    buttons = [
        {"label": "Start", "rect": pygame.Rect(20, 20, 150, 40)},
        {"label": "Stop", "rect": pygame.Rect(20, 70, 150, 40)},
        {"label": "Restart", "rect": pygame.Rect(20, 120, 150, 40)},
        {"label": "Quit", "rect": pygame.Rect(20, 170, 150, 40)}
    ]
    
    for button in buttons:
        pygame.draw.rect(window, button_color, button["rect"])
        pygame.draw.rect(window, black, button["rect"], 2)
        text = button_font.render(button["label"], True, button_text_color)
        text_rect = text.get_rect(center=button["rect"].center)
        window.blit(text, text_rect)
    
    return buttons

# Variables to control the algorithm
algorithm_running = False
algorithm_restart = False

# Calculate positions of hexagons
hexagon_positions = calculate_hexagon_positions(6, 10, hex_size)

# Centering the grid
max_x, max_y = max(hexagon_positions, key=lambda pos: pos[0])[0], max(hexagon_positions, key=lambda pos: pos[1])[1]
offset_x = (width - max_x) // 2 - hex_size
offset_y = (height - max_y) // 2 - hex_size

# Main loop
running = True
path = []
total_path = []
current_position = (0, 0)
energy_level = 20
treasures_collected = 0
steps_taken = 0
treasures_positions = [(1, 4), (3, 7), (3, 9), (4, 3)]
goals = treasures_positions.copy()
last_movement_direction = "N/A"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                if button["rect"].collidepoint(mouse_pos):
                    if button["label"] == "Start":
                        algorithm_running = True
                    elif button["label"] == "Stop":
                        algorithm_running = False
                    elif button["label"] == "Restart":
                        algorithm_running = False
                        algorithm_restart = True
                    elif button["label"] == "Quit":
                        running = False

    if algorithm_restart:
        # Reset variables to restart the algorithm
        total_path = []
        current_position = (0, 0)
        energy_level = 20
        treasures_collected = 0
        steps_taken = 0
        goals = treasures_positions.copy()
        algorithm_restart = False

    if algorithm_running:
        window.fill(white)
        draw_grid()
        
        # Perform A* search to each goal in sequence
        if goals:
            goal = goals[0]
            path = astar(current_position, goal, grid, hexagon_positions)
            if path:
                for step in path:
                    total_path.append(step)  # Add current step to total path
                    
                    # Decrease energy level based on energy cost per step
                    energy_level -= energy_cost_per_step
                    
                    # Adjust steps taken based on current step cost
                    steps_taken += step_cost_per_step
                    
                    # Check if landed on reward1 (r1) to adjust energy cost
                    if grid[step[0]][step[1]] == 'reward1':
                        energy_cost_per_step = 0.5  # Adjust energy cost per step
                    elif grid[step[0]][step[1]] == 'reward2':
                        step_cost_per_step = 0.5  # Adjust step cost per step
                    
                    current_position = step
                    draw_grid()  # Redraw grid to update path
                    draw_path(total_path)  # Draw all steps taken so far
                    draw_info_table(current_position, energy_level, treasures_collected, last_movement_direction, steps_taken)
                    buttons = draw_buttons()  # Draw buttons
                    pygame.display.update()
                    time.sleep(0.2)  # Delay to simulate step-by-step movement
                treasures_collected += 1
                draw_path(path, green)  # Draw path in green
                pygame.display.update()
                time.sleep(1)  # Keep path green for 1 second
                goals.pop(0)
        
        draw_info_table(current_position, energy_level, treasures_collected, last_movement_direction, steps_taken)
    
    window.fill(white)
    draw_grid()
    draw_path(total_path)
    draw_info_table(current_position, energy_level, treasures_collected, last_movement_direction, steps_taken)
    buttons = draw_buttons()  # Draw buttons

    pygame.display.update()

pygame.quit()
