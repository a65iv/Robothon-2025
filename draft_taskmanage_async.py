import tkinter as tk
from tkinter import ttk, messagebox

class RobotSequenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Function Sequence Manager")
        self.root.geometry("1200x800")
        
        # Define all functions with their properties
        self.functions = {
            'captureBoard': {"name": "captureBoard", "color": "#E8E8E8", "type": "auto"},
            'setLocal': {"name": "setLocal", "color": "#E8E8E8", "type": "auto"},
            'penPick': {"name": "penPick", "color": "#E8E8E8", "type": "auto"},
            'armReady': {"name": "armReady", "color": "#E8E8E8", "type": "auto"},
            'penPlace': {"name": "penPlace", "color": "#E8E8E8", "type": "auto"},
            'magnetReady': {"name": "magnetReady", "color": "#E8E8E8", "type": "auto"},
            'stylusReady': {"name": "stylusReady", "color": "#E8E8E8", "type": "auto"},
            'do_pressRBR': {"name": "do_pressRBR", "color": "#FFB366", "type": "user"},
            'do_Maze1': {"name": "do_Maze1", "color": "#FFB366", "type": "user"},
            'do_Maze2': {"name": "do_Maze2", "color": "#FFB366", "type": "user"},
            'do_drawScreen': {"name": "do_drawScreen", "color": "#FFB366", "type": "user"},
            'End': {"name": "End", "color": "#D3D3D3", "type": "auto"}
        }
        
        # Available user functions (can be selected multiple times)
        self.available_functions = ['do_pressRBR', 'do_Maze1', 'do_Maze2', 'do_drawScreen']
        # User's selected sequence (default order)
        self.user_sequence = ['do_pressRBR', 'do_drawScreen', 'do_Maze1', 'do_Maze2']
        
        # Complete execution sequence (will be calculated)
        self.full_sequence = []
        
        # Track current executing function for visual progress
        self.current_executing_index = -1
        
        # Drag and drop variables
        self.drag_data = {"item": None, "start_index": None}
        
        self.setup_ui()
        self.calculate_full_sequence()
        self.update_display()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Robothon Task Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Function selection section
        selection_frame = ttk.LabelFrame(main_frame, text="Select Functions to Include", padding="10")
        selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Available functions layout
        funcs_container = ttk.Frame(selection_frame)
        funcs_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Available functions with add buttons
        funcs_frame = ttk.Frame(funcs_container)
        funcs_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(funcs_frame, text="Available Functions:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=4, pady=(0, 10), sticky=tk.W)
        
        for i, func_name in enumerate(self.available_functions):
            col = i
            # Function button with color (acts as both display and add button)
            func_button = tk.Button(funcs_frame, text=f"{func_name}\n(Click to Add)", 
                                   bg=self.functions[func_name]["color"], 
                                   command=lambda fn=func_name: self.add_function(fn),
                                   font=("Arial", 9, "bold"), width=14, height=3)
            func_button.grid(row=1, column=col, padx=5, pady=5)
        
        # Control buttons on the right side
        controls_right = ttk.Frame(funcs_container)
        controls_right.grid(row=0, column=1, padx=(20, 0), sticky=(tk.N, tk.E))
        
        ttk.Label(controls_right, text="Sequence Controls:", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=(0, 10))
        ttk.Button(controls_right, text="Clear All", 
                  command=self.clear_sequence).grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(controls_right, text="Reset to Default", 
                  command=self.reset_sequence).grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        funcs_container.columnconfigure(0, weight=1)
        
        # User function reordering section
        user_frame = ttk.LabelFrame(main_frame, text="Selected Functions (Drag to Rearrange, Right-click to Remove)", padding="10")
        user_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Canvas for user functions
        self.user_canvas = tk.Canvas(user_frame, height=80, bg="white")
        self.user_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Bind canvas events for drag and drop
        self.user_canvas.bind("<Button-1>", self.on_click)
        self.user_canvas.bind("<B1-Motion>", self.on_drag)
        self.user_canvas.bind("<ButtonRelease-1>", self.on_release)
        self.user_canvas.bind("<Button-3>", self.on_right_click)  # Right-click to remove
        
        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Button(controls_frame, text="Validate Sequence", 
                  command=self.validate_sequence).grid(row=0, column=0, padx=(0, 10))
        
        # PREVIEW Button
        preview_button = ttk.Button(controls_frame, text="📋 PREVIEW Sequence", 
                                   command=self.preview_sequence)
        preview_button.grid(row=0, column=1, padx=(0, 10))
        
        # GO Button (prominent)
        go_button = ttk.Button(controls_frame, text="🚀 GO - Start Execution", 
                              command=self.start_execution)
        go_button.grid(row=0, column=2, padx=(20, 0))
        
        # Full sequence display
        sequence_frame = ttk.LabelFrame(main_frame, text="Complete Execution Sequence Preview", padding="10")
        sequence_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Canvas for full sequence with scrolling
        canvas_frame = ttk.Frame(sequence_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.sequence_canvas = tk.Canvas(canvas_frame, height=150, bg="#f8f8f8")
        self.sequence_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.sequence_canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.sequence_canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Output panel - simple text area for execution status
        output_frame = ttk.LabelFrame(main_frame, text="Execution Status", padding="10")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.output_text = tk.Text(output_frame, height=8, width=80, font=("Arial", 10), wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        output_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        output_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        user_frame.columnconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        sequence_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
    
    def calculate_full_sequence(self):
        """Calculate the complete execution sequence based on state diagram rules"""
        self.full_sequence = []
        current_state = None
        
        # Always start with captureBoard and setLocal
        self.full_sequence.extend(['captureBoard', 'setLocal'])
        current_state = 'setLocal'
        
        # Process each user function in the specified order
        for user_func in self.user_sequence:
            # Determine the required start/end state for this function
            if user_func == 'do_pressRBR':
                required_state = 'armReady'
            elif user_func in ['do_Maze1', 'do_Maze2']:
                required_state = 'magnetReady'
            elif user_func == 'do_drawScreen':
                required_state = 'stylusReady'
            
            # Navigate to the required state
            path_to_state = self.find_path_to_state(current_state, required_state)
            self.full_sequence.extend(path_to_state)
            current_state = required_state
            
            # Execute the user function
            self.full_sequence.append(user_func)
            # Return to the same state (begin and end with same state)
            self.full_sequence.append(required_state)
        
        # Navigate to armReady for the end (if not already there)
        if current_state != 'armReady':
            path_to_armready = self.find_path_to_state(current_state, 'armReady')
            self.full_sequence.extend(path_to_armready)
        
        # Add End
        self.full_sequence.append('End')
    
    def find_path_to_state(self, from_state, to_state):
        """Find the path from current state to target state following the state diagram"""
        if from_state == to_state:
            return []
        
        # Define state transitions based on the diagram
        transitions = {
            'setLocal': ['armReady'],
            'armReady': ['do_pressRBR', 'penPick'],  # do_pressRBR is handled separately
            'penPick': ['stylusReady'],
            'stylusReady': ['magnetReady'],
            'magnetReady': ['stylusReady'],
            'penPlace': ['armReady']
        }
        
        # Handle special transitions and paths
        if from_state == 'setLocal' and to_state == 'armReady':
            return ['armReady']
        elif from_state == 'setLocal' and to_state == 'magnetReady':
            return ['armReady', 'penPick', 'stylusReady', 'magnetReady']
        elif from_state == 'setLocal' and to_state == 'stylusReady':
            return ['armReady', 'penPick', 'stylusReady']
        elif from_state == 'armReady' and to_state == 'magnetReady':
            return ['penPick', 'stylusReady', 'magnetReady']
        elif from_state == 'armReady' and to_state == 'stylusReady':
            return ['penPick', 'stylusReady']
        elif from_state == 'magnetReady' and to_state == 'armReady':
            return ['penPlace', 'armReady']
        elif from_state == 'magnetReady' and to_state == 'stylusReady':
            return ['stylusReady']
        elif from_state == 'stylusReady' and to_state == 'armReady':
            return ['penPlace', 'armReady']
        elif from_state == 'stylusReady' and to_state == 'magnetReady':
            return ['magnetReady']
        
        return []  # Already at target or no path needed
    
    def update_display(self):
        """Update both canvases"""
        # Reset execution progress when updating display
        self.current_executing_index = -1
        self.update_user_canvas()
        self.update_sequence_canvas()
        self.update_output()
    
    def update_user_canvas(self):
        """Update the user-controllable functions canvas"""
        self.user_canvas.delete("all")
        
        box_width = 130
        box_height = 50
        spacing = 15
        start_x = 10
        y = 15
        
        self.user_boxes = {}
        
        for i, func_name in enumerate(self.user_sequence):
            x = start_x + i * (box_width + spacing)
            func_info = self.functions[func_name]
            
            # Draw box with shadow effect
            shadow_offset = 3
            self.user_canvas.create_rectangle(
                x + shadow_offset, y + shadow_offset, 
                x + box_width + shadow_offset, y + box_height + shadow_offset,
                fill="gray", outline="", width=0
            )
            
            # Draw main box
            box_id = self.user_canvas.create_rectangle(
                x, y, x + box_width, y + box_height,
                fill=func_info["color"], outline="black", width=2,
                tags=f"user_{func_name}"
            )
            
            # Draw text
            text_id = self.user_canvas.create_text(
                x + box_width/2, y + box_height/2,
                text=func_name, font=("Arial", 10, "bold"),
                tags=f"user_{func_name}"
            )
            
            # Add position number and count if duplicate
            func_count = self.user_sequence[:i+1].count(func_name)
            total_count = self.user_sequence.count(func_name)
            
            position_text = str(i+1)
            if total_count > 1:
                position_text += f" ({func_count}/{total_count})"
            
            self.user_canvas.create_text(
                x + 10, y + 10,
                text=position_text, font=("Arial", 8), fill="red"
            )
            
            self.user_boxes[func_name] = {
                "box": box_id, "text": text_id, "x": x, "y": y,
                "width": box_width, "height": box_height, "index": i
            }
    
    def update_sequence_canvas(self):
        """Update the complete sequence canvas"""
        self.sequence_canvas.delete("all")
        
        box_width = 90
        box_height = 35
        spacing = 5
        start_x = 10
        y = 20
        row_height = 50
        
        # Calculate layout - multiple rows if needed
        max_per_row = 10
        total_width = max(len(self.full_sequence), max_per_row) * (box_width + spacing) + 100
        total_height = ((len(self.full_sequence) // max_per_row) + 1) * row_height + 50
        
        self.sequence_canvas.configure(scrollregion=(0, 0, total_width, total_height))
        
        for i, func_name in enumerate(self.full_sequence):
            row = i // max_per_row
            col = i % max_per_row
            x = start_x + col * (box_width + spacing)
            y_pos = y + row * row_height
            
            func_info = self.functions[func_name]
            
            # Determine box outline based on execution status
            outline_color = "black"
            outline_width = 1
            
            if i == self.current_executing_index:
                outline_color = "red"
                outline_width = 3
            
            # Draw box
            self.sequence_canvas.create_rectangle(
                x, y_pos, x + box_width, y_pos + box_height,
                fill=func_info["color"], outline=outline_color, width=outline_width
            )
            
            # Draw text
            self.sequence_canvas.create_text(
                x + box_width/2, y_pos + box_height/2,
                text=func_name, font=("Arial", 8),
                width=box_width-4
            )
            
            # Draw step number
            self.sequence_canvas.create_text(
                x + box_width/2, y_pos + box_height + 8,
                text=f"{i+1}", font=("Arial", 7),
                fill="blue"
            )
            
            # Draw arrow to next function (if not last and in same row)
            if i < len(self.full_sequence) - 1 and col < max_per_row - 1:
                arrow_start_x = x + box_width
                arrow_end_x = x + box_width + spacing
                arrow_y = y_pos + box_height/2
                self.sequence_canvas.create_line(
                    arrow_start_x, arrow_y, arrow_end_x, arrow_y,
                    arrow=tk.LAST, fill="blue", width=1
                )
    
    def on_click(self, event):
        """Handle mouse click for drag start"""
        item = self.user_canvas.find_closest(event.x, event.y)[0]
        tags = self.user_canvas.gettags(item)
        
        if tags and tags[0].startswith("user_"):
            func_name = tags[0].split("_", 1)[1]
            self.drag_data["item"] = func_name
            self.drag_data["start_index"] = self.user_sequence.index(func_name)
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.drag_data["item"] is None:
            return
        
        func_name = self.drag_data["item"]
        if func_name in self.user_boxes:
            box_info = self.user_boxes[func_name]
            dx = event.x - (box_info["x"] + box_info["width"]/2)
            self.user_canvas.move(f"user_{func_name}", dx, 0)
            self.user_boxes[func_name]["x"] = event.x - box_info["width"]/2
    
    def on_release(self, event):
        """Handle mouse release for drop"""
        if self.drag_data["item"] is None:
            return
        
        func_name = self.drag_data["item"]
        new_index = self.calculate_drop_position(event.x)
        
        if new_index != self.drag_data["start_index"]:
            # Reorder the user sequence
            self.user_sequence.remove(func_name)
            self.user_sequence.insert(new_index, func_name)
            
            # Recalculate full sequence
            self.calculate_full_sequence()
        
        # Reset drag data and refresh display
        self.drag_data = {"item": None, "start_index": None}
        self.update_display()
    
    def calculate_drop_position(self, x):
        """Calculate new index based on drop x-coordinate"""
        box_width = 130
        spacing = 15
        start_x = 10
        
        for i in range(len(self.user_sequence)):
            box_center = start_x + i * (box_width + spacing) + box_width/2
            if x < box_center:
                return i
        return len(self.user_sequence) - 1
    
    def add_function(self, func_name):
        """Add a function to the user sequence"""
        self.user_sequence.append(func_name)
        self.calculate_full_sequence()
        self.update_display()
    
    def clear_sequence(self):
        """Clear all functions from sequence"""
        result = messagebox.askyesno("Clear Sequence", "Remove all functions from the sequence?")
        if result:
            self.user_sequence = []
            self.calculate_full_sequence()
            self.update_display()
    
    def on_right_click(self, event):
        """Handle right-click to remove function"""
        item = self.user_canvas.find_closest(event.x, event.y)[0]
        tags = self.user_canvas.gettags(item)
        
        if tags and tags[0].startswith("user_"):
            func_name = tags[0].split("_", 1)[1]
            # Find which instance of the function was clicked
            clicked_index = None
            
            for i, box_func in enumerate(self.user_sequence):
                if box_func == func_name and func_name in self.user_boxes:
                    box_info = self.user_boxes[func_name]
                    if (event.x >= box_info["x"] and event.x <= box_info["x"] + box_info["width"] and
                        i == self.user_sequence.index(func_name, clicked_index + 1 if clicked_index is not None else 0)):
                        clicked_index = i
                        break
            
            if clicked_index is not None:
                # Remove the specific instance
                self.user_sequence.pop(clicked_index)
                self.calculate_full_sequence()
                self.update_display()
    
    def reset_sequence(self):
        """Reset user functions to default order"""
        self.user_sequence = ['do_pressRBR', 'do_drawScreen', 'do_Maze1', 'do_Maze2']
        self.calculate_full_sequence()
        self.update_display()
        messagebox.showinfo("Reset", "Function sequence reset to default order:\ndo_pressRBR → do_drawScreen → do_Maze1 → do_Maze2")
    
    def validate_sequence(self):
        """Validate that at least one function is selected"""
        if not self.user_sequence:
            messagebox.showerror("Validation Error", "At least one function must be selected!")
            return False
        
        messagebox.showinfo("Validation", f"✓ Sequence is valid!\n{len(self.user_sequence)} function(s) selected")
        return True
    
    def preview_sequence(self):
        """Show a detailed preview of the execution sequence"""
        if not self.validate_sequence():
            return
            
        preview_text = f"SEQUENCE PREVIEW\n{'='*30}\n\n"
        
        # Show function selection summary
        func_counts = {}
        for func in self.user_sequence:
            func_counts[func] = func_counts.get(func, 0) + 1
        
        preview_text += "Selected Functions:\n"
        for func, count in func_counts.items():
            preview_text += f"  • {func}: {count} time(s)\n"
        
        preview_text += f"\nUser Order: {' → '.join(self.user_sequence)}\n\n"
        preview_text += f"Complete Sequence ({len(self.full_sequence)} steps):\n"
        
        for i, func in enumerate(self.full_sequence, 1):
            func_type = "🎯" if self.functions[func]['type'] == 'user' else "🔧"
            preview_text += f"  {i:2d}. {func_type} {func}\n"
        
        preview_text += f"\n{'='*30}\n"
        preview_text += "🔧 = Auto Function, 🎯 = User Function\n"
        preview_text += "\nClick GO to start execution!"
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, preview_text)
    
    def start_execution(self):
        """Start execution and show status"""
        if not self.validate_sequence():
            return
            
        self.show_execution_status()
    
    def generate_execution_code(self):
        """Generate Python code for the current sequence"""
        code = f"""# Robot Function Execution Sequence
# Generated for user order: {' → '.join(self.user_sequence)}
# Total sequence length: {len(self.full_sequence)} functions

import time
import logging

class RobotController:
    def __init__(self):
        self.current_state = None
        self.executed_functions = []
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
    def log(self, message):
        self.logger.info(message)
        print(f"[{{time.strftime('%H:%M:%S')}}] {{message}}")
    
    def update_state(self, new_state):
        if new_state != self.current_state:
            self.log(f"State transition: {{self.current_state}} → {{new_state}}")
            self.current_state = new_state
    
"""
        
        # Generate individual function definitions
        for func_name in set(self.full_sequence):
            if func_name == 'End':
                code += f"    def {func_name.lower()}(self):\n"
                code += f"        \"\"\"Complete the robot sequence\"\"\"\n"
                code += f"        self.log('🏁 Robot sequence completed successfully!')\n"
                code += f"        self.update_state('End')\n"
                code += f"        self.executed_functions.append('{func_name}')\n\n"
            else:
                code += f"    def {func_name}(self):\n"
                code += f"        \"\"\"Execute {func_name}\"\"\"\n"
                code += f"        self.log('🔧 Executing {func_name}...')\n"
                code += f"        \n"
                code += f"        # TODO: Implement actual {func_name} logic here\n"
                code += f"        time.sleep(0.2)  # Simulate execution time\n"
                code += f"        \n"
                if func_name in ['armReady', 'magnetReady', 'stylusReady']:
                    code += f"        self.update_state('{func_name}')\n"
                code += f"        self.executed_functions.append('{func_name}')\n"
                code += f"        self.log('✅ {func_name} completed')\n\n"
        
        # Generate execution sequence
        code += "    def execute_sequence(self):\n"
        code += "        \"\"\"Execute all functions in the specified order\"\"\"\n"
        code += "        self.log('🚀 Starting robot execution sequence...')\n"
        code += "        self.log(f'Sequence: {\", \".join([\"" + "\", \"".join(self.full_sequence) + "\"])}')\n"
        code += "        \n"
        code += "        try:\n"
        
        for i, func_name in enumerate(self.full_sequence, 1):
            if func_name == 'End':
                code += f"            # Step {i}: Complete sequence\n"
                code += f"            self.end()\n"
            else:
                code += f"            # Step {i}: {func_name}\n"
                code += f"            self.{func_name}()\n"
            code += f"            \n"
        
        code += "            return True\n"
        code += "            \n"
        code += "        except Exception as e:\n"
        code += "            self.log(f'❌ Execution failed at step: {e}')\n"
        code += "            return False\n\n"
        
        code += f"""    def get_execution_summary(self):
        \"\"\"Get a summary of the execution\"\"\"
        return {{
            'user_function_order': {self.user_sequence},
            'total_steps': {len(self.full_sequence)},
            'sequence': {self.full_sequence},
            'executed_count': len(self.executed_functions)
        }}

# Usage example
if __name__ == "__main__":
    robot = RobotController()
    
    print("Robot Function Sequence Manager")
    print("="*50)
    print(f"User-defined order: {' → '.join(self.user_sequence)}")
    print(f"Total sequence steps: {len(self.full_sequence)}")
    print()
    
    success = robot.execute_sequence()
    
    if success:
        print("\\n🎉 Robot sequence completed successfully!")
        summary = robot.get_execution_summary()
        print(f"Executed {{summary['executed_count']}}/{{summary['total_steps']}} functions")
    else:
        print("\\n❌ Robot sequence failed!")
"""
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, code)
    
    def update_output(self):
        """Update the output display with simple execution status"""
        if not hasattr(self, 'output_text'):
            return
            
        if self.user_sequence:
            output = "Current Execution Order:\n"
            for i, func in enumerate(self.user_sequence, 1):
                output += f"{i}. {func}\n"
            
            output += f"\nSequence Valid: ✓ Yes\n"
            output += f"Total Functions: {len(self.full_sequence)}\n\n"
            output += "Ready to execute. Click GO to start.\n"
        else:
            output = "⚠️ No functions selected!\n\n"
            output += "Please add at least one function to the sequence.\n"
            output += "Click the colored function buttons above to add them.\n"
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, output)
    
    def show_execution_status(self):
        """Show execution progress in the output panel"""
        if not self.user_sequence:
            return
            
        # Start execution in a separate thread to avoid blocking UI
        import threading
        import asyncio
        
        def run_async_execution():
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.execute_sequence())
            finally:
                loop.close()
        
        threading.Thread(target=run_async_execution, daemon=True).start()
    
    async def execute_sequence(self):
        """Execute the complete sequence with real-time updates (async version)"""
        import asyncio
        
        # Initial status
        self.update_execution_display("🚀 EXECUTION STARTED", 0, "Initializing...")
        await asyncio.sleep(0.5)
        
        try:
            for i, func_name in enumerate(self.full_sequence, 1):
                # Update display to show current function executing
                self.update_execution_display("EXECUTING", i, f"Executing {func_name}...")
                
                # Call the actual async function based on name
                success = await self.call_robot_function_async(func_name)
                
                if not success:
                    self.update_execution_display("❌ EXECUTION FAILED", i, f"Failed at {func_name}")
                    return
                
                # Small delay to show progress (remove in production)
                await asyncio.sleep(0.3)
            
            # Execution completed successfully
            self.update_execution_display("✅ EXECUTION COMPLETED", len(self.full_sequence), "All functions executed successfully!")
            
        except Exception as e:
            self.update_execution_display("❌ EXECUTION ERROR", i if 'i' in locals() else 0, f"Error: {str(e)}")
    
    async def call_robot_function_async(self, func_name):
        """
        Call the actual async robot function - REPLACE WITH YOUR ASYNC ROBOT CONTROL CODE
        
        This is where you put your actual async robot function calls.
        Return True if successful, False if failed.
        """
        
        # =================================================================
        # PLACEHOLDER: Replace these with your actual ASYNC robot function calls
        # =================================================================
        
        if func_name == 'captureBoard':
            # TODO: Add your async captureBoard implementation here
            # Example: await robot.capture_board()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'setLocal':
            # TODO: Add your async setLocal implementation here
            # Example: await robot.set_local()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'penPick':
            # TODO: Add your async penPick implementation here
            # Example: await robot.pen_pick()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'armReady':
            # TODO: Add your async armReady implementation here
            # Example: await robot.arm_ready()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'penPlace':
            # TODO: Add your async penPlace implementation here
            # Example: await robot.pen_place()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'magnetReady':
            # TODO: Add your async magnetReady implementation here
            # Example: await robot.magnet_ready()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'stylusReady':
            # TODO: Add your async stylusReady implementation here
            # Example: await robot.stylus_ready()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'do_pressRBR':
            # TODO: Add your async do_pressRBR implementation here
            # Example: await robot.press_rbr()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'do_Maze1':
            # TODO: Add your async do_Maze1 implementation here
            # Example: await robot.solve_maze1()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'do_Maze2':
            # TODO: Add your async do_Maze2 implementation here
            # Example: await robot.solve_maze2()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'do_drawScreen':
            # TODO: Add your async do_drawScreen implementation here
            # Example: await robot.draw_screen()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        elif func_name == 'End':
            # TODO: Add your async End/cleanup implementation here
            # Example: await robot.finish_sequence()
            print(f"PLACEHOLDER: Calling async {func_name}")
            await asyncio.sleep(0.1)  # Simulate async operation
            return True
            
        else:
            print(f"WARNING: Unknown function {func_name}")
            return False
        
        # =================================================================
        # END PLACEHOLDER SECTION
        # =================================================================

def main():
    root = tk.Tk()
    app = RobotSequenceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
