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


TRANSLATIONS = {
    "en": {
        "app_title": "Drone Image Sort - GUI", "language": "עברית", "welcome": "Welcome! Let's organize your drone photos",
        "start": "Start Sorting", "home_info": "Select a folder to start sorting your drone images\ninto Thermal, Visual, Wide, and Other categories.",
        "source_title": "Select Source Folder", "source_instruction": "Choose the folder containing your drone images",
        "none": "No folder selected", "browse": "Browse...", "paste": "Or paste a folder path:", "example": "Example: C:\\Users\\user\\Downloads",
        "back": "Back", "next": "Next", "selected": "Selected: {path}", "error": "Error", "picker_error": "Error opening folder dialog: {error}",
        "no_selection": "No Selection", "source_required": "Please enter a source folder path first!",
        "dest_title": "Select Destination Folder (Optional)", "dest_instruction": "Choose destination folder (optional)\nIf not selected, images will be sorted in the same folder as source",
        "dest_none": "No folder selected (will use source folder)", "dest_paste": "Or paste a folder path (optional):",
        "dest_hint": "Leave empty to sort in source folder | Example: C:\\Users\\user\\SortedPhotos",
        "sorting": "Sorting in Progress...", "source": "Source: {path}", "destination": "Destination: {path}", "output": "Output Log:",
        "success": "✓ Sorting completed successfully!", "failed": "✗ Sorting encountered errors!", "fatal": "✗ Fatal error: {error}",
        "view_log": "View Full Log", "restart": "Sort Another Folder", "exit": "Exit", "log_missing": "Log file not found!",
        "picker_source": "Select source folder with drone images", "picker_dest": "Select destination folder (leave empty to use source folder)",
        "folder_path": "Folder path:", "go": "Go", "up": "Up", "drives": "Drives", "home": "Home", "quick": "Quick access",
        "cancel": "Cancel", "select_folder": "Select This Folder", "folder_missing": "Folder does not exist or is not accessible.",
        "cannot_open": "Cannot open folder: {error}", "folder_count": "{count} folders", "drive_count": "{count} drives",
        "open_first": "Open a drive or folder before selecting it.", "Desktop": "Desktop", "Documents": "Documents", "Downloads": "Downloads", "Pictures": "Pictures", "Videos": "Videos",
    },
    "he": {
        "app_title": "מיון תמונות רחפן", "language": "English", "welcome": "ברוכים הבאים! בואו נסדר את תמונות הרחפן",
        "start": "התחלת מיון", "home_info": "בחרו תיקייה כדי למיין את תמונות הרחפן\nלתיקיות תרמי, חזותי, רחב ואחר.",
        "source_title": "בחירת תיקיית מקור", "source_instruction": "בחרו את התיקייה שמכילה את תמונות הרחפן",
        "none": "לא נבחרה תיקייה", "browse": "בחירה...", "paste": "או הדביקו נתיב לתיקייה:", "example": "לדוגמה: C:\\Users\\user\\Downloads",
        "back": "חזרה", "next": "הבא", "selected": "נבחרה: {path}", "error": "שגיאה", "picker_error": "שגיאה בפתיחת חלון בחירת התיקייה: {error}",
        "no_selection": "לא נבחרה תיקייה", "source_required": "יש להזין תחילה נתיב לתיקיית המקור.",
        "dest_title": "בחירת תיקיית יעד (אופציונלי)", "dest_instruction": "בחרו תיקיית יעד (אופציונלי)\nאם לא תיבחר תיקייה, התמונות ימוינו בתוך תיקיית המקור",
        "dest_none": "לא נבחרה תיקייה (ייעשה שימוש בתיקיית המקור)", "dest_paste": "או הדביקו נתיב לתיקיית יעד (אופציונלי):",
        "dest_hint": "השאירו ריק למיון בתיקיית המקור | לדוגמה: C:\\Users\\user\\SortedPhotos",
        "sorting": "המיון מתבצע...", "source": "מקור: {path}", "destination": "יעד: {path}", "output": "יומן פעילות:",
        "success": "✓ המיון הושלם בהצלחה!", "failed": "✗ המיון הסתיים עם שגיאות!", "fatal": "✗ שגיאה חמורה: {error}",
        "view_log": "הצגת היומן המלא", "restart": "מיון תיקייה נוספת", "exit": "יציאה", "log_missing": "קובץ היומן לא נמצא.",
        "picker_source": "בחירת תיקיית מקור עם תמונות רחפן", "picker_dest": "בחירת תיקיית יעד (אפשר להשאיר ריק ולהשתמש במקור)",
        "folder_path": "נתיב התיקייה:", "go": "מעבר", "up": "למעלה", "drives": "כוננים", "home": "בית", "quick": "גישה מהירה",
        "cancel": "ביטול", "select_folder": "בחירת תיקייה זו", "folder_missing": "התיקייה אינה קיימת או שאינה נגישה.",
        "cannot_open": "לא ניתן לפתוח את התיקייה: {error}", "folder_count": "{count} תיקיות", "drive_count": "{count} כוננים",
        "open_first": "יש לפתוח כונן או תיקייה לפני הבחירה.", "Desktop": "שולחן העבודה", "Documents": "מסמכים", "Downloads": "הורדות", "Pictures": "תמונות", "Videos": "סרטונים",
    },
}


def tr(language, key, **values):
    return TRANSLATIONS[language][key].format(**values)


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

    def __init__(self, parent, title, initial_dir=None, language="en"):
        super().__init__(parent)
        self.result = None
        self.current_dir = None
        self.language = language
        self.title(title)
        self.geometry("700x520")
        self.minsize(520, 360)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        path_frame = tk.Frame(self, padx=10, pady=10)
        path_frame.pack(fill=tk.X)

        tk.Label(path_frame, text=tr(language, "folder_path")).pack(anchor=tk.W)
        entry_row = tk.Frame(path_frame)
        entry_row.pack(fill=tk.X, pady=(4, 0))
        self.path_entry = tk.Entry(entry_row)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.path_entry.bind("<Return>", self.go_to_entered_path)
        tk.Button(entry_row, text=tr(language, "go"), width=8,
                  command=self.go_to_entered_path).pack(side=tk.LEFT, padx=(8, 0))

        toolbar = tk.Frame(self, padx=10)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text=tr(language, "up"), width=10,
                  command=self.go_up).pack(side=tk.LEFT)
        tk.Button(toolbar, text=tr(language, "drives"), width=10,
                  command=self.show_drives).pack(side=tk.LEFT, padx=6)
        tk.Button(toolbar, text=tr(language, "home"), width=10,
                  command=lambda: self.load_directory(os.path.expanduser("~"))).pack(side=tk.LEFT)

        browser_frame = tk.Frame(self, padx=10, pady=10)
        browser_frame.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(browser_frame, bg="#ecf0f1", padx=8, pady=8, width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        tk.Label(
            sidebar, text=tr(language, "quick"), font=("Segoe UI", 10, "bold"),
            bg="#ecf0f1", fg="#34495e", anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 8))

        for name, path in get_common_folders():
            tk.Button(
                sidebar, text=tr(language, name), anchor=tk.W, relief=tk.FLAT,
                bg="#ecf0f1", activebackground="#d6eaf8",
                command=lambda folder=path: self.load_directory(folder)
            ).pack(fill=tk.X, pady=1)

        tk.Frame(sidebar, height=1, bg="#bdc3c7").pack(fill=tk.X, pady=8)
        tk.Button(
            sidebar, text=tr(language, "drives"), anchor=tk.W, relief=tk.FLAT,
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
        tk.Button(buttons, text=tr(language, "cancel"), width=12,
                  command=self.cancel).pack(side=tk.RIGHT)
        tk.Button(buttons, text=tr(language, "select_folder"), width=18,
                  bg="#27ae60", fg="white", command=self.select_current).pack(side=tk.RIGHT, padx=8)

        start_dir = initial_dir if initial_dir and os.path.isdir(initial_dir) else os.path.expanduser("~")
        self.load_directory(start_dir)
        self.grab_set()
        self.path_entry.focus_set()

    def load_directory(self, path):
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(path.strip())))
        if not os.path.isdir(path):
            self.status_label.config(text=tr(self.language, "folder_missing"))
            return

        try:
            with os.scandir(path) as entries:
                folders = sorted(
                    (entry.name for entry in entries if entry.is_dir(follow_symlinks=False)),
                    key=str.casefold
                )
        except OSError as error:
            self.status_label.config(text=tr(self.language, "cannot_open", error=error))
            return

        self.current_dir = path
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)
        self.folder_list.delete(0, tk.END)
        for folder in folders:
            self.folder_list.insert(tk.END, folder)
        self.status_label.config(text=tr(self.language, "folder_count", count=len(folders)))

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
        self.status_label.config(text=tr(self.language, "drive_count", count=len(drives)))

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
            self.status_label.config(text=tr(self.language, "open_first"))

    def cancel(self):
        self.result = None
        self.destroy()


def choose_folder(parent, title, initial_dir=None, language="en"):
    picker = FolderPicker(parent, title, initial_dir, language)
    parent.wait_window(picker)
    return picker.result

class DroneImageSortGUI:
    def __init__(self, root):
        self.root = root
        self.language = "en"
        self.current_screen = "home"
        self.root.title(tr(self.language, "app_title"))
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

    def add_language_button(self):
        """Add the language toggle to the current screen."""
        existing = getattr(self, "language_button", None)
        if existing and existing.winfo_exists():
            existing.config(text=tr(self.language, "language"))
            return
        self.language_button = tk.Button(
            self.root, text=tr(self.language, "language"), command=self.toggle_language,
            bg="#f39c12", fg="white", font=("Arial", 10, "bold"), cursor="hand2"
        )
        self.language_button.place(relx=1.0, x=-12, y=12, anchor=tk.NE)

    def toggle_language(self):
        self.language = "he" if self.language == "en" else "en"
        self.root.title(tr(self.language, "app_title"))
        if self.current_screen == "home":
            self.create_home_screen()
        elif self.current_screen == "source":
            self.show_source_selection()
        elif self.current_screen == "destination":
            self.show_dest_selection()
        else:
            self.refresh_sorting_language()

    def refresh_sorting_language(self):
        """Translate the active sorting screen without interrupting its thread."""
        working_path = self.dest_path or self.source_path
        widgets = (
            ("sorting_title_label", "sorting", {}),
            ("source_info_label", "source", {"path": self.source_path}),
            ("dest_info_label", "destination", {"path": working_path}),
            ("output_label", "output", {}),
            ("view_log_button", "view_log", {}),
            ("restart_button", "restart", {}),
            ("exit_button", "exit", {}),
        )
        for attribute, key, values in widgets:
            widget = getattr(self, attribute, None)
            if widget and widget.winfo_exists():
                widget.config(text=tr(self.language, key, **values))
        self.add_language_button()
    
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
        self.current_screen = "home"
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
            text=tr(self.language, "welcome"),
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
            text=tr(self.language, "start"),
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
            text=tr(self.language, "home_info"),
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#34495e",
            justify=tk.CENTER
        )
        info_label.pack(pady=20)
        self.add_language_button()
        
    def show_source_selection(self):
        """Show source folder selection screen"""
        self.current_screen = "source"
        self.clear_window()
        
        # Title
        title_label = tk.Label(
            self.root,
            text=tr(self.language, "source_title"),
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
            text=tr(self.language, "source_instruction"),
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#34495e"
        )
        instructions.pack(pady=20)
        
        # Selected path label
        self.source_label = tk.Label(
            content_frame,
            text=tr(self.language, "selected", path=self.source_path) if self.source_path else tr(self.language, "none"),
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
            text=tr(self.language, "browse"),
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
            text=tr(self.language, "paste"),
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        manual_label.pack(anchor=tk.W)
        
        hint_label = tk.Label(
            manual_frame,
            text=tr(self.language, "example"),
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
            text=tr(self.language, "back"),
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
            text=tr(self.language, "next"),
            font=("Arial", 11),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.show_dest_selection,
            cursor="hand2"
        )
        next_button.pack(side=tk.RIGHT, padx=5)
        self.add_language_button()
        
    def select_source_folder(self):
        """Open folder selection dialog with error handling"""
        try:
            folder = choose_folder(
                self.root,
                tr(self.language, "picker_source"),
                self.source_path or os.path.expanduser("~"),
                self.language,
            )
            if folder:
                self.source_path = folder
                self.source_label.config(
                    text=tr(self.language, "selected", path=self.source_path),
                    fg="#27ae60"
                )
                self.source_path_entry.delete(0, tk.END)
                self.source_path_entry.insert(0, folder)
        except Exception as e:
            messagebox.showerror(tr(self.language, "error"), tr(self.language, "picker_error", error=e))
            
    def show_dest_selection(self):
        """Show destination folder selection screen"""
        if not self.source_path:
            messagebox.showwarning(tr(self.language, "no_selection"), tr(self.language, "source_required"))
            return
            
        self.current_screen = "destination"
        self.clear_window()
        
        # Title
        title_label = tk.Label(
            self.root,
            text=tr(self.language, "dest_title"),
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
            text=tr(self.language, "dest_instruction"),
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#34495e",
            justify=tk.CENTER
        )
        instructions.pack(pady=20)
        
        # Selected path label
        self.dest_label = tk.Label(
            content_frame,
            text=tr(self.language, "selected", path=self.dest_path) if self.dest_path else tr(self.language, "dest_none"),
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
            text=tr(self.language, "browse"),
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
            text=tr(self.language, "dest_paste"),
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        manual_label.pack(anchor=tk.W)
        
        hint_label = tk.Label(
            manual_frame,
            text=tr(self.language, "dest_hint"),
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
            text=tr(self.language, "back"),
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
            text=tr(self.language, "start"),
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=self.start_sorting,
            cursor="hand2"
        )
        start_button.pack(side=tk.RIGHT, padx=5)
        self.add_language_button()
        
    def select_dest_folder(self):
        """Open destination folder selection dialog with error handling"""
        try:
            folder = choose_folder(
                self.root,
                tr(self.language, "picker_dest"),
                self.dest_path or self.source_path or os.path.expanduser("~"),
                self.language,
            )
            if folder:
                self.dest_path = folder
                self.dest_label.config(
                    text=tr(self.language, "selected", path=self.dest_path),
                    fg="#27ae60"
                )
                self.dest_path_entry.delete(0, tk.END)
                self.dest_path_entry.insert(0, folder)
        except Exception as e:
            messagebox.showerror(tr(self.language, "error"), tr(self.language, "picker_error", error=e))
    
    def _on_source_entry_change(self, event=None):
        """Handle manual source path entry"""
        path = self.source_path_entry.get().strip()
        if path and os.path.isdir(path):
            self.source_path = path
            self.source_label.config(
                text=tr(self.language, "selected", path=self.source_path),
                fg="#27ae60"
            )
    
    def _on_dest_entry_change(self, event=None):
        """Handle manual destination path entry"""
        path = self.dest_path_entry.get().strip()
        if path and os.path.isdir(path):
            self.dest_path = path
            self.dest_label.config(
                text=tr(self.language, "selected", path=self.dest_path),
                fg="#27ae60"
            )
            
    def start_sorting(self):
        """Start the sorting process"""
        self.current_screen = "sorting"
        # Use destination path if selected, otherwise use source
        working_path = self.dest_path if self.dest_path else self.source_path
        
        # Setup logging
        self.logger, self.log_file = setup_logging(working_path)
        
        self.clear_window()
        
        # Title
        self.sorting_title_label = tk.Label(
            self.root,
            text=tr(self.language, "sorting"),
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1",
            pady=20
        )
        self.sorting_title_label.pack(fill=tk.X)
        
        # Progress info
        info_frame = tk.Frame(self.root, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.source_info_label = tk.Label(
            info_frame,
            text=tr(self.language, "source", path=self.source_path),
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        self.source_info_label.pack(anchor=tk.W)
        
        self.dest_info_label = tk.Label(
            info_frame,
            text=tr(self.language, "destination", path=working_path),
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#34495e"
        )
        self.dest_info_label.pack(anchor=tk.W)
        
        # Output text area
        output_frame = tk.Frame(self.root, bg="#f0f0f0")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.output_label = tk.Label(
            output_frame,
            text=tr(self.language, "output"),
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#34495e"
        )
        self.output_label.pack(anchor=tk.W, pady=5)
        
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
        self.add_language_button()
        
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
                self.log_to_gui(tr(self.language, "success"), "INFO")
            else:
                self.log_to_gui(tr(self.language, "failed"), "ERROR")
                
            # Add completion button
            if self.is_running:
                self.root.after(500, self.show_completion_buttons)
            
        except Exception as e:
            if self.is_running:
                self.log_to_gui(tr(self.language, "fatal", error=e), "ERROR")
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
        self.view_log_button = tk.Button(
            button_frame,
            text=tr(self.language, "view_log"),
            font=("Arial", 11),
            bg="#9b59b6",
            fg="white",
            padx=20,
            pady=8,
            command=self.view_log_file,
            cursor="hand2"
        )
        self.view_log_button.pack(side=tk.LEFT, padx=5)
        
        # Restart button
        self.restart_button = tk.Button(
            button_frame,
            text=tr(self.language, "restart"),
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=8,
            command=self.reset_to_home,
            cursor="hand2"
        )
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        self.exit_button = tk.Button(
            button_frame,
            text=tr(self.language, "exit"),
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=8,
            command=self.root.quit,
            cursor="hand2"
        )
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
    def view_log_file(self):
        """Open the log file in default application"""
        if self.log_file and os.path.exists(self.log_file):
            os.startfile(self.log_file)
        else:
            messagebox.showerror(tr(self.language, "error"), tr(self.language, "log_missing"))
            
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
