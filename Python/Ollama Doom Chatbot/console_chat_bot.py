# Import tkinter for GUI creation
import tkinter as tk
# Import scrolledtext widget for chat display
from tkinter import scrolledtext, ttk
# Import requests for making HTTP requests to Ollama API
import requests
# Import subprocess to run the Ollama server
import subprocess
# Import threading for running Ollama queries in a separate thread
import threading
# Import keyboard for detecting keypresses (e.g., ` key to toggle console)
import keyboard
# Import get_monitors to detect screen dimensions and monitor info
from screeninfo import get_monitors
# Import os for file operations (e.g., checking if config file exists)
import os
# Import json for reading/writing configuration to a file
import json
# Import Pillow modules for handling GIF frames with transparency
from PIL import Image, ImageTk

# Define the Ollama API endpoint for sending queries
OLLAMA_API = "http://127.0.0.1:11434/api/generate"

# Define the path to the configuration file
CONFIG_FILE = "F:\\ollama\\config.json"

# Define default themes for the console appearance
THEMES = {
    "default": {
        "bg": "#1e1e1e",           # Background color
        "fg": "#00ff00",           # User message color (green)
        "ollama_fg": "#00b7eb",    # Ollama response color (cyan)
        "input_bg": "#333333",     # Input field background color
        "input_fg": "#ffffff",     # Input field text color (white)
        "alpha": 0.9,              # Window transparency (0.0 to 1.0)
        "border_color": "#555555"  # Border color
    },
    "midnight_blue": {
        "bg": "#0a1a2b",           # Background color
        "fg": "#d0e1f9",           # User message color (light blue)
        "ollama_fg": "#ffcc66",    # Ollama response color (yellow)
        "input_bg": "#1e2a44",     # Input field background color
        "input_fg": "#ffffff",     # Input field text color (white)
        "alpha": 0.9,              # Window transparency
        "border_color": "#2a3a54"  # Border color
    },
    "slate_gray": {
        "bg": "#2b2e3b",           # Background color
        "fg": "#b0b3c1",           # User message color (light gray)
        "ollama_fg": "#8aebff",    # Ollama response color (light blue)
        "input_bg": "#3e424f",     # Input field background color
        "input_fg": "#e0e2ea",     # Input field text color (light gray)
        "alpha": 0.9,              # Window transparency
        "border_color": "#4e525f"  # Border color
    },
    "forest_shadow": {
        "bg": "#1a2b1e",           # Background color
        "fg": "#a0c5a0",           # User message color (pale green)
        "ollama_fg": "#7ba87b",    # Ollama response color (darker green)
        "input_bg": "#2a3b2e",     # Input field background color
        "input_fg": "#d0e0d0",     # Input field text color (light green)
        "alpha": 0.9,              # Window transparency
        "border_color": "#3a4b3e"  # Border color
    }
}

# Define default configuration settings
CONFIG = {
    "monitor": 0,                  # Monitor index to display the console on
    "slide_from": "top",           # Direction from which the console slides in
    "width": 800,                  # Console window width
    "height": 300,                 # Console window height
    "theme": "default",            # Default theme name
    "animation_speed": 10,         # Speed of the slide-in/out animation
    "font": "Courier",             # Font for chat and input
    "font_size": 12,               # Font size for input field
    "chat_font_size": 12,          # Font size for chat area
    "chatbot_name": "Ollama",      # Name of the chatbot
    "animation_alpha": 0.9,        # Transparency for animation window
    "animation_width": 270,        # Width of the animation window
    "animation_height": 480,       # Height of the animation window
    "animation_bg": "#1e1e1e",     # Background color for animation window (or "transparent")
    "animation_enabled": True,     # Enable or disable the animation canvas
    "gif_path": "F:\\ollama\\dancing_robot.gif"  # Path to the GIF file
}

# Function to load configuration from file
def load_config():
    global THEMES, CONFIG  # Access global THEMES and CONFIG dictionaries
    if os.path.exists(CONFIG_FILE):  # Check if config file exists
        with open(CONFIG_FILE, "r") as f:  # Open the file in read mode
            saved_config = json.load(f)  # Load the JSON data
            CONFIG.update(saved_config.get("config", {}))  # Update CONFIG with saved config
            saved_themes = saved_config.get("themes", {})  # Get saved themes
            for theme_name, theme in saved_themes.items():  # Loop through saved themes
                if "ollama_fg" not in theme:  # Ensure ollama_fg is present in each theme
                    theme["ollama_fg"] = THEMES.get(theme_name, THEMES["default"])["ollama_fg"]
            THEMES.update(saved_themes)  # Update THEMES with saved themes

# Function to save configuration to file
def save_config():
    config_to_save = {  # Create a dictionary to save
        "config": {
            "monitor": CONFIG["monitor"],  # Save monitor index
            "slide_from": CONFIG["slide_from"],  # Save slide direction
            "width": CONFIG["width"],  # Save window width
            "height": CONFIG["height"],  # Save window height
            "theme": CONFIG["theme"],  # Save current theme
            "animation_speed": CONFIG["animation_speed"],  # Save animation speed
            "font": CONFIG["font"],  # Save font type
            "font_size": CONFIG["font_size"],  # Save input font size
            "chat_font_size": CONFIG["chat_font_size"],  # Save chat font size
            "chatbot_name": CONFIG["chatbot_name"],  # Save chatbot name
            "animation_alpha": CONFIG["animation_alpha"],  # Save animation transparency
            "animation_width": CONFIG["animation_width"],  # Save animation width
            "animation_height": CONFIG["animation_height"],  # Save animation height
            "animation_bg": CONFIG["animation_bg"],  # Save animation background
            "animation_enabled": CONFIG["animation_enabled"],  # Save animation enabled state
            "gif_path": CONFIG["gif_path"]  # Save GIF path
        },
        "themes": {name: theme for name, theme in THEMES.items()}  # Save all themes
    }
    with open(CONFIG_FILE, "w") as f:  # Open the file in write mode
        json.dump(config_to_save, f, indent=4)  # Save the config as JSON with indentation

# Load configuration when the script starts
load_config()

# Define the main console class
class OllamaConsole:
    def __init__(self):
        # Start the Ollama server if it's not already running
        self.start_ollama_server()

        # Get monitor information for positioning the console
        self.monitors = get_monitors()
        self.monitor = self.monitors[CONFIG["monitor"]]
        self.screen_width = self.monitor.width  # Screen width
        self.screen_height = self.monitor.height  # Screen height
        self.x_offset = self.monitor.x  # X offset of the monitor
        self.y_offset = self.monitor.y  # Y offset of the monitor

        # Set up the main window
        self.root = tk.Tk()  # Create the main Tkinter window
        self.root.overrideredirect(True)  # Remove window decorations (title bar, borders)

        # Set the current theme from CONFIG
        self.current_theme = CONFIG["theme"]
        self.apply_theme()  # Apply the theme to the window

        # Create a separate window for the animated GIF (dancing robot)
        self.animation_window = tk.Toplevel(self.root)  # Create a top-level window
        self.animation_window.overrideredirect(True)  # Remove window decorations
        self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])  # Set transparency
        # Set initial background for the animation window
        if CONFIG["animation_bg"].lower() == "transparent":
            self.animation_window.configure(bg="black")  # Use black as a placeholder for transparency
            self.animation_window.wm_attributes("-transparentcolor", "black")  # Make black transparent
        else:
            self.animation_window.configure(bg=CONFIG["animation_bg"])  # Use configured background
        self.animation_window.withdraw()  # Hide the window initially

        # Create a canvas for the animated GIF in the separate window
        self.animation_canvas = tk.Canvas(
            self.animation_window,
            width=CONFIG["animation_width"],  # Set canvas width
            height=CONFIG["animation_height"],  # Set canvas height
            bg="black" if CONFIG["animation_bg"].lower() == "transparent" else CONFIG["animation_bg"],  # Set background
            highlightthickness=0  # Remove canvas border
        )
        self.animation_canvas.pack()  # Add the canvas to the window

        # Load and prepare the GIF for animation
        self.gif_path = CONFIG["gif_path"]  # Get the GIF path from CONFIG
        self.gif_frames = []  # List to store GIF frames
        self.current_frame = 0  # Track the current frame
        self.load_gif()  # Load the GIF
        self.animation_running = False  # Flag to track if animation is running

        # Set the initial geometry of the animation window
        self.animation_window.geometry(f"{CONFIG['animation_width']}x{CONFIG['animation_height']}+0+0")

        # Set initial position of the main window (off-screen)
        self.width = CONFIG["width"]  # Set window width
        self.height = CONFIG["height"]  # Set window height
        self.slide_from = CONFIG["slide_from"]  # Set slide direction
        self.set_initial_position()  # Position the window

        # Create the chat display area
        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            bg=THEMES[self.current_theme]["bg"],  # Set background color
            fg=THEMES[self.current_theme]["fg"],  # Set text color
            height=10,  # Set height in lines
            width=80,  # Set width in characters
            wrap=tk.WORD,  # Wrap text at word boundaries
            state="disabled",  # Disable direct editing
            font=(CONFIG["font"], CONFIG["chat_font_size"])  # Set font and size
        )
        self.chat_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)  # Add to window with padding

        # Configure tags for colorizing messages in the chat area
        self.chat_area.tag_configure("user", foreground=THEMES[self.current_theme]["fg"])  # User message color
        self.chat_area.tag_configure("ollama", foreground=THEMES[self.current_theme]["ollama_fg"])  # Ollama message color
        self.chat_area.tag_configure("system", foreground="#aaaaaa")  # System message color (gray)

        # Create the input field for user messages
        self.input_field = tk.Entry(
            self.root,
            bg=THEMES[self.current_theme]["input_bg"],  # Set background color
            fg=THEMES[self.current_theme]["input_fg"],  # Set text color
            insertbackground=THEMES[self.current_theme]["fg"],  # Set cursor color
            width=80,  # Set width in characters
            font=(CONFIG["font"], CONFIG["font_size"])  # Set font and size
        )
        self.input_field.pack(padx=5, pady=5, fill=tk.X)  # Add to window with padding
        self.input_field.bind("<Return>", self.send_message)  # Bind Enter key to send message
        self.input_field.bind("<Control-r>", self.restart_console)  # Bind Ctrl+R to restart console

        # Initialize state variables
        self.is_visible = False  # Track if the console is visible
        self.is_animating = False  # Track if animation is in progress
        self.first_open = True  # Track if this is the first time the console is opened
        self.config_window = None  # Reference to the config window (if open)

        # Start with the main window hidden
        self.root.withdraw()

        # Set up a key listener for the ` key to toggle the console
        keyboard.on_press_key("`", self.toggle_console)

        # Start the Tkinter main loop
        self.root.mainloop()

    # Method to load the GIF frames using Pillow
    def load_gif(self):
        try:
            # Open the GIF file with Pillow
            gif = Image.open(self.gif_path)
            self.gif_frames = []  # Clear any existing frames
            frame_count = 0  # Initialize frame counter

            # Iterate through each frame of the GIF
            while True:
                try:
                    # Seek to the current frame
                    gif.seek(frame_count)
                    # Convert the frame to RGBA to handle transparency
                    frame = gif.convert("RGBA")
                    # Create a PhotoImage from the frame
                    photo = ImageTk.PhotoImage(frame)
                    self.gif_frames.append(photo)  # Add the frame to the list
                    frame_count += 1  # Increment frame counter
                except EOFError:
                    break  # Exit loop when there are no more frames

            # Display the first frame, centered in the canvas
            center_x = CONFIG["animation_width"] // 2  # Calculate center X
            center_y = CONFIG["animation_height"] // 2  # Calculate center Y
            self.animation_canvas.create_image(center_x, center_y, image=self.gif_frames[0], anchor="center")
        except Exception as e:
            # Handle errors during GIF loading
            print(f"Error loading GIF: {str(e)}")
            self.chat_area.config(state="normal")  # Enable chat area for writing
            self.chat_area.insert(tk.END, f"Error loading animation: {str(e)}\n\n", "system")  # Display error
            self.chat_area.config(state="disabled")  # Disable chat area
            self.chat_area.see(tk.END)  # Scroll to the end

    # Method to animate the GIF by cycling through frames
    def animate_gif(self):
        if self.animation_running and self.gif_frames:  # Check if animation is running and frames exist
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)  # Cycle to next frame
            self.animation_canvas.delete("all")  # Clear previous frame
            center_x = CONFIG["animation_width"] // 2  # Calculate center X
            center_y = CONFIG["animation_height"] // 2  # Calculate center Y
            self.animation_canvas.create_image(center_x, center_y, image=self.gif_frames[self.current_frame], anchor="center")
            self.root.after(100, self.animate_gif)  # Schedule the next frame after 100ms

    # Method to start the GIF animation
    def start_animation(self):
        if not CONFIG["animation_enabled"]:  # Check if animation is enabled
            self.animation_window.withdraw()  # Ensure the window is hidden if disabled
            self.animation_running = False  # Clear the running flag
            return
        if not self.animation_running and self.is_visible:  # Check if animation is not running and console is visible
            self.animation_running = True  # Set animation running flag
            self.animation_window.deiconify()  # Show the animation window
            self.update_animation_position()  # Position the window
            self.animate_gif()  # Start the animation

    # Method to stop the GIF animation
    def stop_animation(self):
        self.animation_running = False  # Clear animation running flag
        self.animation_window.withdraw()  # Hide the animation window

    # Method to update the position of the animation window relative to the console
    def update_animation_position(self):
        # Get the current position of the console window
        console_x, console_y = self.root.winfo_x(), self.root.winfo_y()
        console_width = self.width  # Get console width
        animation_x = console_x + console_width + 10  # Position 10 pixels to the right
        animation_y = console_y  # Align vertically with the console
        # Set the geometry of the animation window
        self.animation_window.geometry(f"{CONFIG['animation_width']}x{CONFIG['animation_height']}+{animation_x}+{animation_y}")

    # Method to apply the current theme to the UI
    def apply_theme(self):
        theme = THEMES[self.current_theme]  # Get the current theme
        self.root.attributes("-alpha", theme["alpha"])  # Set main window transparency
        self.root.configure(bg=theme["bg"], highlightbackground=theme["border_color"], highlightthickness=2)  # Set background and border
        if hasattr(self, "chat_area"):  # Check if chat_area exists
            self.chat_area.configure(bg=theme["bg"], fg=theme["fg"])  # Update chat area colors
            self.chat_area.tag_configure("user", foreground=theme["fg"])  # Update user message color
            self.chat_area.tag_configure("ollama", foreground=theme["ollama_fg"])  # Update Ollama message color
        if hasattr(self, "animation_window"):  # Check if animation_window exists
            self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])  # Set animation window transparency
            if CONFIG["animation_bg"].lower() == "transparent":  # Check if background is transparent
                self.animation_window.configure(bg="black")  # Set placeholder color
                self.animation_window.wm_attributes("-transparentcolor", "black")  # Make black transparent
            else:
                self.animation_window.configure(bg=CONFIG["animation_bg"])  # Use configured background
        if hasattr(self, "animation_canvas"):  # Check if animation_canvas exists
            if CONFIG["animation_bg"].lower() == "transparent":  # Check if background is transparent
                self.animation_canvas.configure(bg="black")  # Set placeholder color
            else:
                self.animation_canvas.configure(bg=CONFIG["animation_bg"])  # Use configured background
        if hasattr(self, "input_field"):  # Check if input_field exists
            self.input_field.configure(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["fg"])  # Update input field colors

    # Method to start the Ollama server if it's not running
    def start_ollama_server(self):
        try:
            requests.get("http://127.0.0.1:11434")  # Check if Ollama server is running
        except requests.ConnectionError:
            # Start the Ollama server in the background
            subprocess.Popen(
                ["F:\\ollama\\ollama.exe", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW  # Run without creating a console window
            )
            import time
            time.sleep(5)  # Wait 5 seconds to ensure the server starts

    # Method to set the initial off-screen position of the console window
    def set_initial_position(self):
        if self.slide_from == "top":  # Slide from the top
            self.hidden_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset - self.height)
            self.visible_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset)
        elif self.slide_from == "bottom":  # Slide from the bottom
            self.hidden_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset + self.screen_height)
            self.visible_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset + self.screen_height - self.height)
        elif self.slide_from == "left":  # Slide from the left
            self.hidden_pos = (self.x_offset - self.width, self.y_offset + (self.screen_height - self.height) // 2)
            self.visible_pos = (self.x_offset, self.y_offset + (self.screen_height - self.height) // 2)
        elif self.slide_from == "right":  # Slide from the right
            self.hidden_pos = (self.x_offset + self.screen_width, self.y_offset + (self.screen_height - self.height) // 2)
            self.visible_pos = (self.x_offset + self.screen_width - self.width, self.y_offset + (self.screen_height - self.height) // 2)
        # Set the initial geometry of the main window (hidden position)
        self.root.geometry(f"{self.width}x{self.height}+{self.hidden_pos[0]}+{self.hidden_pos[1]}")
        self.update_animation_position()  # Update the animation window position

    # Method to display the help menu in the chat area
    def display_help(self):
        help_text = (
            "=== Chatbot Console Commands ===\n"
            "/help - Show this help menu\n"
            "/restart - Clear the chat and restart the console\n"
            "/theme <name> - Switch themes (available: default, midnight_blue, slate_gray, forest_shadow)\n"
            "/save_theme <name> - Save current theme settings as a new theme\n"
            "/config - Open configuration window\n"
            "Ctrl+R - Restart the console\n"
            "~ - Toggle the console\n"
            "===============================\n"
        )
        self.chat_area.config(state="normal")  # Enable chat area for writing
        self.chat_area.insert(tk.END, help_text + "\n", "system")  # Insert help text
        self.chat_area.config(state="disabled")  # Disable chat area
        self.chat_area.see(tk.END)  # Scroll to the end

    # Method to open the configuration window
    def open_config_window(self):
        if self.config_window is not None and self.config_window.winfo_exists():  # Check if config window is already open
            self.config_window.lift()  # Bring it to the front
            return

        self.config_window = tk.Toplevel(self.root)  # Create a new top-level window
        self.config_window.title("Console Configuration")  # Set the window title
        self.config_window.geometry("450x850")  # Set window size (increased for new fields)
        self.config_window.configure(bg="#2e2e2e")  # Set background color
        self.config_window.resizable(False, False)  # Disable resizing

        # Create a main frame for the config window
        main_frame = tk.Frame(self.config_window, bg="#2e2e2e")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Add frame with padding

        # Section: Chatbot Settings
        tk.Label(main_frame, text="Chatbot Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")
        tk.Label(main_frame, text="Chatbot Name:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5)
        chatbot_name_var = tk.StringVar(value=CONFIG["chatbot_name"])  # Variable for chatbot name
        chatbot_name_entry = tk.Entry(main_frame, textvariable=chatbot_name_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        chatbot_name_entry.grid(row=1, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Font Settings
        tk.Label(main_frame, text="Font Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky="w")
        tk.Label(main_frame, text="Font Type:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=5)
        font_var = tk.StringVar(value=CONFIG["font"])  # Variable for font type
        font_menu = ttk.OptionMenu(main_frame, font_var, CONFIG["font"], "Courier", "Arial", "Helvetica", "Times")
        font_menu.grid(row=3, column=1, sticky="ew", padx=5)  # Add dropdown menu

        tk.Label(main_frame, text="Chat Font Size:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=5)
        chat_font_size_var = tk.StringVar(value=str(CONFIG["chat_font_size"]))  # Variable for chat font size
        chat_font_size_entry = tk.Entry(main_frame, textvariable=chat_font_size_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        chat_font_size_entry.grid(row=4, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Input Font Size:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=5, column=0, sticky="w", padx=5)
        font_size_var = tk.StringVar(value=str(CONFIG["font_size"]))  # Variable for input font size
        font_size_entry = tk.Entry(main_frame, textvariable=font_size_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        font_size_entry.grid(row=5, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Color Settings
        tk.Label(main_frame, text="Color Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky="w")
        tk.Label(main_frame, text="User Text Color:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=7, column=0, sticky="w", padx=5)
        chat_fg_var = tk.StringVar(value=THEMES[self.current_theme]["fg"])  # Variable for user text color
        chat_fg_entry = tk.Entry(main_frame, textvariable=chat_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        chat_fg_entry.grid(row=7, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Chatbot Text Color:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=8, column=0, sticky="w", padx=5)
        ollama_fg_var = tk.StringVar(value=THEMES[self.current_theme]["ollama_fg"])  # Variable for chatbot text color
        ollama_fg_entry = tk.Entry(main_frame, textvariable=ollama_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        ollama_fg_entry.grid(row=8, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Input Text Color:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=9, column=0, sticky="w", padx=5)
        input_fg_var = tk.StringVar(value=THEMES[self.current_theme]["input_fg"])  # Variable for input text color
        input_fg_entry = tk.Entry(main_frame, textvariable=input_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        input_fg_entry.grid(row=9, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Window Background:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=10, column=0, sticky="w", padx=5)
        bg_var = tk.StringVar(value=THEMES[self.current_theme]["bg"])  # Variable for window background
        bg_entry = tk.Entry(main_frame, textvariable=bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        bg_entry.grid(row=10, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Chat Background:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=11, column=0, sticky="w", padx=5)
        chat_bg_var = tk.StringVar(value=THEMES[self.current_theme]["bg"])  # Variable for chat background
        chat_bg_entry = tk.Entry(main_frame, textvariable=chat_bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        chat_bg_entry.grid(row=11, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Input Background:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=12, column=0, sticky="w", padx=5)
        input_bg_var = tk.StringVar(value=THEMES[self.current_theme]["input_bg"])  # Variable for input background
        input_bg_entry = tk.Entry(main_frame, textvariable=input_bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        input_bg_entry.grid(row=12, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Border Color:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=13, column=0, sticky="w", padx=5)
        border_var = tk.StringVar(value=THEMES[self.current_theme]["border_color"])  # Variable for border color
        border_entry = tk.Entry(main_frame, textvariable=border_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        border_entry.grid(row=13, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Main Window Transparency
        tk.Label(main_frame, text="Main Window Transparency (0.0-1.0):", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=14, column=0, sticky="w", padx=5)
        alpha_var = tk.StringVar(value=str(THEMES[self.current_theme]["alpha"]))  # Variable for main window transparency
        alpha_entry = tk.Entry(main_frame, textvariable=alpha_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        alpha_entry.grid(row=14, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Animation Window Settings
        tk.Label(main_frame, text="Animation Window Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=15, column=0, columnspan=2, pady=(10, 5), sticky="w")
        tk.Label(main_frame, text="Enable Animation:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=16, column=0, sticky="w", padx=5)
        animation_enabled_var = tk.BooleanVar(value=CONFIG["animation_enabled"])  # Variable for animation enabled state
        animation_enabled_check = tk.Checkbutton(main_frame, variable=animation_enabled_var, bg="#2e2e2e", fg="#ffffff", selectcolor="#3e3e3e")
        animation_enabled_check.grid(row=16, column=1, sticky="w", padx=5)  # Add checkbox

        tk.Label(main_frame, text="Animation Transparency (0.0-1.0):", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=17, column=0, sticky="w", padx=5)
        animation_alpha_var = tk.StringVar(value=str(CONFIG["animation_alpha"]))  # Variable for animation transparency
        animation_alpha_entry = tk.Entry(main_frame, textvariable=animation_alpha_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        animation_alpha_entry.grid(row=17, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Animation Width:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=18, column=0, sticky="w", padx=5)
        animation_width_var = tk.StringVar(value=str(CONFIG["animation_width"]))  # Variable for animation width
        animation_width_entry = tk.Entry(main_frame, textvariable=animation_width_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        animation_width_entry.grid(row=18, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Animation Height:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=19, column=0, sticky="w", padx=5)
        animation_height_var = tk.StringVar(value=str(CONFIG["animation_height"]))  # Variable for animation height
        animation_height_entry = tk.Entry(main_frame, textvariable=animation_height_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        animation_height_entry.grid(row=19, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Animation Background (or 'transparent'):", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=20, column=0, sticky="w", padx=5)
        animation_bg_var = tk.StringVar(value=CONFIG["animation_bg"])  # Variable for animation background
        animation_bg_entry = tk.Entry(main_frame, textvariable=animation_bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        animation_bg_entry.grid(row=20, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="GIF Path (must be a transparent .gif):", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=21, column=0, sticky="w", padx=5)
        gif_path_var = tk.StringVar(value=CONFIG["gif_path"])  # Variable for GIF path
        gif_path_entry = tk.Entry(main_frame, textvariable=gif_path_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        gif_path_entry.grid(row=21, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Main Window Size
        tk.Label(main_frame, text="Main Window Size", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=22, column=0, columnspan=2, pady=(10, 5), sticky="w")
        tk.Label(main_frame, text="Width:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=23, column=0, sticky="w", padx=5)
        width_var = tk.StringVar(value=str(CONFIG["width"]))  # Variable for window width
        width_entry = tk.Entry(main_frame, textvariable=width_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        width_entry.grid(row=23, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Height:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=24, column=0, sticky="w", padx=5)
        height_var = tk.StringVar(value=str(CONFIG["height"]))  # Variable for window height
        height_entry = tk.Entry(main_frame, textvariable=height_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        height_entry.grid(row=24, column=1, sticky="ew", padx=5)  # Add entry field

        # Section: Animation & Position
        tk.Label(main_frame, text="Animation & Position", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=25, column=0, columnspan=2, pady=(10, 5), sticky="w")
        tk.Label(main_frame, text="Animation Speed:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=26, column=0, sticky="w", padx=5)
        anim_speed_var = tk.StringVar(value=str(CONFIG["animation_speed"]))  # Variable for animation speed
        anim_speed_entry = tk.Entry(main_frame, textvariable=anim_speed_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")
        anim_speed_entry.grid(row=26, column=1, sticky="ew", padx=5)  # Add entry field

        tk.Label(main_frame, text="Slide From:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=27, column=0, sticky="w", padx=5)
        slide_var = tk.StringVar(value=CONFIG["slide_from"])  # Variable for slide direction
        slide_menu = ttk.OptionMenu(main_frame, slide_var, CONFIG["slide_from"], "top", "bottom", "left", "right")
        slide_menu.grid(row=27, column=1, sticky="ew", padx=5)  # Add dropdown menu

        tk.Label(main_frame, text="Monitor:", bg="#2e2e2e", fg="#cccccc", font=("Arial", 10)).grid(row=28, column=0, sticky="w", padx=5)
        monitor_var = tk.StringVar(value=str(CONFIG["monitor"]))  # Variable for monitor index
        monitor_menu = ttk.OptionMenu(main_frame, monitor_var, str(CONFIG["monitor"]), *[str(i) for i in range(len(self.monitors))])
        monitor_menu.grid(row=28, column=1, sticky="ew", padx=5)  # Add dropdown menu

        # Create a frame for the Apply and Save buttons
        button_frame = tk.Frame(main_frame, bg="#2e2e2e")
        button_frame.grid(row=29, column=0, columnspan=2, pady=10)

        # Function to apply configuration changes
        def apply_config():
            try:
                # Update chatbot name
                CONFIG["chatbot_name"] = chatbot_name_var.get()

                # Update font settings
                CONFIG["font"] = font_var.get()
                CONFIG["font_size"] = int(font_size_var.get())
                CONFIG["chat_font_size"] = int(chat_font_size_var.get())
                self.chat_area.configure(font=(CONFIG["font"], CONFIG["chat_font_size"]))
                self.input_field.configure(font=(CONFIG["font"], CONFIG["font_size"]))

                # Update colors
                THEMES[self.current_theme]["fg"] = chat_fg_var.get()
                THEMES[self.current_theme]["ollama_fg"] = ollama_fg_var.get()
                THEMES[self.current_theme]["input_fg"] = input_fg_var.get()
                THEMES[self.current_theme]["bg"] = bg_var.get()
                THEMES[self.current_theme]["input_bg"] = input_bg_var.get()
                THEMES[self.current_theme]["border_color"] = border_var.get()
                THEMES[self.current_theme]["alpha"] = float(alpha_var.get())

                # Update animation window settings
                CONFIG["animation_enabled"] = animation_enabled_var.get()  # Update animation enabled state
                # Immediately apply the animation enabled/disabled state
                if CONFIG["animation_enabled"]:
                    if self.is_visible:  # If console is visible, show animation
                        self.start_animation()
                else:
                    self.stop_animation()  # Hide animation if disabled
                CONFIG["animation_alpha"] = float(animation_alpha_var.get())
                CONFIG["animation_width"] = int(animation_width_var.get())
                CONFIG["animation_height"] = int(animation_height_var.get())
                CONFIG["animation_bg"] = animation_bg_var.get()

                # Validate and update GIF path
                new_gif_path = gif_path_var.get()
                if not os.path.exists(new_gif_path):  # Check if the file exists
                    raise FileNotFoundError(f"GIF file not found: {new_gif_path}")
                if not new_gif_path.lower().endswith(".gif"):  # Check if it's a GIF file
                    raise ValueError("File must be a .gif")
                CONFIG["gif_path"] = new_gif_path  # Update the GIF path
                self.gif_path = CONFIG["gif_path"]  # Update the instance variable

                # Apply animation window settings
                self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])
                self.animation_canvas.configure(width=CONFIG["animation_width"], height=CONFIG["animation_height"])
                if CONFIG["animation_bg"].lower() == "transparent":
                    self.animation_window.configure(bg="black")
                    self.animation_window.wm_attributes("-transparentcolor", "black")
                    self.animation_canvas.configure(bg="black")
                else:
                    self.animation_window.configure(bg=CONFIG["animation_bg"])
                    self.animation_canvas.configure(bg=CONFIG["animation_bg"])
                self.update_animation_position()  # Update position with new size

                # Reload GIF to adjust for new settings
                self.gif_frames = []
                self.current_frame = 0
                self.load_gif()

                # Update window size
                CONFIG["width"] = int(width_var.get())
                CONFIG["height"] = int(height_var.get())
                self.width = CONFIG["width"]
                self.height = CONFIG["height"]

                # Update animation and position settings
                CONFIG["animation_speed"] = int(anim_speed_var.get())
                CONFIG["slide_from"] = slide_var.get()
                CONFIG["monitor"] = int(monitor_var.get())

                # Apply changes to monitor and position
                self.monitor = self.monitors[CONFIG["monitor"]]
                self.screen_width = self.monitor.width
                self.screen_height = self.monitor.height
                self.x_offset = self.monitor.x
                self.y_offset = self.monitor.y
                self.slide_from = CONFIG["slide_from"]
                self.set_initial_position()
                self.apply_theme()

                # Display success message
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, "Configuration updated.\n\n", "system")
                self.chat_area.config(state="disabled")
                self.chat_area.see(tk.END)
            except Exception as e:
                # Display error message if something goes wrong
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, f"Error applying config: {str(e)}\n\n", "system")
                self.chat_area.config(state="disabled")
                self.chat_area.see(tk.END)

        # Function to apply changes and save them
        def save_and_close():
            apply_config()  # Apply the changes
            save_config()  # Save to file
            self.chat_area.config(state="normal")  # Enable chat area
            self.chat_area.insert(tk.END, "Configuration saved.\n\n", "system")  # Display success message
            self.chat_area.config(state="disabled")  # Disable chat area
            self.chat_area.see(tk.END)  # Scroll to the end
            self.config_window.destroy()  # Close the config window

        # Add Apply and Save buttons
        tk.Button(button_frame, text="Apply", command=apply_config, bg="#4e4e4e", fg="#ffffff", font=("Arial", 10), relief="flat").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save & Close", command=save_and_close, bg="#4e4e4e", fg="#ffffff", font=("Arial", 10), relief="flat").pack(side=tk.LEFT, padx=5)

        # Configure grid weights to make entry fields expandable
        main_frame.columnconfigure(1, weight=1)

    # Method to toggle the console visibility when ` key is pressed
    def toggle_console(self, event):
        if self.is_animating:  # Prevent toggling during animation
            return
        self.is_visible = not self.is_visible  # Toggle visibility state
        if self.is_visible:
            self.root.deiconify()  # Show the main window
            self.start_animation()  # Start the animation
            self.animate_slide_in()  # Slide the console in
        else:
            self.stop_animation()  # Stop the animation
            self.animate_slide_out()  # Slide the console out

    # Method to animate the console sliding in
    def animate_slide_in(self):
        self.is_animating = True  # Set animating flag
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()  # Get current position
        target_x, target_y = self.visible_pos  # Get target position
        step = CONFIG["animation_speed"]  # Get animation step size

        # Continue animating if not at target position
        if abs(current_x - target_x) > step or abs(current_y - target_y) > step:
            if current_x != target_x:  # Move X position
                new_x = current_x + step if current_x < target_x else current_x - step
            else:
                new_x = current_x
            if current_y != target_y:  # Move Y position
                new_y = current_y + step if current_y < target_y else current_y - step
            else:
                new_y = current_y
            self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")  # Update position
            self.update_animation_position()  # Update animation window position
            self.root.after(10, self.animate_slide_in)  # Schedule next frame
        else:
            # Animation complete, set final position
            self.root.geometry(f"{self.width}x{self.height}+{target_x}+{target_y}")
            self.update_animation_position()  # Final position update
            self.is_animating = False  # Clear animating flag
            if self.first_open:  # If first time opening
                self.display_help()  # Show help menu
                self.first_open = False  # Mark as not first open
            self.root.focus_force()  # Focus on the window
            self.root.after(100, self.input_field.focus)  # Focus on input field

    # Method to animate the console sliding out
    def animate_slide_out(self):
        self.is_animating = True  # Set animating flag
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()  # Get current position
        target_x, target_y = self.hidden_pos  # Get target position
        step = CONFIG["animation_speed"]  # Get animation step size

        # Continue animating if not at target position
        if abs(current_x - target_x) > step or abs(current_y - target_y) > step:
            if current_x != target_x:  # Move X position
                new_x = current_x + step if current_x < target_x else current_x - step
            else:
                new_x = current_x
            if current_y != target_y:  # Move Y position
                new_y = current_y + step if current_y < target_y else current_y - step
            else:
                new_y = current_y
            self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")  # Update position
            self.update_animation_position()  # Update animation window position
            self.root.after(10, self.animate_slide_out)  # Schedule next frame
        else:
            # Animation complete, set final position
            self.root.geometry(f"{self.width}x{self.height}+{target_x}+{target_y}")
            self.root.withdraw()  # Hide the window
            self.is_animating = False  # Clear animating flag

    # Method to restart the console (clear chat and reset)
    def restart_console(self, event=None):
        self.chat_area.config(state="normal")  # Enable chat area
        self.chat_area.delete(1.0, tk.END)  # Clear all text
        self.chat_area.config(state="disabled")  # Disable chat area
        self.input_field.delete(0, tk.END)  # Clear input field
        if self.is_visible:  # If console is visible
            self.root.focus_force()  # Focus on the window
            self.root.after(100, self.input_field.focus)  # Focus on input field
        self.chat_area.config(state="normal")  # Enable chat area
        self.chat_area.insert(tk.END, "Console restarted.\n\n", "system")  # Display message
        self.chat_area.config(state="disabled")  # Disable chat area
        self.chat_area.see(tk.END)  # Scroll to the end

    # Method to save the current theme under a new name
    def save_theme(self, theme_name):
        if not theme_name:  # Check if a theme name was provided
            self.chat_area.config(state="normal")  # Enable chat area
            self.chat_area.insert(tk.END, "Usage: /save_theme <name>\n\n", "system")  # Display usage
            self.chat_area.config(state="disabled")  # Disable chat area
            self.chat_area.see(tk.END)  # Scroll to the end
            return
        THEMES[theme_name] = THEMES[self.current_theme].copy()  # Copy current theme
        save_config()  # Save the updated themes
        self.chat_area.config(state="normal")  # Enable chat area
        self.chat_area.insert(tk.END, f"Theme saved as '{theme_name}'.\n\n", "system")  # Display success
        self.chat_area.config(state="disabled")  # Disable chat area
        self.chat_area.see(tk.END)  # Scroll to the end

    # Method to switch to a different theme
    def switch_theme(self, theme_name):
        if theme_name in THEMES:  # Check if the theme exists
            self.current_theme = theme_name  # Set the new theme
            self.apply_theme()  # Apply the theme
            self.chat_area.config(state="normal")  # Enable chat area
            self.chat_area.insert(tk.END, f"Switched to theme: {theme_name}\n\n", "system")  # Display success
            self.chat_area.config(state="disabled")  # Disable chat area
            self.chat_area.see(tk.END)  # Scroll to the end
        else:
            self.chat_area.config(state="normal")  # Enable chat area
            self.chat_area.insert(tk.END, f"Theme '{theme_name}' not found. Available themes: {', '.join(THEMES.keys())}\n\n", "system")  # Display error
            self.chat_area.config(state="disabled")  # Disable chat area
            self.chat_area.see(tk.END)  # Scroll to the end

    # Method to send a message to Ollama
    def send_message(self, event):
        message = self.input_field.get()  # Get the message from the input field
        if not message:  # Check if the message is empty
            return
        self.input_field.delete(0, tk.END)  # Clear the input field

        # Check for commands
        if message.strip().lower() == "/restart":  # Restart command
            self.restart_console()
            return
        elif message.strip().lower() == "/help":  # Help command
            self.display_help()
            return
        elif message.strip().lower() == "/config":  # Config command
            self.open_config_window()
            return
        elif message.strip().lower().startswith("/theme"):  # Theme switch command
            parts = message.strip().split()
            if len(parts) > 1:
                theme_name = parts[1].lower()
                self.switch_theme(theme_name)
            else:
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, f"Usage: /theme <name>. Available themes: {', '.join(THEMES.keys())}\n\n", "system")
                self.chat_area.config(state="disabled")
                self.chat_area.see(tk.END)
            return
        elif message.strip().lower().startswith("/save_theme"):  # Save theme command
            parts = message.strip().split(maxsplit=1)
            if len(parts) > 1:
                theme_name = parts[1].lower()
                self.save_theme(theme_name)
            else:
                self.chat_area.config(state="normal")
                self.chat_area.insert(tk.END, "Usage: /save_theme <name>\n\n", "system")
                self.chat_area.config(state="disabled")
                self.chat_area.see(tk.END)
            return

        # Display the user's message
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"You: {message}\n\n", "user")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

        # Start the animation while the message is being processed
        self.start_animation()

        # Send the message to Ollama in a separate thread
        threading.Thread(target=self.query_ollama, args=(message,), daemon=True).start()

    # Method to query Ollama and display the response
    def query_ollama(self, message):
        payload = {"model": "llama3.2", "prompt": message, "stream": False}  # Prepare the API payload
        try:
            response = requests.post(OLLAMA_API, json=payload)  # Send the request to Ollama
            reply = response.json().get("response", "Error: No response")  # Get the response
        except Exception as e:
            reply = f"Error: {str(e)}"  # Handle errors

        # Display Ollama's response
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{CONFIG['chatbot_name']}: {reply}\n\n", "ollama")
        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

        # Keep the animation running during the response
        self.start_animation()

# Main entry point of the script
if __name__ == "__main__":
    console = OllamaConsole()  # Create and run the console
