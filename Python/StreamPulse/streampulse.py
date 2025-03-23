# Import system module for interacting with the operating system
import sys
# Import os module for file and directory operations
import os
# Import subprocess module to spawn external processes like FFmpeg
import subprocess
# Import threading module to run tasks concurrently
import threading
# Import psutil module to monitor system processes
import psutil
# Import time module for timing and delays
import time
# Import pygetwindow for window management on Windows
import pygetwindow as gw
# Import win32gui for low-level Windows GUI operations
import win32gui
# Import logging module for logging application events
import logging
# Import get_monitors from screeninfo to detect monitor configurations
from screeninfo import get_monitors
# Import dxcam for high-performance screen capture
import dxcam
# Import OpenCV (cv2) for image processing
import cv2
# Import NumPy for numerical operations on image data
import numpy as np
# Import PyQt5 widgets for building the GUI
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QFormLayout, QSpinBox, QMessageBox, QCheckBox
)
# Import PyQt5 core module for Qt constants and timers
from PyQt5.QtCore import Qt, QTimer
# Import PyQt5 GUI module for colors and fonts
from PyQt5.QtGui import QColor, QFont
# Import traceback module to format exception stack traces
import traceback
# Import RotatingFileHandler for log file rotation
from logging.handlers import RotatingFileHandler

# Define the version of the application
__version__ = "1.5.25"

# Set the base directory for file paths
BASE_DIR = "[Directory Here]"
# Define the RTSP server address and port
RTSP_SERVER = "localhost:8555"
# Set the path to FFmpeg executable
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg", "ffmpeg.exe")
# Set the path to yt-dlp executable
YTDLP_PATH = os.path.join(BASE_DIR, "yt-dlp", "yt-dlp.exe")
# Set the path to MediaMTX executable
MEDIAMTX_PATH = os.path.join(BASE_DIR, "mediamtx", "mediamtx.exe")
# Define the log file path with a timestamp
LOG_FILE = os.path.join(BASE_DIR, "logs", f"streampulse_{time.strftime('%Y%m%d_%H%M%S')}.log.txt")

# Create a logger instance
logger = logging.getLogger()
# Set the logging level to INFO (less verbose than DEBUG)
logger.setLevel(logging.INFO)
# Create a rotating file handler with 5MB max size and 2 backups
handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
# Set the log message format with timestamp, level, and message
handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s", "%Y-%m-%d %H:%M:%S"))
# Add the handler to the logger
logger.addHandler(handler)

# Set debug mode to False to reduce logging verbosity
DEBUG_MODE = False

# Define a dictionary of streams with their configurations
STREAMS = {
    "radar": {
        "type": "window",           # Stream type is window capture
        "name": "RadarOmega",       # Name of the window to capture
        "active": False,            # Whether the stream is currently active
        "process": None,            # Subprocess object for FFmpeg
        "status": "Inactive",       # Current status of the stream
        "width": 0,                 # Output width (0 for native)
        "height": 0,                # Output height (0 for native)
        "fps": 30,                  # Frames per second
        "lock_position": False,     # Whether to lock capture position
        "last_region": None         # Last captured region
    },
    "broadway": {
        "type": "",                 # Type is empty (possibly a placeholder)
        "name": "RadarOmega",       # Name of the window
        "active": False,            # Stream is inactive
        "process": None,            # No process assigned
        "status": "Inactive",       # Status is inactive
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 60 FPS (Note: Comment says 60 but code says 30)
        "lock_position": False,     # Position not locked
        "last_region": None         # No last region
    },
    "mystream1": {
        "type": "window",           # Window capture stream
        "name": "RadarOmega",       # Window name
        "active": False,            # Inactive
        "process": None,            # No process
        "status": "Inactive",       # Inactive status
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 60 FPS (Note: Comment says 60 but code says 30)
        "lock_position": False,     # Position not locked
        "last_region": None         # No last region
    },
    "mystream2": {
        "type": "window",           # Window capture stream
        "name": "RadarOmega",       # Window name
        "active": False,            # Inactive
        "process": None,            # No process
        "status": "Inactive",       # Inactive status
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 60 FPS (Note: Comment says 60 but code says 30)
        "lock_position": False,     # Position not locked
        "last_region": None         # No last region
    },
    "mystream3": {
        "type": "window",           # Window capture stream
        "name": "RadarOmega",       # Window name
        "active": False,            # Inactive
        "process": None,            # No process
        "status": "Inactive",       # Inactive status
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 60 FPS (Note: Comment says 60 but code says 30)
        "lock_position": False,     # Position not locked
        "last_region": None         # No last region
    },
    "ryanhallyall": {
        "type": "youtube",          # YouTube stream
        "url": "[URL Here]",        # YouTube URL placeholder
        "active": False,            # Inactive
        "process": None,            # No process
        "status": "Inactive",       # Inactive status
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 30 FPS
        "lock_position": False      # Position not locked
    },
    "fallback": {
        "type": "youtube",          # YouTube stream
        "url": "[URL Here]",        # YouTube URL placeholder
        "active": False,            # Inactive
        "process": None,            # No process
        "status": "Inactive",       # Inactive status
        "width": 0,                 # Native width
        "height": 0,                # Native height
        "fps": 30,                  # 30 FPS
        "lock_position": False      # Position not locked
    }
}

# Define the main window class for the application
class streampulseWindow(QMainWindow):
    # Initialize the window
    def __init__(self):
        # Call the parent class (QMainWindow) initializer
        super().__init__()
        # Set the window title with the version
        self.setWindowTitle(f"streampulse Stream Manager v{__version__}")
        # Set the window geometry (x, y, width, height)
        self.setGeometry(100, 100, 900, 600)
        # Flag to track if table is being edited
        self.editing = False
        # Log the application start
        logger.info(f"Starting streampulse v{__version__}")
        # Try to initialize the UI and other components
        try:
            # Initialize the user interface
            self.init_ui()
            # Check if MediaMTX is running
            self.check_mediamtx()
            # Create a timer to update status periodically
            self.status_timer = QTimer(self)
            # Connect the timer's timeout signal to update_status method
            self.status_timer.timeout.connect(self.update_status)
            # Start the timer to trigger every 2000ms (2 seconds)
            self.status_timer.start(2000)
            # Create a lock for thread-safe status updates
            self.status_lock = threading.Lock()
        # Handle any exceptions during initialization
        except Exception as e:
            # Log the error with stack trace
            logger.error(f"Initialization failed: {str(e)}\n{traceback.format_exc()}")
            # Show an error message box
            QMessageBox.critical(self, "Error", f"Failed to initialize: {str(e)}")
            # Exit the application with an error code
            sys.exit(1)

    # Initialize the user interface
    def init_ui(self):
        # Create a central widget for the window
        central_widget = QWidget()
        # Set the central widget for the main window
        self.setCentralWidget(central_widget)
        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)
        # Set the stylesheet for the UI elements
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QPushButton { background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px; }
            QPushButton:hover { background-color: #45a049; }
            QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 3px; }
            QTableWidget { border: 1px solid #ddd; background-color: white; }
            QGroupBox { font-weight: bold; border: 1px solid #ccc; border-radius: 5px; padding: 10px; }
        """)
        # Create a table widget for displaying streams
        self.stream_table = QTableWidget(0, 8)
        # Set the column headers for the table
        self.stream_table.setHorizontalHeaderLabels(["Stream", "Type", "Source", "Status", "Capture Active", "Start/Stop", "Remove", "Lock Position"])
        # Make the table columns stretch to fill the width
        self.stream_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Set the font for the table
        self.stream_table.setFont(QFont("Arial", 10))
        # Connect double-click event to start editing
        self.stream_table.itemDoubleClicked.connect(self.start_editing)
        # Connect item changed event to update stream source
        self.stream_table.itemChanged.connect(self.update_stream_source)
        # Add the table to the layout
        layout.addWidget(self.stream_table)
        # Update the stream table with current data
        self.update_stream_table()
        # Create a group box for stream configuration
        config_group = QGroupBox("Stream Configuration")
        # Create a form layout for the configuration group
        config_layout = QFormLayout()
        # Create a text input for the stream source
        self.source_input = QLineEdit()
        # Set placeholder text for the source input
        self.source_input.setPlaceholderText("YouTube URL or Window Name")
        # Add the source input to the form layout
        config_layout.addRow("Source:", self.source_input)
        # Create a spin box for width configuration
        self.width_spin = QSpinBox()
        # Set the range for the width spin box
        self.width_spin.setRange(0, 3840)
        # Set the default value for width
        self.width_spin.setValue(0)
        # Add the width spin box to the form layout
        config_layout.addRow("Width (0 for native):", self.width_spin)
        # Create a spin box for height configuration
        self.height_spin = QSpinBox()
        # Set the range for the height spin box
        self.height_spin.setRange(0, 2160)
        # Set the default value for height
        self.height_spin.setValue(0)
        # Add the height spin box to the form layout
        config_layout.addRow("Height (0 for native):", self.height_spin)
        # Create a spin box for FPS configuration
        self.fps_spin = QSpinBox()
        # Set the range for the FPS spin box
        self.fps_spin.setRange(1, 60)
        # Set the default value for FPS
        self.fps_spin.setValue(30)
        # Add the FPS spin box to the form layout
        config_layout.addRow("FPS:", self.fps_spin)
        # Create a checkbox for locking capture position
        self.lock_checkbox = QCheckBox("Lock Capture Position")
        # Add the lock checkbox to the form layout
        config_layout.addRow(self.lock_checkbox)
        # Create a button to add a new stream
        self.add_btn = QPushButton("Add Stream")
        # Connect the button click to the add_stream method
        self.add_btn.clicked.connect(self.add_stream)
        # Add the add button to the form layout
        config_layout.addRow(self.add_btn)
        # Set the layout for the config group
        config_group.setLayout(config_layout)
        # Add the config group to the main layout
        layout.addWidget(config_group)
        # Create a label for status updates
        self.status_label = QLabel("Status: Idle")
        # Set the style for the status label
        self.status_label.setStyleSheet("background-color: #e0e0e0; padding: 5px;")
        # Add the status label to the layout
        layout.addWidget(self.status_label)

    # Start editing a table item when double-clicked
    def start_editing(self, item):
        # Set editing flag to True
        self.editing = True
        # Begin editing the selected item
        self.stream_table.editItem(item)

    # Update the stream table with current stream data
    def update_stream_table(self):
        # Skip update if currently editing
        if self.editing:
            return
        # Block signals to prevent unwanted updates
        self.stream_table.blockSignals(True)
        # Clear the table rows
        self.stream_table.setRowCount(0)
        # Iterate over each stream in the STREAMS dictionary
        for stream_key, stream in STREAMS.items():
            # Get the current row count
            row = self.stream_table.rowCount()
            # Insert a new row
            self.stream_table.insertRow(row)
            # Add the stream key to the first column
            self.stream_table.setItem(row, 0, QTableWidgetItem(stream_key))
            # Add the stream type to the second column
            self.stream_table.setItem(row, 1, QTableWidgetItem(stream["type"]))
            # Create an editable item for the source
            source_item = QTableWidgetItem(stream.get("url", stream.get("name", "")))
            # Make the source item editable
            source_item.setFlags(source_item.flags() | Qt.ItemIsEditable)
            # Add the source item to the third column
            self.stream_table.setItem(row, 2, source_item)
            # Create an item for the status
            status_item = QTableWidgetItem(stream["status"])
            # Check if the stream is active
            is_active = stream["active"]
            # Set the background color based on active status
            status_item.setBackground(QColor("lightgreen" if is_active else "lightcoral"))
            # Add the status item to the fourth column
            self.stream_table.setItem(row, 3, status_item)
            # Determine if capture is active (process is running)
            capture_active = stream["active"] and stream["process"] and stream["process"].poll() is None
            # Create an item for capture active status
            capture_item = QTableWidgetItem("")
            # Set the background color based on capture status
            capture_item.setBackground(QColor("green" if capture_active else "red"))
            # Add the capture item to the fifth column
            self.stream_table.setItem(row, 4, capture_item)
            # Create a start/stop button
            start_stop_btn = QPushButton("Stop" if stream["active"] else "Start")
            # Connect the button click to toggle_stream with the stream key
            start_stop_btn.clicked.connect(lambda _, k=stream_key: self.toggle_stream(k))
            # Add the button to the sixth column
            self.stream_table.setCellWidget(row, 5, start_stop_btn)
            # Create a remove button
            remove_btn = QPushButton("Remove")
            # Connect the button click to remove_stream with the stream key
            remove_btn.clicked.connect(lambda _, k=stream_key: self.remove_stream(k))
            # Disable the button for protected streams
            remove_btn.setEnabled(stream_key not in ["radar", "mystream2", "fallback"])
            # Add the remove button to the seventh column
            self.stream_table.setCellWidget(row, 6, remove_btn)
            # Create a checkbox for locking position
            lock_checkbox = QCheckBox()
            # Set the checkbox state based on lock_position
            lock_checkbox.setChecked(stream["lock_position"])
            # Connect the checkbox state change to toggle_lock
            lock_checkbox.stateChanged.connect(lambda state, k=stream_key: self.toggle_lock(k, state))
            # Add the checkbox to the eighth column
            self.stream_table.setCellWidget(row, 7, lock_checkbox)
        # Re-enable signals after updating
        self.stream_table.blockSignals(False)

    # Toggle the lock position for a stream
    def toggle_lock(self, stream_key, state):
        # Update the lock_position value in the STREAMS dictionary
        STREAMS[stream_key]["lock_position"] = bool(state)
        # Log the change
        logger.info(f"Lock position for {stream_key} set to {bool(state)}")

    # Update the stream source when edited in the table
    def update_stream_source(self, item):
        # Try to update the stream source
        try:
            # Get the row of the edited item
            row = item.row()
            # Get the stream key from the first column
            stream_key = self.stream_table.item(row, 0).text()
            # Get the new source text
            new_source = item.text().strip()
            # Check if the stream key exists
            if stream_key not in STREAMS:
                # Raise an error if the stream is not found
                raise KeyError(f"Stream '{stream_key}' not found")
            # Get the stream dictionary
            stream = STREAMS[stream_key]
            # Update the URL or name based on stream type
            if stream["type"] == "youtube":
                # Update the URL for YouTube streams
                stream["url"] = new_source
                # Log the update
                logger.info(f"Updated {stream_key} URL to: {new_source}")
            else:
                # Update the name for window streams
                stream["name"] = new_source
                # Log the update
                logger.info(f"Updated {stream_key} name to: {new_source}")
            # Update the status label
            self.status_label.setText(f"Status: Updated {stream_key}")
        # Handle any exceptions during update
        except Exception as e:
            # Log the error with stack trace
            logger.error(f"Error updating {stream_key}: {str(e)}\n{traceback.format_exc()}")
            # Show a warning message box
            QMessageBox.warning(self, "Error", f"Failed to update stream: {e}")
        # Reset editing flag and update table
        finally:
            # Set editing flag to False
            self.editing = False
            # Refresh the stream table
            self.update_stream_table()

    # Check if MediaMTX is running
    def check_mediamtx(self):
        # Check if any process named 'mediamtx.exe' is running
        mediamtx_running = any(proc.info['name'].lower() == 'mediamtx.exe' for proc in psutil.process_iter(['pid', 'name']))
        # Update status if MediaMTX is not running
        if not mediamtx_running:
            # Set the status label
            self.status_label.setText("Status: MediaMTX not running. Start it manually or via batch file with admin rights.")
            # Log a warning
            logger.warning("MediaMTX not detected")
        # Update status if MediaMTX is running
        else:
            # Set the status label
            self.status_label.setText("Status: MediaMTX detected")
            # Log the detection
            logger.info("MediaMTX detected")

    # Toggle a stream on or off
    def toggle_stream(self, stream_key):
        # Get the stream dictionary
        stream = STREAMS[stream_key]
        # Stop the stream if it's active
        if stream["active"]:
            # Call stop_stream method
            self.stop_stream(stream_key)
        # Start the stream if it's inactive
        else:
            # Call start_stream method
            self.start_stream(stream_key)
        # Update the stream table
        self.update_stream_table()

    # Start a stream
    def start_stream(self, stream_key):
        # Check if MediaMTX is running
        mediamtx_running = any(proc.info['name'].lower() == 'mediamtx.exe' for proc in psutil.process_iter(['pid', 'name']))
        # Warn if MediaMTX is not running
        if not mediamtx_running:
            # Show a warning message box
            QMessageBox.warning(self, "Warning", "MediaMTX is not running. Start it manually or via batch file with admin rights.")
            # Exit the method
            return
        # Get the stream dictionary
        stream = STREAMS[stream_key]
        # Start window capture if type is window
        if stream["type"] == "window":
            # Call start_window_capture with stream parameters
            self.start_window_capture(stream_key, stream["name"], stream["width"], stream["height"], stream["fps"])
        # Start YouTube stream if type is youtube
        elif stream["type"] == "youtube":
            # Call start_youtube_stream with stream parameters
            self.start_youtube_stream(stream_key, stream["url"], stream["width"], stream["height"], stream["fps"])
        # Mark the stream as active
        stream["active"] = True
        # Update the stream status
        stream["status"] = "Streaming"
        # Update the status label
        self.status_label.setText(f"Status: Started {stream_key}")
        # Log the stream start
        logger.info(f"Started stream {stream_key} at rtsp://{RTSP_SERVER}/{stream_key}")

    # Define a method to log FFmpeg output
    def log_ffmpeg_output(self, ffmpeg_process, stream_key):
        # Read lines from FFmpeg stderr
        for line in iter(ffmpeg_process.stderr.readline, b''):
            # Check if the line contains an error
            if "error" in line.decode().lower():
                # Log the error
                logger.error(f"FFmpeg error for {stream_key}: {line.decode().strip()}")

    # Start capturing a window stream
    def start_window_capture(self, stream_key, window_name, width, height, fps):
        # Define a function to feed frames to FFmpeg
        def feed_frames(camera, ffmpeg_process, stream_key, fps, captured_width, captured_height):
            # Initialize frame counter
            frame_count = 0
            # Record the last logging time
            last_log_time = time.time()
            # Continue while stream is active and capture is running
            while STREAMS[stream_key]["active"] and camera.is_capturing and ffmpeg_process.poll() is None:
                # Get the latest frame from the camera
                frame = camera.get_latest_frame()
                # Process the frame if it exists
                if frame is not None:
                    # Try to feed the frame to FFmpeg
                    try:
                        # Convert frame to bytes
                        buffer = frame.tobytes()
                        # Write the buffer to FFmpeg stdin
                        ffmpeg_process.stdin.write(buffer)
                        # Flush the stdin buffer
                        ffmpeg_process.stdin.flush()
                        # Increment the frame counter
                        frame_count += 1
                        # Log every 5 seconds
                        if time.time() - last_log_time >= 5:
                            # Log the frame count and buffer size
                            logger.info(f"Streaming {stream_key}: frame {frame_count}, size: {len(buffer)} bytes")
                            # Update the last log time
                            last_log_time = time.time()
                    # Handle any exceptions during frame feeding
                    except Exception as e:
                        # Log the error
                        logger.error(f"Error feeding frame for {stream_key}: {str(e)}")
                        # Break the loop
                        break
                # Sleep to maintain the target FPS
                time.sleep(1 / fps)

        # Define a function to monitor the window and stream
        def monitor_and_stream():
            # Initialize camera and FFmpeg process variables
            camera = None
            ffmpeg_process = None
            current_output_idx = None
            initial_region = None
            captured_width = None
            captured_height = None
            last_restart_time = 0
            last_window_pos = None
            debounce_delay = 0.5  # Delay to prevent rapid restarts
            # Log the start of window capture
            logger.info(f"Starting window capture for {stream_key}: {window_name}")
            # Continue while the stream is active
            while STREAMS[stream_key]["active"]:
                # Try to monitor and stream
                try:
                    # Find the window by name
                    window = next((w for w in gw.getAllWindows() if window_name.lower() in w.title.lower()), None)
                    # Check if the window was found
                    if not window:
                        # Log a warning if window not found
                        logger.warning(f"Window '{window_name}' not found. Retrying...")
                        # Wait before retrying
                        time.sleep(1)
                        # Skip to next iteration
                        continue
                    # Get window position and size
                    rx, ry, r_width, r_height = window.left, window.top, window.width, window.height
                    rx_adjusted = rx + 24  # Adjust x position
                    ry_adjusted = ry       # No adjustment for y
                    # Get list of monitors
                    monitors = get_monitors()
                    target_monitor_idx = 0  # Default monitor index
                    # Find the monitor containing the window
                    for i, monitor in enumerate(monitors):
                        if (monitor.x <= rx_adjusted < monitor.x + monitor.width and
                            monitor.y <= ry_adjusted < monitor.y + monitor.height):
                            target_monitor_idx = i
                            break
                    # Get the target monitor
                    monitor = monitors[target_monitor_idx]
                    # Calculate capture region within monitor bounds
                    region_left = max(rx_adjusted, monitor.x)
                    region_top = max(ry_adjusted, monitor.y)
                    region_right = min(region_left + r_width, monitor.x + monitor.width)
                    region_bottom = min(region_top + r_height, monitor.y + monitor.height)
                    # Calculate captured dimensions
                    new_captured_width = region_right - region_left
                    new_captured_height = region_bottom - region_top
                    # Define the capture region relative to monitor
                    region = (region_left - monitor.x, region_top - monitor.y, 
                             region_right - monitor.x, region_bottom - monitor.y)
                    # Set the output index
                    output_idx = target_monitor_idx
                    # Use specified width/height or captured dimensions
                    output_width = width if width > 0 else new_captured_width
                    output_height = height if height > 0 else new_captured_height
                    # Ensure even dimensions for FFmpeg
                    if output_width % 2 != 0:
                        output_width -= 1
                    if output_height % 2 != 0:
                        output_height -= 1
                    # Record current window position
                    current_window_pos = (rx, ry, r_width, r_height)
                    # Check conditions for restarting capture
                    size_changed = new_captured_width != captured_width or new_captured_height != captured_height
                    monitor_changed = current_output_idx != output_idx
                    region_changed = not STREAMS[stream_key]["lock_position"] and region != initial_region
                    pos_changed = current_window_pos != last_window_pos and not STREAMS[stream_key]["lock_position"]
                    should_restart = (size_changed or monitor_changed or region_changed or pos_changed) and (time.time() - last_restart_time > debounce_delay)
                    # Log debug info if DEBUG_MODE is enabled
                    if DEBUG_MODE:
                        logger.debug(f"Window {window_name} pos: {current_window_pos}, region: {region}")
                    # Restart camera if needed
                    if camera is None or monitor_changed or (region_changed and not size_changed):
                        if camera:
                            # Stop the existing camera
                            camera.stop()
                            logger.info(f"Stopped previous DXCamera on output {current_output_idx}")
                        # Create a new DXCamera instance
                        camera = dxcam.create(device_idx=0, output_idx=output_idx)
                        if camera is None:
                            # Fallback to output 0 if creation fails
                            logger.error(f"DXCamera failed on output {output_idx}, falling back to 0")
                            camera = dxcam.create(device_idx=0, output_idx=0)
                            output_idx = 0
                        # Start the camera with specified settings
                        camera.start(target_fps=fps, region=region, video_mode=True)
                        logger.info(f"Started DXCamera for {stream_key} on output {output_idx} with region {region}")
                        # Set the initial region
                        initial_region = region
                        # Update the current output index
                        current_output_idx = output_idx
                    # Restart FFmpeg if needed
                    if ffmpeg_process is None or should_restart:
                        if ffmpeg_process:
                            # Terminate the existing FFmpeg process
                            ffmpeg_process.terminate()
                            logger.info(f"Terminated FFmpeg due to change")
                        # Define video filters for FFmpeg
                        vf_filters = [f"scale={output_width}:{output_height}", "format=rgb24,format=yuv420p"]
                        if width > 0 and height > 0:
                            vf_filters = [
                                f"scale={output_width}:{output_height}:force_original_aspect_ratio=decrease",
                                f"pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2",
                                "format=rgb24,format=yuv420p"
                            ]
                        # Define the FFmpeg command
                        cmd = [
                            FFMPEG_PATH, "-f", "rawvideo", "-pixel_format", "rgb24",
                            "-video_size", f"{new_captured_width}x{new_captured_height}", "-framerate", str(fps),
                            "-i", "pipe:0", "-fflags", "nobuffer", "-c:v", "libx264", "-preset", "ultrafast",
                            "-tune", "zerolatency", "-vf", ",".join(vf_filters), "-an", "-f", "rtsp",
                            "-rtsp_transport", "tcp", f"rtsp://{RTSP_SERVER}/{stream_key}"
                        ]
                        # Start the FFmpeg process
                        ffmpeg_process = subprocess.Popen(
                            cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,  # Use PIPE for stderr
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        # Store the process in the STREAMS dictionary
                        STREAMS[stream_key]["process"] = ffmpeg_process
                        # Start a thread to log FFmpeg output using class method
                        threading.Thread(target=self.log_ffmpeg_output, args=(ffmpeg_process, stream_key), daemon=True).start()
                        # Start a thread to feed frames to FFmpeg
                        threading.Thread(target=feed_frames, args=(camera, ffmpeg_process, stream_key, fps, new_captured_width, new_captured_height), daemon=True).start()
                        # Log the FFmpeg start
                        logger.info(f"Started FFmpeg for {stream_key} with region {region}, size {new_captured_width}x{new_captured_height}")
                        # Update captured dimensions
                        captured_width = new_captured_width
                        captured_height = new_captured_height
                        # Update the last restart time
                        last_restart_time = time.time()
                        # Update the last window position
                        last_window_pos = current_window_pos
                        # Update the initial region
                        initial_region = region
                    # Wait before the next check
                    time.sleep(0.5)
                # Handle exceptions in monitoring
                except Exception as e:
                    # Log the error
                    logger.error(f"Error in window capture for {stream_key}: {str(e)}")
                    # Break the loop
                    break
            # Clean up camera if it exists
            if camera:
                # Stop the camera
                camera.stop()
                # Log the stop
                logger.info(f"Stopped DXCamera for {stream_key}")
            # Clean up FFmpeg if it exists
            if ffmpeg_process:
                # Terminate the FFmpeg process
                ffmpeg_process.terminate()
                # Log the stop
                logger.info(f"Stopped FFmpeg for {stream_key}")

        # Start the monitoring thread
        threading.Thread(target=monitor_and_stream, daemon=True).start()

    # Start streaming a YouTube video
    def start_youtube_stream(self, stream_key, url, width, height, fps):
        # Define a function to handle YouTube streaming
        def stream_youtube():
            # Set maximum retry attempts
            max_retries = 3
            # Set delay between retries
            retry_delay = 2
            # Initialize attempt counter
            attempt = 0
            # Log the start attempt
            logger.info(f"Starting YouTube stream {stream_key}: {url}")
            # Continue while active and retries remain
            while attempt < max_retries and STREAMS[stream_key]["active"]:
                # Try to start the stream
                try:
                    # Command to get the HLS URL from yt-dlp
                    ytdlp_cmd = [YTDLP_PATH, "-f", "bestvideo", "--get-url", url]
                    # Execute yt-dlp and get the URL
                    m3u8_url = subprocess.check_output(ytdlp_cmd, text=True, stderr=subprocess.STDOUT).strip()
                    # Check if URL is empty
                    if not m3u8_url:
                        # Raise an error if no URL is returned
                        raise ValueError("yt-dlp returned empty URL")
                    # Define the FFmpeg command
                    cmd = [
                        FFMPEG_PATH, "-re", "-i", m3u8_url,
                        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
                        "-r", str(fps),
                    ]
                    # Add scaling filter if width/height specified
                    if width > 0 and height > 0:
                        cmd.extend(["-vf", f"scale={width}:{height},format=yuv420p"])
                    else:
                        cmd.extend(["-vf", "format=yuv420p"])
                    # Add output options
                    cmd.extend(["-an", "-rtsp_transport", "tcp", "-f", "rtsp", f"rtsp://{RTSP_SERVER}/{stream_key}"])
                    # Start the FFmpeg process
                    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                    # Store the process in the STREAMS dictionary
                    STREAMS[stream_key]["process"] = process
                    # Start a thread to log FFmpeg output using class method
                    threading.Thread(target=self.log_ffmpeg_output, args=(process, stream_key), daemon=True).start()
                    # Wait for the process to complete
                    process.wait()
                    # Check the return code
                    if process.returncode != 0 and STREAMS[stream_key]["active"]:
                        # Log a warning if failed
                        logger.warning(f"Stream {stream_key} failed, retrying ({attempt + 1}/{max_retries})")
                        # Increment attempt counter
                        attempt += 1
                        # Wait before retrying
                        time.sleep(retry_delay)
                    else:
                        # Break if successful or stopped
                        break
                # Handle exceptions during streaming
                except Exception as e:
                    # Log the error
                    logger.error(f"Error starting YouTube stream {stream_key}: {str(e)}")
                    # Break the loop
                    break

        # Start the YouTube streaming thread
        threading.Thread(target=stream_youtube, daemon=True).start()

    # Stop a stream
    def stop_stream(self, stream_key):
        # Get the stream dictionary
        stream = STREAMS[stream_key]
        # Terminate the process if it exists
        if stream["process"]:
            # Terminate the FFmpeg process
            stream["process"].terminate()
            # Clear the process reference
            stream["process"] = None
        # Mark the stream as inactive
        stream["active"] = False
        # Update the stream status
        stream["status"] = "Inactive"
        # Update the status label
        self.status_label.setText(f"Status: Stopped {stream_key}")
        # Log the stop
        logger.info(f"Stopped stream {stream_key}")

    # Add a new stream
    def add_stream(self):
        # Get the source text from the input
        source = self.source_input.text().strip()
        # Check if source is empty
        if not source:
            # Show a warning if no source provided
            QMessageBox.warning(self, "Warning", "Please enter a source!")
            # Exit the method
            return
        # Determine the stream key from the source
        stream_key = source.split("/")[-1] if source.startswith("http") else source
        # Check if stream key already exists
        if stream_key in STREAMS:
            # Show a warning if stream exists
            QMessageBox.warning(self, "Warning", "Stream already exists!")
            # Exit the method
            return
        # Add a YouTube stream if source is a URL
        if source.startswith("http"):
            STREAMS[stream_key] = {
                "type": "youtube", "url": source, "active": False, "process": None,
                "status": "Inactive", "width": self.width_spin.value(),
                "height": self.height_spin.value(), "fps": self.fps_spin.value(),
                "lock_position": False
            }
        # Add a window stream otherwise
        else:
            STREAMS[stream_key] = {
                "type": "window", "name": source, "active": False, "process": None,
                "status": "Inactive", "width": self.width_spin.value(),
                "height": self.height_spin.value(), "fps": self.fps_spin.value(),
                "lock_position": self.lock_checkbox.isChecked()
            }
        # Update the stream table
        self.update_stream_table()
        # Update the status label
        self.status_label.setText(f"Status: Added {stream_key}")
        # Log the addition
        logger.info(f"Added stream {stream_key}")

    # Remove a stream
    def remove_stream(self, stream_key):
        # Check if stream is protected
        if stream_key in ["radar", "mystream2", "fallback"]:
            # Show a warning if trying to remove a protected stream
            QMessageBox.warning(self, "Warning", "Cannot remove primary streams!")
            # Exit the method
            return
        # Stop the stream if it's active
        if STREAMS[stream_key]["active"]:
            # Call stop_stream method
            self.stop_stream(stream_key)
        # Delete the stream from the dictionary
        del STREAMS[stream_key]
        # Update the stream table
        self.update_stream_table()
        # Update the status label
        self.status_label.setText(f"Status: Removed {stream_key}")
        # Log the removal
        logger.info(f"Removed stream {stream_key}")

    # Update the status of all streams
    def update_status(self):
        # Acquire the status lock for thread safety
        with self.status_lock:
            # Iterate over all streams
            for stream_key, stream in STREAMS.items():
                # Check if stream failed
                if stream["active"] and stream["process"] and stream["process"].poll() is not None:
                    # Mark stream as inactive
                    stream["active"] = False
                    # Clear the process reference
                    stream["process"] = None
                    # Update the status to failed
                    stream["status"] = "Failed"
                    # Log the failure
                    logger.warning(f"Stream {stream_key} failed")
            # Update the stream table
            self.update_stream_table()

    # Handle window close event
    def closeEvent(self, event):
        # Stop all active streams
        for stream in STREAMS.values():
            if stream["active"] and stream["process"]:
                # Terminate the FFmpeg process
                stream["process"].terminate()
        # Kill any lingering FFmpeg processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == 'ffmpeg.exe':
                    # Kill the FFmpeg process
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Log a warning if killing fails
                logger.warning(f"Failed to kill ffmpeg process: {proc.info}")
                # Continue to next process
                continue
        # Log the application closure
        logger.info("Application closed")
        # Accept the close event
        event.accept()

# Main entry point of the application
if __name__ == "__main__":
    # Try to start the application
    try:
        # Create the Qt application
        app = QApplication(sys.argv)
        # Create the main window
        window = streampulseWindow()
        # Show the window
        window.show()
        # Execute the application event loop
        sys.exit(app.exec_())
    # Handle any exceptions during startup
    except Exception as e:
        # Log the error
        logger.error(f"Failed to start streampulse: {str(e)}")
        # Exit with an error code
        sys.exit(1)