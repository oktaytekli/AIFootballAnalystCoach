v2.0 - Web Platform Transformation & SaaS Architecture
With this major update, the project has evolved from a local Python script into a full-stack modern web application powered by Flask.

New Features:

Web Interface (Frontend):
    Landing Page: Modern design with Tailwind CSS, video background, and animations (AOS, Typed.js).
    Dashboard: A professional admin panel with a collapsible sidebar for managing analysis.
    Auth System: B2B-focused login system restricting access to authorized (Admin) users only.

Setup Wizard:
    Automatic snapshot retrieval from YouTube links.
    Pixel-Perfect Color Picker: Select team colors directly by clicking on the video frame.
    Custom start time selection to skip video intros.

Token & Credit System:
    Cost calculation based on video duration (1 min = 1 Token).
    Balance checks and "Play within Budget" functionality.
    Simple database (users.json) for user and balance management.

Video Control Center:
    Web-based controls to Play / Pause / Seek the analysis video.
    Dynamic team name updates during live analysis.

Performance & Backend:
    Threading Architecture: Decoupled video processing from the web server using Python threading. Analysis continues in the background even if the tab is inactive.
    Live Data Streaming: Real-time updates for scores and AI commentary via AJAX/Fetch API without page reloads.