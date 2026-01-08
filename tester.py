import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import sys
import io
import traceback
import os

# Configuration
SAVE_FILE = "my_code_slots.json"
TOTAL_SLOTS = 100

class CodeTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Tester - 100 Slots")
        self.root.geometry("800x700")
        
        # Load data
        self.data = self.load_data()
        self.current_slot = 1
        
        # --- UI Layout ---
        
        # Top Bar: Slot Selection and Run Button
        top_frame = tk.Frame(root, pady=5)
        top_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(top_frame, text="Slot:").pack(side=tk.LEFT)
        
        self.slot_var = tk.StringVar(value="1")
        self.slot_selector = ttk.Spinbox(
            top_frame, 
            from_=1, 
            to=TOTAL_SLOTS, 
            textvariable=self.slot_var, 
            command=self.change_slot,
            width=5
        )
        self.slot_selector.pack(side=tk.LEFT, padx=5)
        # Bind enter key on spinbox to change slot manually
        self.slot_selector.bind('<Return>', lambda e: self.change_slot())
        
        self.run_btn = tk.Button(
            top_frame, 
            text="▶ Run Code", 
            bg="#4CAF50", 
            fg="white", 
            command=self.run_code,
            font=("Arial", 10, "bold")
        )
        self.run_btn.pack(side=tk.RIGHT)

        self.status_lbl = tk.Label(top_frame, text="Saved", fg="grey")
        self.status_lbl.pack(side=tk.RIGHT, padx=10)

        # Code Editor Area
        tk.Label(root, text="Code Editor:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.code_editor = scrolledtext.ScrolledText(
            root, 
            height=20, 
            font=("Consolas", 11), 
            undo=True
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Bind key release to auto-save
        self.code_editor.bind("<KeyRelease>", self.on_key_release)

        # Output Area
        tk.Label(root, text="Output:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        self.output_console = scrolledtext.ScrolledText(
            root, 
            height=10, 
            bg="#f0f0f0", 
            fg="#333", 
            font=("Consolas", 10),
            state='disabled'
        )
        self.output_console.pack(fill=tk.BOTH, padx=10, pady=(0, 10))

        # Load initial slot
        self.load_slot_content(1)

    def load_data(self):
        """Loads the JSON file or creates a new dictionary if missing."""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        """Writes all data to disk."""
        with open(SAVE_FILE, "w") as f:
            json.dump(self.data, f, indent=2)
        self.status_lbl.config(text="Saved", fg="green")

    def on_key_release(self, event):
        """Auto-save logic triggered on typing."""
        code = self.code_editor.get("1.0", tk.END)
        # Store in memory
        self.data[str(self.current_slot)] = code
        # Write to disk
        self.save_data()

    def change_slot(self):
        """Switches the active slot."""
        try:
            new_slot = int(self.slot_var.get())
            if 1 <= new_slot <= TOTAL_SLOTS:
                self.current_slot = new_slot
                self.load_slot_content(new_slot)
        except ValueError:
            pass

    def load_slot_content(self, slot_num):
        """Updates editor with content from the selected slot."""
        content = self.data.get(str(slot_num), "")
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", content)
        self.status_lbl.config(text=f"Loaded Slot {slot_num}", fg="blue")

    def run_code(self):
        """Executes the code and captures stdout/stderr."""
        code = self.code_editor.get("1.0", tk.END)
        
        # Clear previous output
        self.output_console.config(state='normal')
        self.output_console.delete("1.0", tk.END)
        
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            # We create a separate dictionary for the execution namespace 
            # so variables don't persist between runs oddly
            exec_globals = {}
            exec(code, exec_globals)
            output = redirected_output.getvalue()
            self.output_console.insert(tk.END, output)
            self.output_console.config(fg="black")
        except Exception:
            # Get the full traceback if code fails
            error_msg = traceback.format_exc()
            self.output_console.insert(tk.END, error_msg)
            self.output_console.config(fg="red")
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            self.output_console.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeTesterApp(root)
    root.mainloop()
