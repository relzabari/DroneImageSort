import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import logging
import os
import sys
import string
import ctypes

from app_logging import log_sort_summary, setup_logging
from sorting_engine import sort_drone_images


def get_common_folders():
    """Return existing, commonly used folders without querying Windows Explorer."""
    home = os.path.expanduser("~")
    cloud_home = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")

    def first_existing(*paths):
        return next((path for path in paths if path and os.path.isdir(path)), None)

    candidates = [
        ("Home", home),
        ("Desktop", first_existing(os.path.join(home, "Desktop"),
                                   os.path.join(cloud_home, "Desktop") if cloud_home else None)),
        ("Documents", first_existing(os.path.join(home, "Documents"),
                                     os.path.join(cloud_home, "Documents") if cloud_home else None)),
        ("Downloads", os.path.join(home, "Downloads")),
        ("Pictures", first_existing(os.path.join(home, "Pictures"),
                                    os.path.join(cloud_home, "Pictures") if cloud_home else None)),
        ("Videos", first_existing(os.path.join(home, "Videos"),
                                  os.path.join(cloud_home, "Videos") if cloud_home else None)),
    ]
    return [(name, path) for name, path in candidates if path and os.path.isdir(path)]


class FolderPicker(tk.Toplevel):
    """A Tk-only folder picker that does not invoke the Windows shell dialog."""

    def __init__(self, parent, title, initial_dir=None):
        super().__init__(parent)
        self.result = None
        self.current_dir = None
        self.title(title)
        self.geometry("700x520")
        self.minsize(520, 360)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        path_frame = tk.Frame(self, padx=10, pady=10)
        path_frame.pack(fill=tk.X)

        tk.Label(path_frame, text="Folder path:").pack(anchor=tk.W)
        entry_row = tk.Frame(path_frame)
        entry_row.pack(fill=tk.X, pady=(4, 0))
        self.path_entry = tk.Entry(entry_row)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_entry.bind("<Return>", self.go_to_entered_path)
        tk.Button(entry_row, text="Go", width=8,
                  command=self.go_to_entered_path).pack(side=tk.LEFT, padx=(8, 0))

        toolbar = tk.Frame(self, padx=10)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="Up", width=10,
                  command=self.go_up).pack(side=tk.LEFT)
        tk.Button(toolbar, text="Drives", width=10,
                  command=self.show_drives).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text="Home", width=10,
                  command=lambda: self.load_directory(os.path.expanduser("~"))).pack(side=tk.LEFT)

        browser_frame = tk.Frame(self, padx=10, pady=10)
        browser_frame.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(browser_frame, bg="#ecf0f1", padx=8, pady=8, width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        tk.Label(
            sidebar, text="Quick access", font=("Segoe UI", 10, "bold"),
            bg="#ecf0f1", fg="#34495e", anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 8))

        for name, path in get_common_folders():
            tk.Button(
                sidebar, text=name, anchor=tk.W, relief=tk.FLAT,
                bg="#ecf0f1", activebackground="#d6eaf8",
                command=lambda folder=path: self.load_directory(folder)
            ).pack(fill=tk.X, pady=1)

        tk.Frame(sidebar, height=1, bg="#bdc3c7").pack(fill=tk.X, pady=8)
        tk.Button(
            sidebar, text="Drives", anchor=tk.W, relief=tk.FLAT,
            bg="#ecf0f1", activebackground="#d6eaf8",
            command=self.show_drives
        ).pack(fill=tk.X, pady=1)

        list_frame = tk.Frame(browser_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_list = tk.Listbox(
            list_frame, font=("Segoe UI", 11), activestyle="dotbox",
            yscrollcommand=scrollbar.set
        )
        self.folder_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.folder_list.yview)
        self.folder_list.bind("<Double-Button-1>", self.open_selected)
        self.folder_list.bind("<Return>", self.open_selected)

        self.status_label = tk.Label(self, text="", anchor=tk.W, fg="#c0392b", padx=10)
        self.status_label.pack(fill=tk.X)

        buttons = tk.Frame(self, padx=10, pady=10)
        buttons.pack(fill=tk.X)
        tk.Button(buttons, text="Cancel", width=12,
                  command=self.cancel).pack(side=tk.RIGHT)
        tk.Button(buttons, text="Select This Folder", width=18,
                  bg="#27ae60", fg="white", command=self.select_current).pack(side=tk.RIGHT, padx=8)

        start_dir = initial_dir if initial_dir and os.path.isdir(initial_dir) else os.path.expanduser("~")
        self.load_directory(start_dir)
        self.grab_set()
        self.path_entry.focus_set()

    def load_directory(self, path):
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(path.strip())))
        if not os.path.isdir(path):
            self.status_label.config(text="Folder does not exist or is not accessible.")
            return

        try:
            with os.scandir(path) as entries:
                folders = sorted(
                    (entry.name for entry in entries if entry.is_dir(follow_symlinks=False)),
                    key=str.casefold
                )
        except OSError as error:
            self.status_label.config(text=f"Cannot open folder: {error}")
            return

        self.current_dir = path
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)
        self.folder_list.delete(0, tk.END)
        for folder in folders:
            self.folder_list.insert(tk.END, folder)
        self.status_label.config(text=f"{len(folders)} folders")

    def show_drives(self):
        self.current_dir = None
        self.path_entry.delete(0, tk.END)
        self.folder_list.delete(0, tk.END)
        if os.name == "nt":
            drive_mask = ctypes.windll.kernel32.GetLogicalDrives()
            drives = [f"{letter}:\\" for index, letter in enumerate(string.ascii_uppercase)
                      if drive_mask & (1 << index)]
        else:
            drives = [os.path.sep]
        for drive in drives:
            self.folder_list.insert(tk.END, drive)
        self.status_label.config(text=f"{len(drives)} drives")

    def go_to_entered_path(self, event=None):
        self.load_directory(self.path_entry.get())

    def go_up(self):
        if not self.current_dir:
            return
        parent = os.path.dirname(self.current_dir)
        if parent == self.current_dir:
            self.show_drives()
        else:
            self.load_directory(parent)

    def open_selected(self, event=None):
        selection = self.folder_list.curselection()
        if not selection:
            return
        name = self.folder_list.get(selection[0])
        path = name if self.current_dir is None else os.path.join(self.current_dir, name)
        self.load_directory(path)

    def select_current(self):
        if self.current_dir and os.path.isdir(self.current_dir):
            self.result = self.current_dir
            self.destroy()
        else:
            self.status_label.config(text="Open a drive or folder before selecting it.")

    def cancel(self):
        self.result = None
        self.destroy()


def choose_folder(parent, title, initial_dir=None):
    picker = FolderPicker(parent, title, initial_dir)
    parent.wait_window(picker)
    return picker.result

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
        self.sorting_thread = None
        self.is_running = True
        
        # Setup proper cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create UI
        self.create_home_screen()
    
    def on_closing(self):
        """Handle window closing gracefully"""
        self.is_running = False
        
        # Wait for sorting thread to finish (with timeout)
        if self.sorting_thread and self.sorting_thread.is_alive():
            self.sorting_thread.join(timeout=5)
        
        # Close logger handlers
        if self.logger:
            for handler in self.logger.handlers[:]:
                try:
                    handler.close()
                    self.logger.removeHandler(handler)
                except:
                    pass
        
        # Destroy the window
        self.root.destroy()
        
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
        title_label.pack(fill=tk.X)
        
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
        
        # Manual entry option
        manual_frame = tk.Frame(content_frame, bg="#f0f0f0")
        manual_frame.pack(fill=tk.X, pady=10)
        
        manual_label = tk.Label(
            manual_frame,
            text="Or paste a folder path:",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        manual_label.pack(anchor=tk.W)
        
        hint_label = tk.Label(
            manual_frame,
            text="Example: C:\\Users\\user\\Downloads",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        hint_label.pack(anchor=tk.W)

        self.source_path_entry = tk.Entry(
            manual_frame,
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50"
        )
        self.source_path_entry.pack(fill=tk.X, pady=5)
        # Set initial value if path was already selected
        if self.source_path:
            self.source_path_entry.insert(0, self.source_path)
        self.source_path_entry.bind("<KeyRelease>", self._on_source_entry_change)
        
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
        """Open folder selection dialog with error handling"""
        try:
            folder = choose_folder(
                self.root,
                "Select source folder with drone images",
                self.source_path or os.path.expanduser("~")
            )
            if folder:
                self.source_path = folder
                self.source_label.config(
                    text=f"Selected: {self.source_path}",
                    fg="#27ae60"
                )
                self.source_path_entry.delete(0, tk.END)
                self.source_path_entry.insert(0, folder)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening folder dialog: {e}")
            
    def show_dest_selection(self):
        """Show destination folder selection screen"""
        if not self.source_path:
            messagebox.showwarning("No Selection", "Please enter a source folder path first!")
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
        title_label.pack(fill=tk.X)
        
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
        
        # Manual entry option
        manual_frame = tk.Frame(content_frame, bg="#f0f0f0")
        manual_frame.pack(fill=tk.X, pady=10)
        
        manual_label = tk.Label(
            manual_frame,
            text="Or paste a folder path (optional):",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        manual_label.pack(anchor=tk.W)
        
        hint_label = tk.Label(
            manual_frame,
            text="Leave empty to sort in source folder | Example: C:\\Users\\user\\SortedPhotos",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        hint_label.pack(anchor=tk.W)

        self.dest_path_entry = tk.Entry(
            manual_frame,
            font=("Arial", 10),
            bg="white",
            fg="#2c3e50"
        )
        self.dest_path_entry.pack(fill=tk.X, pady=5)
        # Set initial value if path was already selected
        if self.dest_path:
            self.dest_path_entry.insert(0, self.dest_path)
        self.dest_path_entry.bind("<KeyRelease>", self._on_dest_entry_change)
        
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
        """Open destination folder selection dialog with error handling"""
        try:
            folder = choose_folder(
                self.root,
                "Select destination folder (leave empty to use source folder)",
                self.dest_path or self.source_path or os.path.expanduser("~")
            )
            if folder:
                self.dest_path = folder
                self.dest_label.config(
                    text=f"Selected: {self.dest_path}",
                    fg="#27ae60"
                )
                self.dest_path_entry.delete(0, tk.END)
                self.dest_path_entry.insert(0, folder)
        except Exception as e:
            messagebox.showerror("Error", f"Error opening folder dialog: {e}")
    
    def _on_source_entry_change(self, event=None):
        """Handle manual source path entry"""
        path = self.source_path_entry.get().strip()
        if path and os.path.isdir(path):
            self.source_path = path
            self.source_label.config(
                text=f"Selected: {self.source_path}",
                fg="#27ae60"
            )
    
    def _on_dest_entry_change(self, event=None):
        """Handle manual destination path entry"""
        path = self.dest_path_entry.get().strip()
        if path and os.path.isdir(path):
            self.dest_path = path
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
        title_label.pack(fill=tk.X)
        
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
        self.sorting_thread = threading.Thread(
            target=self.run_sorting,
            daemon=True
        )
        self.sorting_thread.start()
        
    def run_sorting(self):
        """Run sorting in background thread"""
        try:
            # Check if we should still run
            if not self.is_running:
                return
            
            # Redirect logging to GUI
            self.setup_gui_logging_handler()
            
            # Run the UI-independent engine and forward progress to logging.
            result = sort_drone_images(
                self.source_path,
                self.dest_path,
                progress=lambda level, message: getattr(self.logger, level)(message),
            )
            log_sort_summary(self.logger, result)
            
            # Check again before updating GUI
            if not self.is_running:
                return
            
            if result.success:
                self.log_to_gui("✓ Sorting completed successfully!", "INFO")
            else:
                self.log_to_gui("✗ Sorting encountered errors!", "ERROR")
                
            # Add completion button
            if self.is_running:
                self.root.after(500, self.show_completion_buttons)
            
        except Exception as e:
            if self.is_running:
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
        """Add message to GUI output text area (thread-safe)"""
        self.root.after(0, self._update_output_text, message, level)
    
    def _update_output_text(self, message, level):
        """Actually update the output text (called on main thread)"""
        if hasattr(self, 'output_text') and self.output_text.winfo_exists():
            self.output_text.insert(tk.END, f"{message}\n", level)
            self.output_text.see(tk.END)
        
    def show_completion_buttons(self):
        """Show completion buttons"""
        # Check if window still exists
        if not self.is_running or not self.root.winfo_exists():
            return
        
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
    try:
        root = tk.Tk()
        app = DroneImageSortGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error in GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
