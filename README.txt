ORBITLINK MISSION INTELLIGENCE — OOP PYTHON MINI PROJECT
=========================================================

PROJECT PURPOSE
A desktop simulation of autonomous satellite downlink planning for the SomaiyaSat / SomaiyaPod AI use case. It decides which queued data can be sent during a short ground pass using priority, signal quality, battery reserve, packet size, and remaining time.

IMPORTANT CLARIFICATION
The routing logic is an explainable AI-inspired heuristic simulation. It is not a trained machine-learning model and is not flight-qualified. This distinction is stated for accurate project reporting.

REQUIREMENTS
- Python 3.10 or newer recommended
- Tkinter (included with many Python installations; on some Linux systems install python3-tk)
- SQLite (included in Python's standard library)
- python-docx only if you want to regenerate the Word documents; it is not needed to run the app

HOW TO RUN
1. Extract the ZIP folder.
2. Open a terminal/command prompt in the OrbitLink_AI_Mission_Control folder.
3. Run: python main.py
4. Click "Generate test queue" or add packets manually.
5. Click "Run 60-second pass".
6. Click "Build report" to generate and open website/mission_report.html.

FILES
- main.py: Tkinter interface and pass simulation
- models.py: abstract Packet class, inheritance, polymorphism, routing score
- database.py: SQLite tables and CRUD operations
- website.py: generates the read-only HTML report
- website/mission_report.html: generated after Build report
- Project_Report.docx: project report
- Project_Explanation.docx: code walkthrough and viva preparation
- orbitlink.db: created automatically on first run

CONTROL RULES
- TT&C / Health has highest base priority and the lowest signal threshold.
- SSTV images need a stronger signal.
- M17 / Codec2 voice can use the remaining eligible capacity.
- The routing score is adjusted for signal and low battery.
- A packet is deferred if signal is too weak, the power reserve is below the safe simulation threshold, or there is not enough time.
- Each decision is stored in SQLite with an explanation.

BUTTONS
All interactive controls are Tkinter buttons. The generated HTML report is display-only; its CSS controls visual styling and layout, not application behaviour.

DATABASE
The app creates orbitlink.db automatically in the project folder. Packet and session records persist until Reset is confirmed.

ACADEMIC NOTE
The project demonstrates classes/objects, constructors, inheritance, abstract classes, polymorphism, exception handling, GUI design, database connectivity, and data visualization/report presentation. The simulation uses random link and battery values for demonstration, not real satellite telemetry.
