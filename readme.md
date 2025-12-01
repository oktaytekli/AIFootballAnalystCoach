AI Football Analyst Pro is an advanced Python tool that watches football matches on YouTube in real-time and performs tactical analysis using Computer Vision and Generative AI.
The system tracks players and the ball, estimates possession rates, and provides "Virtual Manager" commentary powered by Google Gemini.

🚀 Features
    Real-Time Match Viewing: Processes YouTube links (HLS streams) without buffering or freezing.
    Smart Object Tracking: Uses YOLOv8 and ByteTrack to maintain player IDs in memory and prevent flickering.
    Dynamic Team Setup: Automatically detects team colors by clicking on a jersey at the start of the match.
    Dashboard Mode: Offers a sleek, resource-efficient information panel that displays only the statistics, reducing computer load.
    Virtual Manager: Google Gemini 2.0 Flash model analyzes the game flow and provides commentary (in a Mourinho/Guardiola style).
    Post-Match Report: Reads data when the match ends and generates pie and radar charts for visualization.

🛠️ Installation
    Download the Project:
        git clone 
        cd ai-football-analyst

    Install Required Libraries:
        requirements.txt

    Set Up API Key:
        Create a file named .env in the project folder.
        Paste your API key obtained from Google AI Studio inside it

🎮 Usage
    Step 1: Start Analysis
        Open the terminal and run the main engine (python main.py)
    
    Step 2: Team Setup
        When the program starts, the video will pause, and a window will open:
        Click on a player's jersey for Team 1 and type the team name in the terminal.
        Do the same for Team 2.
        The window will close, and the Live Statistics Dashboard will open.

    Step 3: Monitor the Game
        Follow the data on the black panel.
        The program performs automatic analysis every 60 seconds.
        To exit, click on the panel and press the q key.
    
    Step 4: Get Visual Report
        To generate visual charts after the match ends, run (python visualize_report.py)

📂 File Structure
        main.py: The brain of the project. Manages the interface and flow.
        vision_ai.py: Computer vision and object tracking (YOLO) module.
        coach_ai.py: AI module that communicates with Google Gemini.
        video_stream.py: Module that converts YouTube videos into a processable format.
        prompts.py: Instructions defining the AI's "character".
        visualize_report.py: Tool that reads the text report and draws charts.
        config.py: Configuration file containing settings.

⚠️ Requirements
    Python 3.10 or higher
    GPU (Recommended for faster analysis)
    Google Gemini API Key (Free to obtain)