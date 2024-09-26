import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mysql.connector

# Параметри
grid_size = 50  # розмірність решітки
P_burn = 0.3  # ймовірність загоряння для незайманої клітини
T_burn = 3  # час горіння клітини

# Стан клітин
UNBURNED = 0
BURNING = 1
BURNED = 2

# Ініціалізація простору клітинного автомата
grid = np.zeros((grid_size, grid_size), dtype=int)
burn_time = np.zeros((grid_size, grid_size), dtype=int)

# Випадкове початкове загоряння
num_initial_burning = 5
initial_burning_cells = np.random.choice(grid_size**2, num_initial_burning, replace=False)
for cell in initial_burning_cells:
    x, y = cell // grid_size, cell % grid_size
    grid[x, y] = BURNING
    burn_time[x, y] = T_burn

def update_grid(grid, burn_time):
    new_grid = grid.copy()
    for x in range(grid_size):
        for y in range(grid_size):
            if grid[x, y] == UNBURNED:
                # Перевірка сусідніх клітин на горіння
                burning_neighbors = (
                    (x > 0 and grid[x-1, y] == BURNING) or
                    (x < grid_size-1 and grid[x+1, y] == BURNING) or
                    (y > 0 and grid[x, y-1] == BURNING) or
                    (y < grid_size-1 and grid[x, y+1] == BURNING)
                )
                if burning_neighbors and np.random.rand() < P_burn:
                    new_grid[x, y] = BURNING
                    burn_time[x, y] = T_burn
            elif grid[x, y] == BURNING:
                burn_time[x, y] -= 1
                if burn_time[x, y] == 0:
                    new_grid[x, y] = BURNED
    return new_grid

# Візуалізація процесу
def animate(i):
    global grid, burn_time
    grid = update_grid(grid, burn_time)
    mat.set_data(grid)
    return [mat]

# Кольори для кожного стану клітин
cmap = plt.cm.colors.ListedColormap(['green', 'orange', 'black'])
bounds = [0, 1, 2, 3]
norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots()
mat = ax.matshow(grid, cmap=cmap, norm=norm)
ani = animation.FuncAnimation(fig, animate, frames=200, interval=200, blit=True)


# Функція для обчислення результатів
def calculate_results(grid):
    total_cells = grid_size * grid_size
    burned_cells = np.count_nonzero(grid == BURNED)
    burned_ratio = burned_cells / total_cells
    return burned_cells, burned_ratio

# Збереження результатів в базу даних
def save_results_to_db(P_burn, T_burn, burned_cells, burned_ratio):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='forest_fire',
            user='root',
            password='04082005'
        )
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO fire_simulation_results (P_burn, T_burn, burned_cells, burned_ratio)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (P_burn, T_burn, burned_cells, burned_ratio))
        connection.commit()

    except mysql.connector.Error as error:
        print("Failed to insert record into MySQL table {}".format(error))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

plt.title(f'P_burn = {P_burn}, T_burn = {T_burn}')
plt.show()
burned_cells, burned_ratio = calculate_results(grid)
save_results_to_db(P_burn, T_burn, burned_cells, burned_ratio)

# Приклад різних значень параметрів
P_burn_values = [0.1, 0.5]
T_burn_values = [2, 4]

for P_burn in P_burn_values:
    for T_burn in T_burn_values:
        grid = np.zeros((grid_size, grid_size), dtype=int)
        burn_time = np.zeros((grid_size, grid_size), dtype=int)
        for cell in initial_burning_cells:
            x, y = cell // grid_size, cell % grid_size
            grid[x, y] = BURNING
            burn_time[x, y] = T_burn

        fig, ax = plt.subplots()
        mat = ax.matshow(grid, cmap=cmap, norm=norm)
        ani = animation.FuncAnimation(fig, animate, frames=200, interval=200, blit=True)
        plt.title(f'P_burn = {P_burn}, T_burn = {T_burn}')
        plt.show()

        burned_cells, burned_ratio = calculate_results(grid)
        save_results_to_db(P_burn, T_burn, burned_cells, burned_ratio)
