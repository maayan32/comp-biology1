import random
import copy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  
import tkinter as tk
from tkinter import messagebox, filedialog
import sys


# Constants
GRID_SIZE = 150
GENERATIONS = 250
DEFAULT_PROBABILITY = 0.5
SAVE_FREQUENCY = 10

matplotlib.use("Agg")  # Non-interactive backend - prevent matplotlib GUI plots display - plots appear only on the PDF
    
def get_initial_probability_gui():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    choices = {"25%": 0.25, "50%": 0.5, "75%": 0.75}
    choice = tk.StringVar()

    def select():
        root.quit()


    top = tk.Toplevel()
    def on_close():
        root.quit()
    top.protocol("WM_DELETE_WINDOW", on_close)
    top.title("Select Initial Probability")
    top.configure(bg="#f0f0f0")
    tk.Label(top, text="Select initial probability for cell = 1:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=10)
    for label, prob in choices.items():
        tk.Radiobutton(top, text=label, variable=choice, value=prob, bg="#f0f0f0").pack(anchor='w', padx=20)
    tk.Button(top, text="OK", command=select, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), width=10).pack(pady=15)

    root.mainloop()
    top.destroy()
    return float(choice.get()) if choice.get() else DEFAULT_PROBABILITY
    
def get_interesting_pattern_gui():
    root = tk.Tk()
    root.withdraw()

    patterns = [
        "Still Life",
        "Global Blinker",
        "Period-4 Oscillator",
        "Large Arrowhead"
    ]
    selection = tk.IntVar()
    selection.set(0)

    def submit():
        root.quit()
   

    top = tk.Toplevel()
    def on_close():
        root.quit()
    top.protocol("WM_DELETE_WINDOW", on_close)
    top.title("Choose Pattern")
    top.configure(bg="#f0f0f0")
    tk.Label(top, text="Select an interesting pattern:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=10)
    for idx, name in enumerate(patterns):
        tk.Radiobutton(top, text=name, variable=selection, value=idx, bg="#f0f0f0").pack(anchor='w', padx=20)
    tk.Button(top, text="OK", command=submit, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), width=10).pack(pady=15)

    root.mainloop()
    top.destroy()
    return selection.get()

# GUI: Wrap Mode
def get_wrap_mode_gui():
    root = tk.Tk()
    root.withdraw()
    wrap_mode = tk.BooleanVar()

    def choose_wrap():
        wrap_mode.set(True)
        root.quit()

    def choose_regular():
        wrap_mode.set(False)
        root.quit()
   

    top = tk.Toplevel()
    def on_close():
        root.quit()
    top.protocol("WM_DELETE_WINDOW", on_close)
    top.title("Boundary Condition")
    top.configure(bg="#f0f0f0")
    tk.Label(top, text="Select boundary condition:", font=("Helvetica", 12), bg="#f0f0f0").pack(pady=10)
    tk.Button(top, text="Regular (no wraparound)", width=30, command=choose_regular, bg="#2196F3", fg="white").pack(pady=5)
    tk.Button(top, text="Wraparound", width=30, command=choose_wrap, bg="#2196F3", fg="white").pack(pady=5)

    root.mainloop()
    top.destroy()
    return wrap_mode.get()

# this function creates the initial grid based on the user input for the probability of a cell being alive
# its used for the first question and the glider simulation
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

# this function holds the main logic of the automation, the rules of the 'game'. 
# it updates the grid based on the rules of the automaton one generation at a time.
def update_grid(grid, wraparound, generation):
    N = GRID_SIZE
    new_grid = copy.deepcopy(grid)
    # this way we decide which cells (meaning red or blue block) to check based on the generation number
    offset = 0 if generation % 2 == 1 else 1
    # iterate over the 4x4 blocks of cells in the grid
    # the offset is used to determine which cells to check based on the generation number
    for i in range(offset, N, 2):
        for j in range(offset, N, 2):
            # Check the 2x2 block of cells to determine the new state for the next generation
            block = []
            coords = []
            # iterate over the 2x2 block of cells 
            for di in [0, 1]:
                for dj in [0, 1]:
                    # Get the coordinates of the cells in the block, take into account wraparound, if so go in a circle (%)

                    ni = (i + di) % N if wraparound else i + di
                    nj = (j + dj) % N if wraparound else j + dj
                    if ni >= N or nj >= N:
                        continue
                    block.append(grid[ni][nj])
                    coords.append((ni, nj))
            # check if the block is valid (4 cells) (for non-wraparound mode)
            if len(block) < 4:
                continue
            # Count the number of alive cells in the block to determine what rules to apply
            count = sum(block)
            # if two cells are alive, we do nothing
            if count == 2:
                continue
            # if 3 cells are alive, we flip the state of the block (1->0, 0->1)
            elif count in [0, 1, 4]:
                for idx, (ni, nj) in enumerate(coords):
                    new_grid[ni][nj] = 1 - grid[ni][nj]
            # if there are 3 alive cells, we flip the state of the block and rotate it 180 degrees clockwise
            elif count == 3:
                flipped = [1 - x for x in block]
                rotated = flipped[::-1]
                for idx, (ni, nj) in enumerate(coords):
                    new_grid[ni][nj] = rotated[idx]
    return new_grid

# This function computes the stability of the grid by comparing the previous and current generations.
def compute_stability(prev, curr):
    unchanged = np.sum(prev == curr)
    total = GRID_SIZE * GRID_SIZE
    return (unchanged / total) * 100

# This function counts the number of alive cells in the grid.
def count_alive_cells(grid):
    return np.sum(grid)

# This function counts the change in the number of alive cells between two generations.
def count_alive_change(prev, curr):
    return np.sum(curr) - np.sum(prev)

# This function computes the variance of the grid to measure the distribution of alive cells.
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
                plt.close()


            grid = new_grid

# GUI: PDF Filename
def get_pdf_filename(default_name="simulation_report"):
    root = tk.Tk()
    root.withdraw()
    
    # Show a message box to inform the user
    messagebox.showinfo("Information", "Please choose where to save the simulation PDF.")
    
    filename = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=default_name,
        title="Save Simulation PDF"
    )
    root.destroy()
    
    # Check if the user pressed Cancel (filename will be an empty string)
    if not filename:
        return None  # Return None if Cancel was pressed
    
    return filename  # Return the chosen filename
# This function runs the main simulation based on user input for initial probability and wrap mode.
def run_simulation():
    # Get the initial probability from the user
    prob = get_initial_probability_gui()
    wrap = get_wrap_mode_gui()
    # create the initial grid based on the user input
    grid = create_initial_grid(prob)
    pdf_path = get_pdf_filename("simulation_report")
    if pdf_path is None:
        return # User pressed Cancel, exit the function
    simulate_and_save(grid, wrap, pdf_path, include_alive_change=True)
    print(f"\n✅ Saved full simulation report to '{pdf_path}'")
     # Show messagebox on top
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Make it topmost
    messagebox.showinfo("Done", "Simulation completed successfully.", parent=root)
    root.destroy()

# this function runs the glider grids simulation
def run_gliders_simulation():
    # Get the wrap mode from the user
    wrap = get_wrap_mode_gui()
    # create both beginning grids for the glider simulation
    grids = create_glider_grid()
    #  get the spisific grid that matches the wrap mode (0 for regular, 1 for wraparound)
    grid = grids[wrap]
    pdf_path = get_pdf_filename("gliders_report")
    if pdf_path is None:
        return # User pressed Cancel, exit the function

    simulate_and_save(grid, wrap, pdf_path, include_alive_change=False)
    print(f"\n✅ Saved gliders report to '{pdf_path}'")
     # Show messagebox on top
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Make it topmost
    messagebox.showinfo("Done", "Simulation completed successfully.", parent=root)
    root.destroy()
# this function runs the interesting patterns simulation
def run_interesting_patterns():
    # for this question we used wraparound mode only
    wrap = 1
     # get the begining grids for the interesting patterns
    patterns = create_interesting_patterns()
    #get what pattern the user wants to see
    pattern = get_interesting_pattern_gui()
    grid = patterns[pattern]
    pdf_path = get_pdf_filename(f"interesting_pattern_{pattern + 1}")
    if pdf_path is None:
        return # User pressed Cancel, exit the function

    simulate_and_save(grid, wrap, pdf_path, include_alive_change=False)
    print(f"\n✅ Saved interesting pattern to '{pdf_path}'")
     # Show messagebox on top
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    root.attributes("-topmost", True)  # Make it topmost
    messagebox.showinfo("Done", "Simulation completed successfully.", parent=root)
    root.destroy()


def gui_main_menu():
    # Create the main window
    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", lambda: on_exit())
    window.title("Computational Biology Ex.1")
    window.geometry("420x350")
    window.configure(bg="#e6f2ff")
    window.resizable(False, False)

    tk.Label(window, text="Computational Biology Ex.1", font=("Helvetica", 18, "bold"), bg="#e6f2ff").pack(pady=25)

    # Button functions
    def on_run_simulation():
        window.withdraw()
        run_simulation()
        window.deiconify()

    def on_run_gliders():
        window.withdraw()
        run_gliders_simulation()
        window.deiconify()

    def on_run_patterns():
        window.withdraw()
        run_interesting_patterns()
        window.deiconify()

    def on_exit():
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            window.destroy()
        sys.exit(0)

    button_style = {"font": ("Helvetica", 11), "width": 30, "bg": "#4CAF50", "fg": "white"}

    tk.Button(window, text="1. Run simulation", command=on_run_simulation, **button_style).pack(pady=7)
    tk.Button(window, text="2. Run gliders simulation", command=on_run_gliders, **button_style).pack(pady=7)
    tk.Button(window, text="3. Run interesting patterns", command=on_run_patterns, **button_style).pack(pady=7)
    tk.Button(window, text="4. Exit", command=on_exit, bg="#f44336", fg="white", font=("Helvetica", 11), width=30).pack(pady=20)


    # Run the GUI loop
    window.mainloop()
if __name__ == "__main__":
    gui_main_menu()