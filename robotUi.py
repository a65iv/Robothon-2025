import tkinter as tk
from tkinter import ttk, messagebox


class RobotSequenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Function Sequence Manager")
        self.root.geometry("1200x800")

        # Dummy function metadata
        self.functions = {
            'captureBoard': {"name": "captureBoard", "color": "#E8E8E8"},
            'setLocal': {"name": "setLocal", "color": "#E8E8E8"},
            'penPick': {"name": "penPick", "color": "#E8E8E8"},
            'armReady': {"name": "armReady", "color": "#E8E8E8"},
            'penPlace': {"name": "penPlace", "color": "#E8E8E8"},
            'magnetReady': {"name": "magnetReady", "color": "#E8E8E8"},
            'stylusReady': {"name": "stylusReady", "color": "#E8E8E8"},
            'do_pressRBR': {"name": "do_pressRBR", "color": "#FFB366"},
            'do_Maze1': {"name": "do_Maze1", "color": "#FFB366"},
            'do_Maze2': {"name": "do_Maze2", "color": "#FFB366"},
            'do_drawScreen': {"name": "do_drawScreen", "color": "#FFB366"},
            'End': {"name": "End", "color": "#D3D3D3"},
        }

        self.available_functions = ['do_pressRBR', 'do_Maze1', 'do_Maze2', 'do_drawScreen']
        self.user_sequence = []

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Robothon Task Manager", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        # Available Functions
        selection_frame = ttk.LabelFrame(main_frame, text="Select Functions to Include", padding="10")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        funcs_frame = ttk.Frame(selection_frame)
        funcs_frame.grid(row=0, column=0)

        for i, func in enumerate(self.available_functions):
            btn = tk.Button(
                funcs_frame,
                text=func,
                bg=self.functions[func]["color"],
                font=("Arial", 9, "bold"),
                width=14,
                height=3,
                command=lambda f=func: self.add_function(f)
            )
            btn.grid(row=1, column=i, padx=5, pady=5)

        # Selected Functions
        self.user_frame = ttk.LabelFrame(main_frame, text="Selected Sequence", padding="10")
        self.user_frame.grid(row=2, column=0, sticky="nsew")

        self.user_canvas = tk.Canvas(self.user_frame, height=100, bg="white")
        self.user_canvas.pack(fill="x", expand=True)

        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=1, sticky="n")

        tk.Button(control_frame, text="Clear", command=self.clear_sequence).pack(pady=5)
        tk.Button(control_frame, text="Reset", command=self.reset_sequence).pack(pady=5)
        tk.Button(control_frame, text="🚀 GO", bg="#00FF00", font=("Arial", 12, "bold")).pack(pady=10)

    def add_function(self, func_name):
        self.user_sequence.append(func_name)
        self.update_user_canvas()

    def clear_sequence(self):
        self.user_sequence.clear()
        self.update_user_canvas()

    def reset_sequence(self):
        self.user_sequence = ['do_pressRBR', 'do_drawScreen', 'do_Maze1', 'do_Maze2']
        self.update_user_canvas()

    def update_user_canvas(self):
        self.user_canvas.delete("all")
        x, y = 10, 20
        width = 130
        spacing = 15

        for i, func in enumerate(self.user_sequence):
            color = self.functions[func]["color"]
            self.user_canvas.create_rectangle(x, y, x + width, y + 50, fill=color, outline="black")
            self.user_canvas.create_text(x + width / 2, y + 25, text=func, font=("Arial", 10, "bold"))
            x += width + spacing


def main():
    root = tk.Tk()
    app = RobotSequenceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
