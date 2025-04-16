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


def create_initial_grid(prob_one):
    return np.array([
        [1 if random.random() < prob_one else 0 for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ])


def create_glider_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    center = GRID_SIZE // 2
    pattern = [
        [0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    for i in range(5):
        for j in range(5):
            grid[center - 2 + i][center - 2 + j] = pattern[i][j]
    return grid


def plot_grid(grid, generation, stats_text):
    # Create a figure with adjusted size to make room for stats text
    plt.figure(figsize=(8, 8))
    
    # Create a specific area for the grid
    grid_ax = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    
    # Plot the grid in the designated area
    grid_ax.imshow(grid, cmap='Greys', interpolation='nearest', origin='upper')
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


def run_simulation():
    prob = get_initial_probability()
    wrap = get_wrap_mode()
    grid = create_initial_grid(prob)
    output_name = input("Enter the output PDF filename (without .pdf): ").strip()
    if not output_name:
        output_name = "simulation_report"
    pdf_path = output_name + ".pdf"

    with PdfPages(pdf_path) as pdf:
        for gen in range(1, GENERATIONS + 1):
            new_grid = update_grid(grid, wrap, gen)
            stability = compute_stability(grid, new_grid)
            alive_change = count_alive_change(grid, new_grid)
            variance = compute_variance(new_grid)
            alive_now = count_alive_cells(new_grid)

            stats = (
                f"Generation {gen}\n"
                f"Stability: {stability:.2f}%\n"
                f"Δ Alive: {alive_change}\n"
                f"Alive now: {alive_now}\n"
                f"Variance: {variance:.4f}"
            )

            print(stats.replace("\n", " | "))

            if gen == 1 or gen % SAVE_FREQUENCY == 0:
                plot_grid(new_grid, gen, stats)
                pdf.savefig()
            grid = new_grid
        print(f"\n✅ Saved full simulation report to '{pdf_path}'")


def run_gliders_simulation():
    wrap = get_wrap_mode()
    grid = create_glider_grid()
    output_name = input("Enter the output PDF filename (without .pdf): ").strip()
    if not output_name:
        output_name = "gliders_report"
    pdf_path = output_name + ".pdf"

    with PdfPages(pdf_path) as pdf:
        for gen in range(1, GENERATIONS + 1):
            new_grid = update_grid(grid, wrap, gen)
            stability = compute_stability(grid, new_grid)
            alive_now = count_alive_cells(new_grid)

            stats = (
                f"Generation {gen}\n"
                f"Stability: {stability:.2f}%\n"
                f"Alive now: {alive_now}"
            )

            print(stats.replace("\n", " | "))

            if gen == 1 or gen % SAVE_FREQUENCY == 0:
                plot_grid(new_grid, gen, stats)
                pdf.savefig()
            grid = new_grid
        print(f"\n✅ Saved gliders report to '{pdf_path}'")


def run_interesting_patterns():
    print("\n[TODO] This part is under construction.")


def main_menu():
    print("Select a question to play:")
    print("1. Answer to question 1")
    print("2. Answer to question 2")
    print("3. Answer to question 3")
    choice = input("Enter a number between 1-3: ")

    if choice == "1":
        run_simulation()
    elif choice == "2":
        run_gliders_simulation()
    elif choice == "3":
        run_interesting_patterns()
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main_menu()