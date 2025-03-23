Project Summary
This project involved creating and enhancing a Tkinter-based console chat application (console_chat.py) that interacts with the Ollama API for chatbot functionality. The application features a sliding console window with a customizable appearance, a chat area for user and chatbot messages, and an animated GIF (a dancing robot) displayed in a separate window. Over the course of the project, we implemented several key features and improvements:
Core Functionality:
Built a console that slides in/out from a configurable edge of the screen (top, bottom, left, or right) when toggled with the ~ key.

Integrated with the Ollama API to send user messages and display responses in the chat area.

Added a separate animation window displaying a dancing robot GIF that animates while the chatbot is processing or responding.

Customization and Configuration:
Added a /config command to open a configuration window where users can customize settings like window size, font, colors, animation settings, and more.

Implemented a theme system with multiple predefined themes (default, midnight_blue, slate_gray, forest_shadow) and the ability to save custom themes using /save_theme.

Allowed users to configure the animation window's transparency, size, and background color.

Animation Enhancements:
Made the animation window's background transparent, ensuring only the dancing robot GIF is visible (if the GIF itself has a transparent background).

Added the ability to enable/disable the animation via a checkbox in the /config menu, with immediate effect on visibility.

Added a custom field in the /config menu to specify the path to a transparent GIF file, with validation to ensure the file exists and is a .gif.

Bug Fixes and Improvements:
Fixed the "Enable Animation" checkbox functionality to properly show/hide the animation window when toggled.

Ensured the animation only appears when the console is visible and the animation is enabled.

Added detailed comments to every line of code for clarity and maintainability.

The final script is a fully functional, customizable chat console with a visually engaging animation feature, suitable for interacting with the Ollama chatbot in a user-friendly way.

What is Ollama
Ollama is an open-source tool mainly written in Go lang (89%) that runs open LLMs on your local machine (or a server). It acts like a bridge between any open LLM and your machine, not only running them but also providing an API layer on top of them so that another application or service can use them.

Ollama is a user-friendly and powerful software for running LLMs locally. It hides the complexities of LLMs, packaging them to be accessible and easily customizable with a model file. There are alternatives to Ollama, like vllm and aphrodite, but Ollama is surely the most popular one. Ollama provides a clean, user-friendly interface that allows you to interact directly with LLMs, tailoring the experience to your needs.

** One key note that I feel needs to be addressed in installing Ollama.
By default, running the OllamaSetup.exe Just installs it "willy nilly" onto your system, typically C:\Users\[User]\appdata. I did NOT want this & wanted it contained to 1 drive.
Nowhere on Ollamas main download page is this mentioned & the installer does NOT give you an option of choosing where to install Ollama.

Changing Install Location
To install the Ollama application in a location different than your home directory, start the installer with the following flagOllamaSetup.exe /DIR="d:\some\location"

so you need to download, copy, and paste the OllamaSetup.exe (if you opt for the .zip then extract it to the directory of your choice). Then open a cmd.exe, prompt window, CD into the drive/directory if you need to.
Then you want to run OllamaSetup.exe or Ollama.exe /DIR="[The directory you are in or want it to install to] \ [The main folder i.e Ollama] \ [sub folder if you so choose]. The result should be
i.e. OllamaSetup.exe DIR="D:\AI\Ollama". Then Ollama will install to the directory that you specify.
