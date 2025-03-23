# Import tkinter for GUI creation
import tkinter as tk
# Import scrolledtext widget for chat display and ttk for themed widgets
from tkinter import scrolledtext, ttk
# Import requests for making HTTP requests to Ollama API
import requests
# Import subprocess to run the Ollama server
import subprocess
# Import threading for running tasks (e.g., animation loading) in a separate thread
import threading
# Import keyboard for detecting keypresses (e.g., custom hotkey to toggle console)
import keyboard
# Import get_monitors to detect screen dimensions and monitor info
from screeninfo import get_monitors
# Import os for file operations (e.g., checking if config file exists)
import os
# Import json for reading/writing configuration and chat history to files
import json
# Import Pillow modules for handling GIF frames with transparency
from PIL import Image, ImageTk
# Import glob for handling file patterns (e.g., PNG sequences)
import glob
# Import requests exceptions for better network error handling
from requests.exceptions import RequestException
# Import datetime for adding timestamps to messages
from datetime import datetime

# Define the Ollama API endpoint for sending queries
OLLAMA_API = "http://127.0.0.1:11434/api/generate"
# Define the path to the configuration file
CONFIG_FILE = "F:\\ollama\\config.json"
# Define the path to the chat history file
CHAT_HISTORY_FILE = "F:\\ollama\\chat_history.json"
# Define the default animation path for the dancing robot GIF
DEFAULT_ANIMATION_PATH = "F:\\ollama\\dancing_robot.gif"

# Define default themes for the console appearance as a dictionary
THEMES = {
    "default": {"bg": "#1e1e1e", "fg": "#00ff00", "ollama_fg": "#00b7eb", "input_bg": "#333333", "input_fg": "#ffffff", "alpha": 0.9, "border_color": "#555555"},
    "midnight_blue": {"bg": "#0a1a2b", "fg": "#d0e1f9", "ollama_fg": "#ffcc66", "input_bg": "#1e2a44", "input_fg": "#ffffff", "alpha": 0.9, "border_color": "#2a3a54"},
    "slate_gray": {"bg": "#2b2e3b", "fg": "#b0b3c1", "ollama_fg": "#8aebff", "input_bg": "#3e424f", "input_fg": "#e0e2ea", "alpha": 0.9, "border_color": "#4e525f"},
    "forest_shadow": {"bg": "#1a2b1e", "fg": "#a0c5a0", "ollama_fg": "#7ba87b", "input_bg": "#2a3b2e", "input_fg": "#d0e0d0", "alpha": 0.9, "border_color": "#3a4b3e"},
    "cyberpunk": {"bg": "#0d0d0d", "fg": "#ff00ff", "ollama_fg": "#00ffcc", "input_bg": "#1a1a1a", "input_fg": "#ff00ff", "alpha": 0.95, "border_color": "#ff00ff"},
    "retro_terminal": {"bg": "#000000", "fg": "#00ff00", "ollama_fg": "#00ff00", "input_bg": "#000000", "input_fg": "#00ff00", "alpha": 1.0, "border_color": "#00ff00"}
}

# Define default configuration settings as a dictionary
CONFIG = {
    "monitor": 0,              # Index of the monitor to display the console on
    "slide_from": "top",       # Direction from which the console slides in
    "width": 800,              # Width of the console window
    "height": 300,             # Height of the console window
    "theme": "default",        # Default theme name
    "animation_speed": 10,     # Speed of the slide-in/out animation (pixels per frame)
    "font": "Courier",         # Font type for chat and input
    "font_size": 12,           # Font size for input field
    "chat_font_size": 12,      # Font size for chat area
    "chatbot_name": "Ollama",  # Name of the chatbot
    "animation_alpha": 0.9,    # Transparency for animation window (0.0 to 1.0)
    "animation_width": 270,    # Width of the animation window
    "animation_height": 480,   # Height of the animation window
    "animation_bg": "#1e1e1e", # Background color for animation window (or "transparent")
    "animation_enabled": True, # Boolean to enable/disable the animation canvas
    "gif_path": DEFAULT_ANIMATION_PATH,  # Path to the GIF file or PNG sequence folder
    "gif_frame_delay": 100,    # Delay between GIF frames in milliseconds
    "ollama_model": "llama3.2",# Default Ollama model to use
    "user_prefix": "You:",     # Prefix for user messages
    "ollama_prefix": "Ollama:",# Prefix for Ollama messages
    "auto_save_chat": False,   # Boolean to enable/disable auto-saving of chat history
    "hotkey": "`"              # Default hotkey to toggle the console
}

# Function to load configuration from file
def load_config():
    global THEMES, CONFIG  # Declare global variables to modify them
    if os.path.exists(CONFIG_FILE):  # Check if the config file exists
        try:  # Attempt to load the config file
            with open(CONFIG_FILE, "r") as f:  # Open the config file in read mode
                saved_config = json.load(f)  # Parse the JSON content into a Python dictionary
                CONFIG.update(saved_config.get("config", {}))  # Update CONFIG with saved settings, default to empty dict if "config" key missing
                saved_themes = saved_config.get("themes", {})  # Get saved themes, default to empty dict if "themes" key missing
                for theme_name, theme in saved_themes.items():  # Iterate over each saved theme
                    if "ollama_fg" not in theme:  # Check if "ollama_fg" is missing in the theme
                        theme["ollama_fg"] = THEMES.get(theme_name, THEMES["default"])["ollama_fg"]  # Add default ollama_fg if missing
                THEMES.update(saved_themes)  # Update THEMES dictionary with saved themes
        except (json.JSONDecodeError, IOError) as e:  # Catch JSON parsing or file I/O errors
            print(f"Error loading config: {e}")  # Print error message to console

# Function to save configuration to file
def save_config():
    config_to_save = {"config": CONFIG.copy(), "themes": {name: theme.copy() for name, theme in THEMES.items()}}  # Create a dictionary with config and themes to save
    try:  # Attempt to save the config file
        with open(CONFIG_FILE, "w") as f:  # Open the config file in write mode
            json.dump(config_to_save, f, indent=4)  # Write the config as JSON with indentation for readability
    except IOError as e:  # Catch file I/O errors
        print(f"Error saving config: {e}")  # Print error message to console

# Load configuration when the script starts
load_config()

# Define the main console class
class OllamaConsole:
    def __init__(self):
        self.start_ollama_server()  # Start the Ollama server if not already running
        self.monitors = get_monitors()  # Get list of available monitors
        self.monitor = self.monitors[CONFIG["monitor"]]  # Select the monitor specified in CONFIG
        self.screen_width, self.screen_height = self.monitor.width, self.monitor.height  # Set screen dimensions from selected monitor
        self.x_offset, self.y_offset = self.monitor.x, self.monitor.y  # Set monitor offsets for positioning

        self.root = tk.Tk()  # Create the main Tkinter window
        self.root.overrideredirect(True)  # Remove window decorations (title bar, borders)
        self.current_theme = CONFIG["theme"]  # Set the current theme from CONFIG

        self.animation_window = tk.Toplevel(self.root)  # Create a separate top-level window for the animation
        self.animation_window.overrideredirect(True)  # Remove decorations from animation window
        self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])  # Set transparency for animation window
        self.animation_window.configure(bg="black" if CONFIG["animation_bg"].lower() == "transparent" else CONFIG["animation_bg"])  # Set background color or transparency
        if CONFIG["animation_bg"].lower() == "transparent":  # Check if animation background is set to transparent
            self.animation_window.wm_attributes("-transparentcolor", "black")  # Make black color transparent on Windows
        self.animation_window.withdraw()  # Hide the animation window initially

        self.animation_canvas = tk.Canvas(self.animation_window, width=CONFIG["animation_width"], height=CONFIG["animation_height"],
                                         bg="black" if CONFIG["animation_bg"].lower() == "transparent" else CONFIG["animation_bg"], highlightthickness=0)  # Create canvas for animation
        self.animation_canvas.pack()  # Add the canvas to the animation window
        self.gif_path = CONFIG["gif_path"]  # Set the path to the animation file or folder from CONFIG
        self.gif_frames = []  # Initialize empty list to store animation frames
        self.current_frame = 0  # Track the current frame index
        self.animation_running = False  # Flag to indicate if animation is running
        threading.Thread(target=self.load_animation, daemon=True).start()  # Start loading animation frames in a separate thread

        self.width, self.height = CONFIG["width"], CONFIG["height"]  # Set console window dimensions from CONFIG
        self.slide_from = CONFIG["slide_from"]  # Set slide direction from CONFIG
        self.set_initial_position()  # Calculate and set the initial off-screen position

        self.chat_area = scrolledtext.ScrolledText(self.root, bg=THEMES[self.current_theme]["bg"], fg=THEMES[self.current_theme]["fg"],
                                                   height=10, width=80, wrap=tk.WORD, state="disabled", font=(CONFIG["font"], CONFIG["chat_font_size"]))  # Create chat display area
        self.chat_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)  # Add chat area to window with padding and make it resizable
        self.chat_area.tag_configure("user", foreground=THEMES[self.current_theme]["fg"])  # Configure text color for user messages
        self.chat_area.tag_configure("ollama", foreground=THEMES[self.current_theme]["ollama_fg"])  # Configure text color for Ollama responses
        self.chat_area.tag_configure("system", foreground="#aaaaaa")  # Configure text color for system messages (gray)

        self.input_field = tk.Entry(self.root, bg=THEMES[self.current_theme]["input_bg"], fg=THEMES[self.current_theme]["input_fg"],
                                    insertbackground=THEMES[self.current_theme]["fg"], width=80, font=(CONFIG["font"], CONFIG["font_size"]))  # Create input field for user messages
        self.input_field.pack(padx=5, pady=5, fill=tk.X)  # Add input field to window with padding and make it stretch horizontally
        self.input_field.bind("<Return>", self.send_message)  # Bind Enter key to send message
        self.input_field.bind("<Control-r>", self.restart_console)  # Bind Ctrl+R to restart console

        self.is_visible = False  # Track if the console is currently visible
        self.is_animating = False  # Track if an animation is in progress
        self.first_open = True  # Track if this is the first time the console is opened
        self.config_window = None  # Reference to the config window (None if not open)
        self.root.withdraw()  # Hide the main window initially
        self.hotkey = CONFIG["hotkey"]  # Set the hotkey from CONFIG
        keyboard.on_press_key(self.hotkey, self.toggle_console)  # Bind the hotkey to toggle the console

        self.apply_theme()  # Apply the theme after all widgets are initialized

        self.root.mainloop()  # Start the Tkinter event loop

    # Method to check if an image has transparency
    def has_transparency(self, image):
        return image.mode == "RGBA" and any(pixel < 255 for pixel in image.split()[3].getdata())  # Return True if image has alpha channel with non-opaque pixels

    # Method to load animation frames (GIF or PNG sequence) in a separate thread
    def load_animation(self):
        self.gif_frames.clear()  # Clear any existing frames
        try:  # Attempt to load animation
            if not os.path.exists(self.gif_path):  # Check if the animation path exists
                raise FileNotFoundError(f"Animation path not found: {self.gif_path}")  # Raise error if path doesn't exist
            if os.path.isdir(self.gif_path):  # Check if the path is a directory (PNG sequence)
                png_files = sorted(glob.glob(os.path.join(self.gif_path, "frame_*.png")))  # Get sorted list of PNG files matching pattern
                if not png_files:  # Check if any PNG files were found
                    raise FileNotFoundError("No PNG files found in the specified directory")  # Raise error if no files found
                for png_file in png_files:  # Loop through each PNG file
                    frame = Image.open(png_file).convert("RGBA")  # Open PNG and convert to RGBA for transparency
                    self.gif_frames.append(ImageTk.PhotoImage(frame))  # Convert to PhotoImage and add to frames list
            else:  # Assume the path is a GIF file
                if not self.gif_path.lower().endswith(".gif"):  # Check if file has .gif extension
                    raise ValueError("File must be a .gif if not a directory")  # Raise error if not a GIF
                gif = Image.open(self.gif_path)  # Open the GIF file
                frame_count = 0  # Initialize frame counter
                while True:  # Loop through each frame of the GIF
                    try:  # Attempt to seek to next frame
                        gif.seek(frame_count)  # Move to the current frame
                        frame = gif.convert("RGBA")  # Convert frame to RGBA for transparency
                        self.gif_frames.append(ImageTk.PhotoImage(frame))  # Convert to PhotoImage and add to frames list
                        frame_count += 1  # Increment frame counter
                    except EOFError:  # Catch end-of-file error (no more frames)
                        break  # Exit loop when no more frames are available
            self.animation_canvas.create_image(CONFIG["animation_width"] // 2, CONFIG["animation_height"] // 2,
                                               image=self.gif_frames[0], anchor="center")  # Display the first frame centered on the canvas
        except Exception as e:  # Catch any errors during loading
            self.display_message(f"Error loading animation: {str(e)}\n\n", "system")  # Display error message in chat area

    # Method to animate the GIF or PNG sequence by cycling through frames
    def animate_gif(self):
        if self.animation_running and self.gif_frames:  # Check if animation is running and frames exist
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)  # Move to next frame, looping back to 0 if at end
            self.animation_canvas.delete("all")  # Clear the canvas of previous frame
            self.animation_canvas.create_image(CONFIG["animation_width"] // 2, CONFIG["animation_height"] // 2,
                                               image=self.gif_frames[self.current_frame], anchor="center")  # Draw current frame centered
            self.root.after(CONFIG["gif_frame_delay"], self.animate_gif)  # Schedule next frame after delay

    # Method to start the animation
    def start_animation(self):
        if CONFIG["animation_enabled"] and not self.animation_running and self.is_visible:  # Check if animation is enabled, not running, and console is visible
            self.animation_running = True  # Set animation running flag
            self.animation_window.deiconify()  # Show the animation window
            self.update_animation_position()  # Update animation window position relative to console
            self.animate_gif()  # Start the animation loop

    # Method to stop the animation
    def stop_animation(self):
        self.animation_running = False  # Clear animation running flag
        self.animation_window.withdraw()  # Hide the animation window

    # Method to update the position of the animation window relative to the console
    def update_animation_position(self):
        console_x, console_y = self.root.winfo_x(), self.root.winfo_y()  # Get current position of the console window
        animation_x = console_x + self.width + 10  # Position animation 10 pixels to the right of console
        animation_y = console_y  # Align animation vertically with console
        self.animation_window.geometry(f"{CONFIG['animation_width']}x{CONFIG['animation_height']}+{animation_x}+{animation_y}")  # Set new geometry for animation window

    # Method to apply the current theme to the UI
    def apply_theme(self):
        theme = THEMES[self.current_theme]  # Get the current theme dictionary
        self.root.attributes("-alpha", theme["alpha"])  # Set main window transparency
        self.root.configure(bg=theme["bg"], highlightbackground=theme["border_color"], highlightthickness=2)  # Set main window background and border
        self.chat_area.configure(bg=theme["bg"], fg=theme["fg"])  # Update chat area background and foreground colors
        self.chat_area.tag_configure("user", foreground=theme["fg"])  # Update user message color
        self.chat_area.tag_configure("ollama", foreground=theme["ollama_fg"])  # Update Ollama message color
        self.input_field.configure(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["fg"])  # Update input field colors and cursor
        self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])  # Set animation window transparency
        bg = "black" if CONFIG["animation_bg"].lower() == "transparent" else CONFIG["animation_bg"]  # Determine animation background color
        self.animation_window.configure(bg=bg)  # Apply background color to animation window
        if CONFIG["animation_bg"].lower() == "transparent":  # Check if animation background is transparent
            self.animation_window.wm_attributes("-transparentcolor", "black")  # Make black transparent on Windows
        self.animation_canvas.configure(bg=bg)  # Apply background color to animation canvas

    # Method to start the Ollama server if it's not running
    def start_ollama_server(self):
        try:  # Attempt to check if Ollama server is running
            requests.get("http://127.0.0.1:11434", timeout=2)  # Send a quick GET request to check server status
        except requests.ConnectionError:  # Catch connection error if server isn't running
            subprocess.Popen(["F:\\ollama\\ollama.exe", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)  # Start Ollama server without a console window
            import time  # Import time module for delay
            time.sleep(5)  # Wait 5 seconds to ensure server starts

    # Method to set the initial off-screen position of the console window
    def set_initial_position(self):
        if self.slide_from == "top":  # If sliding from top
            self.hidden_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset - self.height)  # Set hidden position above screen
            self.visible_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset)  # Set visible position at top of screen
        elif self.slide_from == "bottom":  # If sliding from bottom
            self.hidden_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset + self.screen_height)  # Set hidden position below screen
            self.visible_pos = (self.x_offset + (self.screen_width - self.width) // 2, self.y_offset + self.screen_height - self.height)  # Set visible position at bottom
        elif self.slide_from == "left":  # If sliding from left
            self.hidden_pos = (self.x_offset - self.width, self.y_offset + (self.screen_height - self.height) // 2)  # Set hidden position left of screen
            self.visible_pos = (self.x_offset, self.y_offset + (self.screen_height - self.height) // 2)  # Set visible position at left edge
        elif self.slide_from == "right":  # If sliding from right
            self.hidden_pos = (self.x_offset + self.screen_width, self.y_offset + (self.screen_height - self.height) // 2)  # Set hidden position right of screen
            self.visible_pos = (self.x_offset + self.screen_width - self.width, self.y_offset + (self.screen_height - self.height) // 2)  # Set visible position at right edge
        self.root.geometry(f"{self.width}x{self.height}+{self.hidden_pos[0]}+{self.hidden_pos[1]}")  # Set initial geometry to hidden position
        self.update_animation_position()  # Update animation window position

    # Method to display a message in the chat area
    def display_message(self, message, tag="system"):
        self.chat_area.config(state="normal")  # Enable chat area for editing
        self.chat_area.insert(tk.END, message, tag)  # Insert message with specified tag (color)
        self.chat_area.config(state="disabled")  # Disable chat area to prevent user edits
        self.chat_area.see(tk.END)  # Scroll to the end of the chat area

    # Method to display the help menu in the chat area
    def display_help(self):
        help_text = (
            "=== Chatbot Console Commands ===\n"
            "/help - Show this help menu\n"
            "/restart - Clear chat and restart\n"
            "/clear - Clear chat without restarting\n"
            "/theme <name> - Switch themes\n"
            "/save_theme <name> - Save current theme\n"
            "/config - Open configuration window\n"
            "/save_chat - Save chat history\n"
            "/load_chat - Load chat history\n"
            "/export <filename> - Export chat to text file\n"
            "/wordcount - Display chat word count\n"
            f"{self.hotkey} - Toggle console\n"
            "Ctrl+R - Restart console\n"
            "===============================\n"
        )  # Define help text with available commands
        self.display_message(help_text)  # Display the help text in chat area

    # Method to save the chat history to a file
    def save_chat_history(self):
        chat_content = self.chat_area.get(1.0, tk.END).strip()  # Get all text from chat area and remove trailing whitespace
        try:  # Attempt to save chat history
            with open(CHAT_HISTORY_FILE, "w") as f:  # Open chat history file in write mode
                json.dump({"chat": chat_content}, f, indent=4)  # Save chat content as JSON with indentation
            self.display_message("Chat history saved.\n\n")  # Display success message
        except IOError as e:  # Catch file I/O errors
            self.display_message(f"Error saving chat history: {str(e)}\n\n")  # Display error message

    # Method to load the chat history from a file
    def load_chat_history(self):
        try:  # Attempt to load chat history
            if os.path.exists(CHAT_HISTORY_FILE):  # Check if chat history file exists
                with open(CHAT_HISTORY_FILE, "r") as f:  # Open file in read mode
                    data = json.load(f)  # Parse JSON content
                    chat_content = data.get("chat", "")  # Get chat content, default to empty string if missing
                self.chat_area.config(state="normal")  # Enable chat area for editing
                self.chat_area.delete(1.0, tk.END)  # Clear current chat content
                self.chat_area.insert(tk.END, chat_content)  # Insert loaded chat content
                self.chat_area.config(state="disabled")  # Disable chat area
                self.display_message("Chat history loaded.\n\n")  # Display success message
            else:  # If file doesn't exist
                self.display_message("No chat history file found.\n\n")  # Display error message
        except (json.JSONDecodeError, IOError) as e:  # Catch JSON parsing or file I/O errors
            self.display_message(f"Error loading chat history: {str(e)}\n\n")  # Display error message

    # Method to export chat history to a text file
    def export_chat(self, filename):
        chat_content = self.chat_area.get(1.0, tk.END).strip()  # Get all text from chat area
        try:  # Attempt to export chat
            with open(filename, "w", encoding="utf-8") as f:  # Open specified file in write mode with UTF-8 encoding
                f.write(chat_content)  # Write chat content to file
            self.display_message(f"Chat exported to {filename}.\n\n")  # Display success message
        except IOError as e:  # Catch file I/O errors
            self.display_message(f"Error exporting chat: {str(e)}\n\n")  # Display error message

    # Method to calculate and display the word count of the chat history
    def word_count(self):
        chat_content = self.chat_area.get(1.0, tk.END).strip()  # Get all text from chat area
        word_count = len(chat_content.split())  # Split text into words and count them
        self.display_message(f"Total word count: {word_count}\n\n")  # Display word count

    # Method to open the configuration window
    def open_config_window(self):
        if self.config_window and self.config_window.winfo_exists():  # Check if config window is already open
            self.config_window.lift()  # Bring existing config window to the front
            return  # Exit method
        self.config_window = tk.Toplevel(self.root)  # Create a new top-level window for configuration
        self.config_window.title("Console Configuration")  # Set window title
        self.config_window.geometry("450x1000")  # Set window size
        self.config_window.configure(bg="#2e2e2e")  # Set background color
        self.config_window.resizable(False, False)  # Disable resizing

        main_frame = tk.Frame(self.config_window, bg="#2e2e2e")  # Create a frame to hold all config widgets
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Add frame to window with padding

        # Chatbot Settings Section
        tk.Label(main_frame, text="Chatbot Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="w")  # Section header
        tk.Label(main_frame, text="Chatbot Name:", bg="#2e2e2e", fg="#cccccc").grid(row=1, column=0, sticky="w", padx=5)  # Label for chatbot name
        chatbot_name_var = tk.StringVar(value=CONFIG["chatbot_name"])  # Variable to hold chatbot name
        tk.Entry(main_frame, textvariable=chatbot_name_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=1, column=1, sticky="ew", padx=5)  # Entry field for chatbot name

        tk.Label(main_frame, text="Ollama Model:", bg="#2e2e2e", fg="#cccccc").grid(row=2, column=0, sticky="w", padx=5)  # Label for Ollama model
        ollama_model_var = tk.StringVar(value=CONFIG["ollama_model"])  # Variable to hold Ollama model
        ttk.OptionMenu(main_frame, ollama_model_var, CONFIG["ollama_model"], "llama3.2", "mistral", "gemma", "phi").grid(row=2, column=1, sticky="ew", padx=5)  # Dropdown for model selection

        tk.Label(main_frame, text="User Prefix:", bg="#2e2e2e", fg="#cccccc").grid(row=3, column=0, sticky="w", padx=5)  # Label for user prefix
        user_prefix_var = tk.StringVar(value=CONFIG["user_prefix"])  # Variable to hold user prefix
        tk.Entry(main_frame, textvariable=user_prefix_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=3, column=1, sticky="ew", padx=5)  # Entry field for user prefix

        tk.Label(main_frame, text="Ollama Prefix:", bg="#2e2e2e", fg="#cccccc").grid(row=4, column=0, sticky="w", padx=5)  # Label for Ollama prefix
        ollama_prefix_var = tk.StringVar(value=CONFIG["ollama_prefix"])  # Variable to hold Ollama prefix
        tk.Entry(main_frame, textvariable=ollama_prefix_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=4, column=1, sticky="ew", padx=5)  # Entry field for Ollama prefix

        tk.Label(main_frame, text="Auto-Save Chat:", bg="#2e2e2e", fg="#cccccc").grid(row=5, column=0, sticky="w", padx=5)  # Label for auto-save option
        auto_save_chat_var = tk.BooleanVar(value=CONFIG["auto_save_chat"])  # Variable to hold auto-save state
        tk.Checkbutton(main_frame, variable=auto_save_chat_var, bg="#2e2e2e", fg="#ffffff", selectcolor="#3e3e3e").grid(row=5, column=1, sticky="w", padx=5)  # Checkbox for auto-save

        # Font Settings Section
        tk.Label(main_frame, text="Font Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky="w")  # Section header
        tk.Label(main_frame, text="Font Type:", bg="#2e2e2e", fg="#cccccc").grid(row=7, column=0, sticky="w", padx=5)  # Label for font type
        font_var = tk.StringVar(value=CONFIG["font"])  # Variable to hold font type
        ttk.OptionMenu(main_frame, font_var, CONFIG["font"], "Courier", "Arial", "Helvetica", "Times").grid(row=7, column=1, sticky="ew", padx=5)  # Dropdown for font selection

        tk.Label(main_frame, text="Chat Font Size:", bg="#2e2e2e", fg="#cccccc").grid(row=8, column=0, sticky="w", padx=5)  # Label for chat font size
        chat_font_size_var = tk.StringVar(value=str(CONFIG["chat_font_size"]))  # Variable to hold chat font size
        tk.Entry(main_frame, textvariable=chat_font_size_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=8, column=1, sticky="ew", padx=5)  # Entry field for chat font size

        tk.Label(main_frame, text="Input Font Size:", bg="#2e2e2e", fg="#cccccc").grid(row=9, column=0, sticky="w", padx=5)  # Label for input font size
        font_size_var = tk.StringVar(value=str(CONFIG["font_size"]))  # Variable to hold input font size
        tk.Entry(main_frame, textvariable=font_size_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=9, column=1, sticky="ew", padx=5)  # Entry field for input font size

        # Color Settings Section with Previews
        tk.Label(main_frame, text="Color Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=10, column=0, columnspan=2, pady=(10, 5), sticky="w")  # Section header
        tk.Label(main_frame, text="User Text Color:", bg="#2e2e2e", fg="#cccccc").grid(row=11, column=0, sticky="w", padx=5)  # Label for user text color
        chat_fg_var = tk.StringVar(value=THEMES[self.current_theme]["fg"])  # Variable to hold user text color
        chat_fg_entry = tk.Entry(main_frame, textvariable=chat_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for user text color
        chat_fg_entry.grid(row=11, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=chat_fg_var.get(), width=2).grid(row=11, column=2, padx=5)  # Preview square for user text color

        tk.Label(main_frame, text="Chatbot Text Color:", bg="#2e2e2e", fg="#cccccc").grid(row=12, column=0, sticky="w", padx=5)  # Label for chatbot text color
        ollama_fg_var = tk.StringVar(value=THEMES[self.current_theme]["ollama_fg"])  # Variable to hold chatbot text color
        ollama_fg_entry = tk.Entry(main_frame, textvariable=ollama_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for chatbot text color
        ollama_fg_entry.grid(row=12, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=ollama_fg_var.get(), width=2).grid(row=12, column=2, padx=5)  # Preview square for chatbot text color

        tk.Label(main_frame, text="Input Text Color:", bg="#2e2e2e", fg="#cccccc").grid(row=13, column=0, sticky="w", padx=5)  # Label for input text color
        input_fg_var = tk.StringVar(value=THEMES[self.current_theme]["input_fg"])  # Variable to hold input text color
        input_fg_entry = tk.Entry(main_frame, textvariable=input_fg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for input text color
        input_fg_entry.grid(row=13, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=input_fg_var.get(), width=2).grid(row=13, column=2, padx=5)  # Preview square for input text color

        tk.Label(main_frame, text="Window Background:", bg="#2e2e2e", fg="#cccccc").grid(row=14, column=0, sticky="w", padx=5)  # Label for window background
        bg_var = tk.StringVar(value=THEMES[self.current_theme]["bg"])  # Variable to hold window background color
        bg_entry = tk.Entry(main_frame, textvariable=bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for window background
        bg_entry.grid(row=14, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=bg_var.get(), width=2).grid(row=14, column=2, padx=5)  # Preview square for window background

        tk.Label(main_frame, text="Input Background:", bg="#2e2e2e", fg="#cccccc").grid(row=15, column=0, sticky="w", padx=5)  # Label for input background
        input_bg_var = tk.StringVar(value=THEMES[self.current_theme]["input_bg"])  # Variable to hold input background color
        input_bg_entry = tk.Entry(main_frame, textvariable=input_bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for input background
        input_bg_entry.grid(row=15, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=input_bg_var.get(), width=2).grid(row=15, column=2, padx=5)  # Preview square for input background

        tk.Label(main_frame, text="Border Color:", bg="#2e2e2e", fg="#cccccc").grid(row=16, column=0, sticky="w", padx=5)  # Label for border color
        border_var = tk.StringVar(value=THEMES[self.current_theme]["border_color"])  # Variable to hold border color
        border_entry = tk.Entry(main_frame, textvariable=border_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff")  # Entry field for border color
        border_entry.grid(row=16, column=1, sticky="ew", padx=5)  # Place entry field in grid
        tk.Label(main_frame, bg=border_var.get(), width=2).grid(row=16, column=2, padx=5)  # Preview square for border color

        tk.Label(main_frame, text="Transparency (0.0-1.0):", bg="#2e2e2e", fg="#cccccc").grid(row=17, column=0, sticky="w", padx=5)  # Label for transparency
        alpha_var = tk.StringVar(value=str(THEMES[self.current_theme]["alpha"]))  # Variable to hold transparency value
        tk.Entry(main_frame, textvariable=alpha_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=17, column=1, sticky="ew", padx=5)  # Entry field for transparency

        # Animation Settings Section
        tk.Label(main_frame, text="Animation Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=18, column=0, columnspan=2, pady=(10, 5), sticky="w")  # Section header
        tk.Label(main_frame, text="Enable Animation:", bg="#2e2e2e", fg="#cccccc").grid(row=19, column=0, sticky="w", padx=5)  # Label for animation enable
        animation_enabled_var = tk.BooleanVar(value=CONFIG["animation_enabled"])  # Variable to hold animation enabled state
        tk.Checkbutton(main_frame, variable=animation_enabled_var, bg="#2e2e2e", fg="#ffffff", selectcolor="#3e3e3e").grid(row=19, column=1, sticky="w", padx=5)  # Checkbox for animation

        tk.Label(main_frame, text="Animation Transparency:", bg="#2e2e2e", fg="#cccccc").grid(row=20, column=0, sticky="w", padx=5)  # Label for animation transparency
        animation_alpha_var = tk.StringVar(value=str(CONFIG["animation_alpha"]))  # Variable to hold animation transparency
        tk.Entry(main_frame, textvariable=animation_alpha_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=20, column=1, sticky="ew", padx=5)  # Entry field for animation transparency

        tk.Label(main_frame, text="Animation Width:", bg="#2e2e2e", fg="#cccccc").grid(row=21, column=0, sticky="w", padx=5)  # Label for animation width
        animation_width_var = tk.StringVar(value=str(CONFIG["animation_width"]))  # Variable to hold animation width
        tk.Entry(main_frame, textvariable=animation_width_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=21, column=1, sticky="ew", padx=5)  # Entry field for animation width

        tk.Label(main_frame, text="Animation Height:", bg="#2e2e2e", fg="#cccccc").grid(row=22, column=0, sticky="w", padx=5)  # Label for animation height
        animation_height_var = tk.StringVar(value=str(CONFIG["animation_height"]))  # Variable to hold animation height
        tk.Entry(main_frame, textvariable=animation_height_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=22, column=1, sticky="ew", padx=5)  # Entry field for animation height

        tk.Label(main_frame, text="Animation BG:", bg="#2e2e2e", fg="#cccccc").grid(row=23, column=0, sticky="w", padx=5)  # Label for animation background
        animation_bg_var = tk.StringVar(value=CONFIG["animation_bg"])  # Variable to hold animation background color
        tk.Entry(main_frame, textvariable=animation_bg_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=23, column=1, sticky="ew", padx=5)  # Entry field for animation background

        tk.Label(main_frame, text="Animation Path:", bg="#2e2e2e", fg="#cccccc").grid(row=24, column=0, sticky="w", padx=5)  # Label for animation path
        gif_path_var = tk.StringVar(value=CONFIG["gif_path"])  # Variable to hold animation path
        tk.Entry(main_frame, textvariable=gif_path_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=24, column=1, sticky="ew", padx=5)  # Entry field for animation path
        tk.Button(main_frame, text="Reset", command=lambda: gif_path_var.set(DEFAULT_ANIMATION_PATH), bg="#4e4e4e", fg="#ffffff").grid(row=25, column=1, sticky="w", padx=5)  # Button to reset path to default

        tk.Label(main_frame, text="Frame Delay (ms):", bg="#2e2e2e", fg="#cccccc").grid(row=26, column=0, sticky="w", padx=5)  # Label for frame delay
        gif_frame_delay_var = tk.StringVar(value=str(CONFIG["gif_frame_delay"]))  # Variable to hold frame delay
        tk.Entry(main_frame, textvariable=gif_frame_delay_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=26, column=1, sticky="ew", padx=5)  # Entry field for frame delay

        # Window Settings Section
        tk.Label(main_frame, text="Window Settings", bg="#2e2e2e", fg="#ffffff", font=("Arial", 12, "bold")).grid(row=27, column=0, columnspan=2, pady=(10, 5), sticky="w")  # Section header
        tk.Label(main_frame, text="Width:", bg="#2e2e2e", fg="#cccccc").grid(row=28, column=0, sticky="w", padx=5)  # Label for window width
        width_var = tk.StringVar(value=str(CONFIG["width"]))  # Variable to hold window width
        tk.Entry(main_frame, textvariable=width_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=28, column=1, sticky="ew", padx=5)  # Entry field for window width

        tk.Label(main_frame, text="Height:", bg="#2e2e2e", fg="#cccccc").grid(row=29, column=0, sticky="w", padx=5)  # Label for window height
        height_var = tk.StringVar(value=str(CONFIG["height"]))  # Variable to hold window height
        tk.Entry(main_frame, textvariable=height_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=29, column=1, sticky="ew", padx=5)  # Entry field for window height

        tk.Label(main_frame, text="Animation Speed:", bg="#2e2e2e", fg="#cccccc").grid(row=30, column=0, sticky="w", padx=5)  # Label for animation speed
        anim_speed_var = tk.StringVar(value=str(CONFIG["animation_speed"]))  # Variable to hold animation speed
        tk.Entry(main_frame, textvariable=anim_speed_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=30, column=1, sticky="ew", padx=5)  # Entry field for animation speed

        tk.Label(main_frame, text="Slide From:", bg="#2e2e2e", fg="#cccccc").grid(row=31, column=0, sticky="w", padx=5)  # Label for slide direction
        slide_var = tk.StringVar(value=CONFIG["slide_from"])  # Variable to hold slide direction
        ttk.OptionMenu(main_frame, slide_var, CONFIG["slide_from"], "top", "bottom", "left", "right").grid(row=31, column=1, sticky="ew", padx=5)  # Dropdown for slide direction

        tk.Label(main_frame, text="Monitor:", bg="#2e2e2e", fg="#cccccc").grid(row=32, column=0, sticky="w", padx=5)  # Label for monitor selection
        monitor_var = tk.StringVar(value=str(CONFIG["monitor"]))  # Variable to hold monitor index
        ttk.OptionMenu(main_frame, monitor_var, str(CONFIG["monitor"]), *[str(i) for i in range(len(self.monitors))]).grid(row=32, column=1, sticky="ew", padx=5)  # Dropdown for monitor selection

        tk.Label(main_frame, text="Hotkey:", bg="#2e2e2e", fg="#cccccc").grid(row=33, column=0, sticky="w", padx=5)  # Label for hotkey
        hotkey_var = tk.StringVar(value=CONFIG["hotkey"])  # Variable to hold hotkey
        tk.Entry(main_frame, textvariable=hotkey_var, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff").grid(row=33, column=1, sticky="ew", padx=5)  # Entry field for hotkey

        # Function to apply configuration changes
        def apply_config():
            try:  # Attempt to apply config changes
                CONFIG.update({  # Update CONFIG dictionary with new values
                    "chatbot_name": chatbot_name_var.get(), "ollama_model": ollama_model_var.get(),
                    "user_prefix": user_prefix_var.get(), "ollama_prefix": ollama_prefix_var.get(),
                    "auto_save_chat": auto_save_chat_var.get(), "font": font_var.get(),
                    "font_size": int(font_size_var.get()), "chat_font_size": int(chat_font_size_var.get()),
                    "animation_enabled": animation_enabled_var.get(), "animation_alpha": float(animation_alpha_var.get()),
                    "animation_width": int(animation_width_var.get()), "animation_height": int(animation_height_var.get()),
                    "animation_bg": animation_bg_var.get(), "gif_path": gif_path_var.get(),
                    "gif_frame_delay": int(gif_frame_delay_var.get()), "width": int(width_var.get()),
                    "height": int(height_var.get()), "animation_speed": int(anim_speed_var.get()),
                    "slide_from": slide_var.get(), "monitor": int(monitor_var.get()), "hotkey": hotkey_var.get()
                })
                THEMES[self.current_theme].update({  # Update current theme with new color values
                    "fg": chat_fg_var.get(), "ollama_fg": ollama_fg_var.get(), "input_fg": input_fg_var.get(),
                    "bg": bg_var.get(), "input_bg": input_bg_var.get(), "border_color": border_var.get(),
                    "alpha": float(alpha_var.get())
                })
                self.width, self.height = CONFIG["width"], CONFIG["height"]  # Update instance width and height
                self.slide_from = CONFIG["slide_from"]  # Update slide direction
                self.monitor = self.monitors[CONFIG["monitor"]]  # Update selected monitor
                self.screen_width, self.screen_height = self.monitor.width, self.monitor.height  # Update screen dimensions
                self.x_offset, self.y_offset = self.monitor.x, self.monitor.y  # Update monitor offsets
                self.set_initial_position()  # Recalculate window positions
                self.chat_area.configure(font=(CONFIG["font"], CONFIG["chat_font_size"]))  # Update chat area font
                self.input_field.configure(font=(CONFIG["font"], CONFIG["font_size"]))  # Update input field font
                self.animation_window.attributes("-alpha", CONFIG["animation_alpha"])  # Update animation window transparency
                self.animation_canvas.configure(width=CONFIG["animation_width"], height=CONFIG["animation_height"])  # Update animation canvas size
                bg = "black" if CONFIG["animation_bg"].lower() == "transparent" else CONFIG["animation_bg"]  # Determine animation background
                self.animation_window.configure(bg=bg)  # Apply background to animation window
                if CONFIG["animation_bg"].lower() == "transparent":  # Check if transparent
                    self.animation_window.wm_attributes("-transparentcolor", "black")  # Set black as transparent color
                self.animation_canvas.configure(bg=bg)  # Apply background to canvas
                self.gif_path = CONFIG["gif_path"]  # Update GIF path
                self.gif_frames.clear()  # Clear existing frames
                self.current_frame = 0  # Reset frame index
                threading.Thread(target=self.load_animation, daemon=True).start()  # Reload animation in a separate thread
                self.apply_theme()  # Apply updated theme
                keyboard.unhook_all()  # Remove all existing key bindings
                self.hotkey = CONFIG["hotkey"]  # Update hotkey
                keyboard.on_press_key(self.hotkey, self.toggle_console)  # Rebind hotkey
                if CONFIG["animation_enabled"] and self.is_visible:  # Check if animation should start
                    self.start_animation()  # Start animation if enabled and console visible
                else:  # If animation disabled or console hidden
                    self.stop_animation()  # Stop animation
                self.display_message("Configuration updated.\n\n")  # Display success message
            except Exception as e:  # Catch any errors during application
                self.display_message(f"Error applying config: {str(e)}\n\n")  # Display error message

        # Function to apply changes and save them
        def save_and_close():
            apply_config()  # Apply configuration changes
            save_config()  # Save changes to file
            self.display_message("Configuration saved.\n\n")  # Display success message
            self.config_window.destroy()  # Close the config window

        button_frame = tk.Frame(main_frame, bg="#2e2e2e")  # Create frame for buttons
        button_frame.grid(row=34, column=0, columnspan=2, pady=10)  # Place button frame in grid
        tk.Button(button_frame, text="Apply", command=apply_config, bg="#4e4e4e", fg="#ffffff").pack(side=tk.LEFT, padx=5)  # Apply button
        tk.Button(button_frame, text="Save & Close", command=save_and_close, bg="#4e4e4e", fg="#ffffff").pack(side=tk.LEFT, padx=5)  # Save & Close button
        main_frame.columnconfigure(1, weight=1)  # Make column 1 (entry fields) expandable

    # Method to toggle console visibility when hotkey is pressed
    def toggle_console(self, event):
        if self.is_animating:  # Check if animation is currently running
            return  # Do nothing if animating
        self.is_visible = not self.is_visible  # Toggle visibility state
        if self.is_visible:  # If making visible
            self.root.deiconify()  # Show the main window
            self.start_animation()  # Start the animation
            self.animate_slide_in()  # Slide the console in
        else:  # If hiding
            self.stop_animation()  # Stop the animation
            self.animate_slide_out()  # Slide the console out

    # Method to animate the console sliding in
    def animate_slide_in(self):
        self.is_animating = True  # Set animating flag
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()  # Get current window position
        target_x, target_y = self.visible_pos  # Get target visible position
        step = CONFIG["animation_speed"]  # Get animation step size
        if abs(current_x - target_x) > step or abs(current_y - target_y) > step:  # Check if not yet at target
            new_x = current_x + step if current_x < target_x else current_x - step if current_x > target_x else current_x  # Calculate new X position
            new_y = current_y + step if current_y < target_y else current_y - step if current_y > target_y else current_y  # Calculate new Y position
            self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")  # Update window position
            self.update_animation_position()  # Update animation window position
            self.root.after(10, self.animate_slide_in)  # Schedule next frame after 10ms
        else:  # If at target position
            self.root.geometry(f"{self.width}x{self.height}+{target_x}+{target_y}")  # Set final position
            self.update_animation_position()  # Update animation window position
            self.is_animating = False  # Clear animating flag
            if self.first_open:  # If first time opening
                self.display_help()  # Show help menu
                self.first_open = False  # Mark as not first open
            self.root.focus_force()  # Force focus on the window
            self.root.after(100, self.input_field.focus)  # Focus on input field after 100ms

    # Method to animate the console sliding out
    def animate_slide_out(self):
        self.is_animating = True  # Set animating flag
        current_x, current_y = self.root.winfo_x(), self.root.winfo_y()  # Get current window position
        target_x, target_y = self.hidden_pos  # Get target hidden position
        step = CONFIG["animation_speed"]  # Get animation step size
        if abs(current_x - target_x) > step or abs(current_y - target_y) > step:  # Check if not yet at target
            new_x = current_x + step if current_x < target_x else current_x - step if current_x > target_x else current_x  # Calculate new X position
            new_y = current_y + step if current_y < target_y else current_y - step if current_y > target_y else current_y  # Calculate new Y position
            self.root.geometry(f"{self.width}x{self.height}+{new_x}+{new_y}")  # Update window position
            self.update_animation_position()  # Update animation window position
            self.root.after(10, self.animate_slide_out)  # Schedule next frame after 10ms
        else:  # If at target position
            self.root.geometry(f"{self.width}x{self.height}+{target_x}+{target_y}")  # Set final position
            self.root.withdraw()  # Hide the window
            self.is_animating = False  # Clear animating flag

    # Method to restart the console (clear chat and reset)
    def restart_console(self, event=None):
        self.chat_area.config(state="normal")  # Enable chat area for editing
        self.chat_area.delete(1.0, tk.END)  # Clear all text in chat area
        self.chat_area.config(state="disabled")  # Disable chat area
        self.input_field.delete(0, tk.END)  # Clear input field
        if self.is_visible:  # If console is visible
            self.root.focus_force()  # Force focus on window
            self.root.after(100, self.input_field.focus)  # Focus on input field after 100ms
        self.display_message("Console restarted.\n\n")  # Display restart message

    # Method to clear the chat without restarting
    def clear_chat(self):
        self.chat_area.config(state="normal")  # Enable chat area for editing
        self.chat_area.delete(1.0, tk.END)  # Clear all text in chat area
        self.chat_area.config(state="disabled")  # Disable chat area
        self.display_message("Chat cleared.\n\n")  # Display clear message

    # Method to save the current theme under a new name
    def save_theme(self, theme_name):
        if not theme_name:  # Check if theme name is provided
            self.display_message("Usage: /save_theme <name>\n\n")  # Display usage message
            return  # Exit method
        THEMES[theme_name] = THEMES[self.current_theme].copy()  # Copy current theme to new name
        save_config()  # Save updated themes to file
        self.display_message(f"Theme saved as '{theme_name}'.\n\n")  # Display success message

    # Method to switch to a different theme
    def switch_theme(self, theme_name):
        if theme_name in THEMES:  # Check if theme exists
            self.current_theme = theme_name  # Set new current theme
            self.apply_theme()  # Apply the new theme
            self.display_message(f"Switched to theme: {theme_name}\n\n")  # Display success message
        else:  # If theme doesn't exist
            self.display_message(f"Theme '{theme_name}' not found. Available: {', '.join(THEMES.keys())}\n\n")  # Display error with available themes

    # Method to send a message from the input field
    def send_message(self, event):
        message = self.input_field.get().strip()  # Get and strip message from input field
        if not message:  # Check if message is empty
            return  # Exit method if empty
        self.input_field.delete(0, tk.END)  # Clear input field

        if message.lower() == "/restart":  # Check for restart command
            self.restart_console()  # Restart console
        elif message.lower() == "/help":  # Check for help command
            self.display_help()  # Display help menu
        elif message.lower() == "/config":  # Check for config command
            self.open_config_window()  # Open config window
        elif message.lower() == "/save_chat":  # Check for save chat command
            self.save_chat_history()  # Save chat history
        elif message.lower() == "/load_chat":  # Check for load chat command
            self.load_chat_history()  # Load chat history
        elif message.lower() == "/clear":  # Check for clear command
            self.clear_chat()  # Clear chat
        elif message.lower() == "/wordcount":  # Check for wordcount command
            self.word_count()  # Display word count
        elif message.lower().startswith("/theme"):  # Check for theme switch command
            parts = message.split()  # Split command into parts
            if len(parts) > 1:  # Check if theme name provided
                self.switch_theme(parts[1].lower())  # Switch to specified theme
            else:  # If no theme name provided
                self.display_message(f"Usage: /theme <name>. Available: {', '.join(THEMES.keys())}\n\n")  # Display usage
        elif message.lower().startswith("/save_theme"):  # Check for save theme command
            parts = message.split(maxsplit=1)  # Split command into parts, max 1 split
            if len(parts) > 1:  # Check if theme name provided
                self.save_theme(parts[1].lower())  # Save current theme with specified name
            else:  # If no theme name provided
                self.display_message("Usage: /save_theme <name>\n\n")  # Display usage
        elif message.lower().startswith("/export"):  # Check for export command
            parts = message.split(maxsplit=1)  # Split command into parts, max 1 split
            if len(parts) > 1:  # Check if filename provided
                self.export_chat(parts[1])  # Export chat to specified file
            else:  # If no filename provided
                self.display_message("Usage: /export <filename>\n\n")  # Display usage
        else:  # If message is not a command
            timestamp = datetime.now().strftime("[%H:%M:%S]")  # Get current timestamp in [HH:MM:SS] format
            self.display_message(f"{timestamp} {CONFIG['user_prefix']} {message}\n\n", "user")  # Display user message with timestamp
            self.start_animation()  # Start animation while processing
            threading.Thread(target=self.query_ollama, args=(message, timestamp), daemon=True).start()  # Query Ollama in a separate thread

    # Method to query Ollama and display the response
    def query_ollama(self, message, timestamp):
        payload = {"model": CONFIG["ollama_model"], "prompt": message, "stream": True}  # Prepare API payload with streaming enabled
        try:  # Attempt to query Ollama
            response = requests.post(OLLAMA_API, json=payload, stream=True, timeout=10)  # Send POST request with streaming
            response.raise_for_status()  # Raise exception for HTTP errors
            reply = ""  # Initialize empty reply string
            self.display_message(f"{timestamp} {CONFIG['ollama_prefix']}\n", "ollama")  # Display Ollama prefix with timestamp
            for line in response.iter_lines():  # Iterate over streaming response lines
                if line:  # Check if line is not empty
                    data = json.loads(line.decode('utf-8'))  # Parse JSON line
                    chunk = data.get("response", "")  # Get response chunk, default to empty string
                    reply += chunk  # Append chunk to reply
                    self.chat_area.config(state="normal")  # Enable chat area
                    self.chat_area.insert(tk.END, chunk, "ollama")  # Insert chunk into chat area
                    self.chat_area.see(tk.END)  # Scroll to end
                    self.chat_area.config(state="disabled")  # Disable chat area
                    self.root.update_idletasks()  # Update UI to show new text
            self.display_message("\n\n", "ollama")  # Add newline after response
        except RequestException as e:  # Catch network-related errors
            reply = f"Error: {str(e)}"  # Set error message
            self.display_message(f"{timestamp} {CONFIG['ollama_prefix']}\n    {reply}\n\n", "ollama")  # Display error message
        if CONFIG["auto_save_chat"]:  # Check if auto-save is enabled
            self.save_chat_history()  # Save chat history
        self.start_animation()  # Keep animation running during response

# Main entry point of the script
if __name__ == "__main__":
    console = OllamaConsole()  # Create and run the console instance
