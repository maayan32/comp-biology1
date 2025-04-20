import random
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  


# Magic numbers
GRID_SIZE = 150
GENERATIONS = 250
DEFAULT_PROBABILITY = 0.5


SAVE_FREQUENCY = 10


def get_initial_probability():
    print("Select initial probability for cell = 1:")
    probabilities = [0.25, 0.5, 0.75]
    for index, value in enumerate(probabilities):
        print(f"{index + 1}. {value * 100}%")
    choice = input("Enter 1, 2, or 3: ")
    if choice == "1":
        return probabilities[0]
    elif choice == "2":
        return probabilities[1]
    elif choice == "3":
        return probabilities[2]
    else:
        print("Invalid input. Defaulting to 50%.")
        return DEFAULT_PROBABILITY


def get_wrap_mode():
    print("Select boundary condition:")
    print("1. Regular (no wraparound)")
    print("2. Wraparound")
    choice = input("Enter 1 or 2: ")
    return choice == "2"

# this is for the user to choose what special pattern he wants to see in question 3
def get_interesting_pattern():
    print("Select an interesting pattern:")
    print("1. still life")
    print("2. global blinker")
    print("3. Period-4 Oscillator")
    print("4. Large Arrowhead")
    choice = input("Enter 1, 2, 3 or 4: ")
    if choice == "1":
        return 0
    elif choice == "2":
        return 1
    elif choice == "3":
        return 2
    elif choice == "4":
        return 3
    else:
        print("Invalid input. Defaulting to still life.")
        return 0


def create_initial_grid(prob_one):
    return np.array([
        [1 if random.random() < prob_one else 0 for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ])

# This function creates a grids with a glider-like pattern for both wraparound and regular mode

def create_glider_grid():
    grids = []
    center = GRID_SIZE // 2

    # Helper to place a pattern on a grid at offset
    def place_pattern(pattern, x_offset, y_offset):
        grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        for i in range(len(pattern)):
            for j in range(len(pattern[0])):
                grid[center + i + y_offset][center + j + x_offset] = pattern[i][j]
        grids.append(grid)

    # Pattern for middle of grid
    pattern = [
        [0, 0, 0, 1],
        [0, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
    ]
    regGrid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    # Step 1: Create the (border pattern) -> checkerboard style
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if i == 0 or j == 0 or i == GRID_SIZE - 1 or j == GRID_SIZE - 1:
                regGrid[i][j] = (i + j) % 2  

    # Step 2: Add the pattern in the middle

    center = GRID_SIZE // 2 - 2  
    for i in range(4):
        for j in range(4):
            regGrid[center + i][center + j] = pattern[i][j]
    # add first pattern to the grid for regular mode
    grids.append(regGrid)
    # add second pattern to the grid for wraparound mode (no border)
    place_pattern(pattern, -2, -2)  # center it at grid middle

    return grids
# this function creates the interesting patterns (begining grids) for the user to choose from
def create_interesting_patterns():
    grids = []
    center = GRID_SIZE // 2
   # Pattern : Full-grid checkerboard -> this pattern stayes the same each generation
    grid1 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            grid1[i, j] = (i + j) % 2
    grids.append(grid1)

    # pattern 2 : global blinker -> all 0 :
    grid2 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    grids.append(grid2)
    
    # Pattern 3: Full-grid 3-live-cell blocks (starts with (11 10) pattern for each block)  )
    grid3 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for i in range(0, GRID_SIZE, 2):
        for j in range(0, GRID_SIZE, 2):
            if i + 1 < GRID_SIZE and j + 1 < GRID_SIZE:
                # 3 out of 4 cells alive (bottom-right is dead)
                grid3[i][j] = 1
                grid3[i][j+1] = 1
                grid3[i+1][j] = 1
    grids.append(grid3)
    # Pattern 4: Full-grid Large Arrowhead pattern starts with 6x6 pattern that looks like: all across the grid
    pattern6 = [
        [0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0],
        [1, 1, 0, 1, 1, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]
    grid4 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for i in range(0, GRID_SIZE, 6):  # Steps of 6 to fit the 6x6 pattern
        for j in range(0, GRID_SIZE, 6):
            for k in range(6):
                for l in range(6):
                    if i + k < GRID_SIZE and j + l < GRID_SIZE:
                        grid4[i + k][j + l] = pattern6[k][l]
    grids.append(grid4)
    return grids


# This function plots the grid and stats text in a specific layout 
# to save to a PDF file. It uses matplotlib to create the plots.
def plot_grid(grid, generation, stats_text):
    # Create a figure with adjusted size to make room for stats text
    plt.figure(figsize=(8, 8))
    
    # Create a specific area for the grid
    grid_ax = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    
    # Plot the grid in the designated area
    grid_ax.imshow(grid, cmap='Greys', interpolation='nearest', origin='upper', vmin=0, vmax=1)
    # grid_ax.imshow(grid, cmap='Greys', interpolation='nearest', origin='upper')
    grid_ax.set_title(f"Generation {generation}")
    grid_ax.axis('off')

    # blue squares
    for i in range(0, GRID_SIZE, 2):
        for j in range(0, GRID_SIZE, 2):
            if i + 1 >= GRID_SIZE or j + 1 >= GRID_SIZE:
                continue
            grid_ax.plot(
                [j - 0.5, j + 1.5, j + 1.5, j - 0.5, j - 0.5],
                [i - 0.5, i - 0.5, i + 1.5, i + 1.5, i - 0.5],
                color='blue',
                linewidth=0.5
            )

    # red squares
    for i in range(1, GRID_SIZE, 2):
        for j in range(1, GRID_SIZE, 2):
            if i + 1 >= GRID_SIZE or j + 1 >= GRID_SIZE:
                continue
            grid_ax.plot(
                [j - 0.5, j + 1.5, j + 1.5, j - 0.5, j - 0.5],
                [i - 0.5, i - 0.5, i + 1.5, i + 1.5, i - 0.5],
                color='red',
                linewidth=0.5
            )
    
    # Create a text area at the bottom for stats text
    text_ax = plt.subplot2grid((4, 1), (3, 0))
    text_ax.axis('off')  # Hide axes
    text_ax.text(0.01, 0.5, stats_text, fontsize=10, va='center', family='monospace')
    
    plt.tight_layout()


def update_grid(grid, wraparound, generation):
    N = GRID_SIZE
    new_grid = copy.deepcopy(grid)
    offset = 0 if generation % 2 == 1 else 1
    for i in range(offset, N, 2):
        for j in range(offset, N, 2):
            block = []
            coords = []
            for di in [0, 1]:
                for dj in [0, 1]:
                    ni = (i + di) % N if wraparound else i + di
                    nj = (j + dj) % N if wraparound else j + dj
                    if ni >= N or nj >= N:
                        continue
                    block.append(grid[ni][nj])
                    coords.append((ni, nj))

            if len(block) < 4:
                continue

            count = sum(block)
            if count == 2:
                continue
            elif count in [0, 1, 4]:
                for idx, (ni, nj) in enumerate(coords):
                    new_grid[ni][nj] = 1 - grid[ni][nj]
            elif count == 3:
                flipped = [1 - x for x in block]
                rotated = flipped[::-1]
                for idx, (ni, nj) in enumerate(coords):
                    new_grid[ni][nj] = rotated[idx]
    return new_grid


def compute_stability(prev, curr):
    unchanged = np.sum(prev == curr)
    total = GRID_SIZE * GRID_SIZE
    return (unchanged / total) * 100


def count_alive_cells(grid):
    return np.sum(grid)


def count_alive_change(prev, curr):
    return np.sum(curr) - np.sum(prev)


def compute_variance(grid):
    return np.var(grid)

# This function simulates the Game of Life and saves the results to a PDF file.
def simulate_and_save(grid, wrap, pdf_path, include_alive_change=False, save_all_first_10=True):
    with PdfPages(pdf_path) as pdf:
        for gen in range(1, GENERATIONS + 1):
            new_grid = update_grid(grid, wrap, gen)
            stability = compute_stability(grid, new_grid)
            alive_now = count_alive_cells(new_grid)
            variance = compute_variance(new_grid) if include_alive_change else None
            alive_change = count_alive_change(grid, new_grid) if include_alive_change else None
            # save the stats to a text file
            stats_lines = [
                f"Generation {gen}",
                f"Stability: {stability:.2f}%",
                f"Alive now: {alive_now}",
            ]
            if include_alive_change:
                stats_lines.extend([
                    f"Δ Alive: {alive_change}",
                    f"Variance: {variance:.4f}",
                ])

            stats = "\n".join(stats_lines)
            print(stats.replace("\n", " | "))

            if (save_all_first_10 and gen <= 10) or gen % SAVE_FREQUENCY == 0:
                plot_grid(new_grid, gen, stats)
                pdf.savefig()

            grid = new_grid


# This function runs the main simulation based on user input for initial probability and wrap mode.
def run_simulation():
    # Get the initial probability from the user
    prob = get_initial_probability()
    wrap = get_wrap_mode()
    # create the initial grid based on the user input
    grid = create_initial_grid(prob)
    output_name = input("Enter the output PDF filename (without .pdf): ").strip() or "simulation_report"
    pdf_path = output_name + ".pdf"
    
    simulate_and_save(grid, wrap, pdf_path, include_alive_change=True)
    print(f"\n✅ Saved full simulation report to '{pdf_path}'")

# this function runs the glider grids simulation
def run_gliders_simulation():
    # Get the wrap mode from the user
    wrap = get_wrap_mode()
    # create both beginning grids for the glider simulation
    grids = create_glider_grid()
    #  get the spisific grid that matches the wrap mode (0 for regular, 1 for wraparound)
    grid = grids[wrap]
    output_name = input("Enter the output PDF filename (without .pdf): ").strip() or "gliders_report"
    pdf_path = output_name + ".pdf"

    simulate_and_save(grid, wrap, pdf_path, include_alive_change=False)
    print(f"\n✅ Saved gliders report to '{pdf_path}'")

# this function runs the interesting patterns simulation
def run_interesting_patterns():
    # for this question we used wraparound mode only
    wrap = 1
     # get the begining grids for the interesting patterns
    patterns = create_interesting_patterns()
    #get what pattern the user wants to see
    pattern = get_interesting_pattern()
    grid = patterns[pattern]
    output_name = input(f"Enter output PDF name for pattern: ").strip() or f"interesting_pattern_{pattern + 1}"
    pdf_path = output_name + ".pdf"

    simulate_and_save(grid, wrap, pdf_path, include_alive_change=False)
    print(f"\n✅ Saved interesting pattern to '{pdf_path}'")


# This function displays the main menu and handles user input for running simulations.
def main_menu():
    exit_flag = True
    while exit_flag:
        print("Welcome to the Game of Life Simulation!")
        print("1. Run simulation")
        print("2. Run gliders simulation")
        print("3. Run interesting patterns simulation")
        print("4. Exit")
        choice = input("Enter a number between 1-4: ")

        if choice == "1":
            run_simulation()
        elif choice == "2":
            run_gliders_simulation()
        elif choice == "3":
            run_interesting_patterns()
        elif choice == "4":
            exit_flag = False
            print("Exiting the program.")
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main_menu()