import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import logging
from datetime import datetime
import os
import sys

# Import the sorting function
from sort_images import sort_drone_images, setup_logging

class DroneImageSortGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Image Sort - GUI")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Store selected paths
        self.source_path = None
        self.dest_path = None
        self.logger = None
        self.log_file = None
        
        # Create UI
        self.create_home_screen()
        
    def create_home_screen(self):
        """Create the welcome/home screen"""
        self.clear_window()
        
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=200)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(
            title_frame,
            text="🚁 Drone Image Sort 🚁",
            font=("Arial", 32, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=40
        )
        title_label.pack()
        
        welcome_label = tk.Label(
            title_frame,
            text="Welcome! Let's organize your drone photos",
            font=("Arial", 14),
            bg="#2c3e50",
            fg="#3498db",
            pady=10
        )
        welcome_label.pack()
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=80, fill=tk.BOTH, expand=True)
        
        # Start button
        start_button = tk.Button(
            button_frame,
            text="Start Sorting",
            font=("Arial", 16, "bold"),
            bg="#27ae60",
            fg="white",
            padx=40,
            pady=15,
            command=self.show_source_selection,
            cursor="hand2"
        )
        start_button.pack(pady=20)
        
        # Info label
        info_label = tk.Label(
            button_frame,
            text="Select a folder to start sorting your drone images\ninto Thermal, Visual, Wide, and Other categories.",
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#34495e",
            justify=tk.CENTER
        )
        info_label.pack(pady=20)
        
    def show_source_selection(self):
        """Show source folder selection screen"""
        self.clear_window()
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Select Source Folder",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=20
        )
        title_label.pack(fill=tk.X, bg="#2c3e50")
        
        # Content frame
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = tk.Label(
            content_frame,
            text="Choose the folder containing your drone images",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#34495e"
        )
        instructions.pack(pady=20)
        
        # Selected path label
        self.source_label = tk.Label(
            content_frame,
            text="No folder selected",
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#e74c3c",
            padx=10,
            pady=10,
            wraplength=800,
            justify=tk.LEFT
        )
        self.source_label.pack(fill=tk.X, pady=10)
        
        # Browse button
        browse_button = tk.Button(
            content_frame,
            text="Browse...",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=10,
            command=self.select_source_folder,
            cursor="hand2"
        )
        browse_button.pack(pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(content_frame, bg="#f0f0f0")
        nav_frame.pack(fill=tk.X, pady=20)
        
        back_button = tk.Button(
            nav_frame,
            text="Back",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.create_home_screen,
            cursor="hand2"
        )
        back_button.pack(side=tk.LEFT, padx=5)
        
        next_button = tk.Button(
            nav_frame,
            text="Next",
            font=("Arial", 11),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.show_dest_selection,
            cursor="hand2"
        )
        next_button.pack(side=tk.RIGHT, padx=5)
        
    def select_source_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select source folder with drone images")
        if folder:
            self.source_path = folder
            self.source_label.config(
                text=f"Selected: {self.source_path}",
                fg="#27ae60"
            )
            
    def show_dest_selection(self):
        """Show destination folder selection screen"""
        if not self.source_path:
            messagebox.showwarning("No Selection", "Please select a source folder first!")
            return
            
        self.clear_window()
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Select Destination Folder (Optional)",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=20
        )
        title_label.pack(fill=tk.X, bg="#2c3e50")
        
        # Content frame
        content_frame = tk.Frame(self.root, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = tk.Label(
            content_frame,
            text="Choose destination folder (optional)\nIf not selected, images will be sorted in the same folder as source",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#34495e",
            justify=tk.CENTER
        )
        instructions.pack(pady=20)
        
        # Selected path label
        self.dest_label = tk.Label(
            content_frame,
            text="No folder selected (will use source folder)",
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#f39c12",
            padx=10,
            pady=10,
            wraplength=800,
            justify=tk.LEFT
        )
        self.dest_label.pack(fill=tk.X, pady=10)
        
        # Browse button
        browse_button = tk.Button(
            content_frame,
            text="Browse...",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            padx=30,
            pady=10,
            command=self.select_dest_folder,
            cursor="hand2"
        )
        browse_button.pack(pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(content_frame, bg="#f0f0f0")
        nav_frame.pack(fill=tk.X, pady=20)
        
        back_button = tk.Button(
            nav_frame,
            text="Back",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=self.show_source_selection,
            cursor="hand2"
        )
        back_button.pack(side=tk.LEFT, padx=5)
        
        start_button = tk.Button(
            nav_frame,
            text="Start Sorting",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.start_sorting,
            cursor="hand2"
        )
        start_button.pack(side=tk.RIGHT, padx=5)
        
    def select_dest_folder(self):
        """Open destination folder selection dialog"""
        folder = filedialog.askdirectory(title="Select destination folder (leave empty to use source folder)")
        if folder:
            self.dest_path = folder
            self.dest_label.config(
                text=f"Selected: {self.dest_path}",
                fg="#27ae60"
            )
            
    def start_sorting(self):
        """Start the sorting process"""
        # Use destination path if selected, otherwise use source
        working_path = self.dest_path if self.dest_path else self.source_path
        
        # Setup logging
        self.logger, self.log_file = setup_logging(working_path)
        
        self.clear_window()
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Sorting in Progress...",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=20
        )
        title_label.pack(fill=tk.X, bg="#2c3e50")
        
        # Progress info
        info_frame = tk.Frame(self.root, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        source_info = tk.Label(
            info_frame,
            text=f"Source: {self.source_path}",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        source_info.pack(anchor=tk.W)
        
        dest_info = tk.Label(
            info_frame,
            text=f"Destination: {working_path}",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        dest_info.pack(anchor=tk.W)
        
        # Output text area
        output_frame = tk.Frame(self.root, bg="#f0f0f0")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        output_label = tk.Label(
            output_frame,
            text="Output Log:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#34495e"
        )
        output_label.pack(anchor=tk.W, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=("Courier", 10),
            bg="#2c3e50",
            fg="#ecf0f1",
            padx=10,
            pady=10,
            wrap=tk.WORD,
            height=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colors
        self.output_text.tag_config("INFO", foreground="#3498db")
        self.output_text.tag_config("DEBUG", foreground="#95a5a6")
        self.output_text.tag_config("WARNING", foreground="#f39c12")
        self.output_text.tag_config("ERROR", foreground="#e74c3c")
        
        # Start sorting in separate thread
        sort_thread = threading.Thread(
            target=self.run_sorting,
            args=(working_path,),
            daemon=True
        )
        sort_thread.start()
        
    def run_sorting(self, working_path):
        """Run sorting in background thread"""
        try:
            # Redirect logging to GUI
            self.setup_gui_logging_handler()
            
            # Run sorting
            success = sort_drone_images(self.source_path, self.logger)
            
            if success:
                self.log_to_gui("✓ Sorting completed successfully!", "INFO")
            else:
                self.log_to_gui("✗ Sorting encountered errors!", "ERROR")
                
            # Add completion button
            self.root.after(500, self.show_completion_buttons)
            
        except Exception as e:
            self.log_to_gui(f"✗ Fatal error: {e}", "ERROR")
            self.root.after(500, self.show_completion_buttons)
            
    def setup_gui_logging_handler(self):
        """Add a handler to log to GUI"""
        class GUIHandler(logging.Handler):
            def __init__(self, gui_instance):
                super().__init__()
                self.gui = gui_instance
                
            def emit(self, record):
                message = self.format(record)
                level = record.levelname
                self.gui.log_to_gui(message, level)
        
        gui_handler = GUIHandler(self)
        gui_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.logger.addHandler(gui_handler)
        
    def log_to_gui(self, message, level="INFO"):
        """Add message to GUI output text area"""
        self.output_text.insert(tk.END, f"{message}\n", level)
        self.output_text.see(tk.END)
        self.root.update()
        
    def show_completion_buttons(self):
        """Show completion buttons"""
        # Find and create button frame if it doesn't exist
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # View log button
        view_log_button = tk.Button(
            button_frame,
            text="View Full Log",
            font=("Arial", 11),
            bg="#9b59b6",
            fg="white",
            padx=20,
            pady=8,
            command=self.view_log_file,
            cursor="hand2"
        )
        view_log_button.pack(side=tk.LEFT, padx=5)
        
        # Restart button
        restart_button = tk.Button(
            button_frame,
            text="Sort Another Folder",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=self.reset_to_home,
            cursor="hand2"
        )
        restart_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            command=self.root.quit,
            cursor="hand2"
        )
        exit_button.pack(side=tk.RIGHT, padx=5)
        
    def view_log_file(self):
        """Open the log file in default application"""
        if self.log_file and os.path.exists(self.log_file):
            os.startfile(self.log_file)
        else:
            messagebox.showerror("Error", "Log file not found!")
            
    def reset_to_home(self):
        """Reset and go back to home screen"""
        self.source_path = None
        self.dest_path = None
        self.create_home_screen()
        
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    app = DroneImageSortGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
