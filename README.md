# RoboTechX MDX Dubai's Robothon 2025 Repository

### Team Members
- Judhi
- Bittu
- Ziad
- Sydney

Supporting roles: Aman, Harith

- Team video: https://youtu.be/bMHY1cCpEJ8
- Uncut 5 consecutive attempt back-to-back video: https://youtu.be/63KU_glSCqs

### About
This project is part of Robothon Grand Challenge 2025 organized by Munich Institute of Robotics and Machine Intelligence (MIRMI), 
Technical University of Munich (TUM).
The challenge is to program a robot manipulator to do various tasks on a task board distributed by Robothon organizer, which is designed to emulate industrial tasks found in an electronic waste
handling facility. It is designed to be used as a tool for developing, testing, and demonstrating robotic manipulation skill capabilities. 

![Taskboard](https://github.com/a65iv/Robothon-2025/blob/main/photos/robothon2025_taskboard.png)
figure-1: task board 2025

The controller monitors the state of the task board and reports individual task completion times to a public web dashboard to easily share the results. 
View the web dashboard at the following URL: https://bit.ly/robothon2025_dashboard 

The robot workflow is represented in this statemachine:
![State machine](https://github.com/a65iv/Robothon-2025/blob/main/photos/robothon2025_statemachine.png)
figure-3: State machine

In our implementation, the sequence of the task can be re-arranged using Graphical User Interface (GUI) by doing drag-and-drop of the available functions. Any other related functions or dependencies will be automatically arranged accordingly. 
![Task manager](https://github.com/a65iv/Robothon-2025/blob/main/photos/robothon_task_manager.png)
figure-3: Task manager 2025

### Parts List
- Epson VT6 manipulator robot with 6-axis
- Custom pneumatic linear gripper and 3D printed carbon fiber fingers
- USB FHD webcam for localization
- USB 4K camera with zoomed optical lense for screen reading/OCR
- Epson RC8+ software
- Python 3
- Tesseract OCR module
- Dlink wireless router as Ethernet network concentrator
- DELL Laptop as Python code platform

![photos/robothon2025_connectivity.png](https://github.com/a65iv/Robothon-2025/blob/main/photos/robothon2025_connectivitypng.png)
figure-4: connectivity diagram

### Project History
- **09-06-2025:** Completed BYOD 3x3 Slider Puzzle integration. Team video published. Document submitted.
- **07-06-2025:** Integration and making video of 5x successive attempts 
- **03-06-2025:** Image and task recognition
- **27-05-2025:** Task board localization
- **22-05-2025:** Software testing
- **20-05-2025:** Initial setup

  - Dedicated laptop obtained
  - Installed VSCode, Python, GitHub, EPSON RC+8
  - Gripper assembly v1 installed
  - Robot mounted and secured to the table
  - Tele-operated robot to identify optimal workspace position
  - Workspace table clamped onto the robot table
  - Brainstormed navigation and camera mounting positions

---

### Project Setup Instructions

Follow these steps to configure and run the project:

#### 1. Install Python 3.10

Download and install Python 3.10 from the [official website](https://www.python.org/downloads/).

#### 2. Create and Activate Virtual Environment

Set up a simple Python virtual environment:

**macOS/Linux:**

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> **Note:** The `py` command might also be available as `python`, depending on your system configuration.

#### 3. Install Dependencies

Install required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### 4. Calibrate Brightness Threshold

Determine the brightness threshold for detecting button states:

1. Turn ON a button (LED indicator lit).
2. Run:

```bash
py -m modules.Camera --live_feed_detect
```

3. Note the brightness value.
4. Turn OFF the button and repeat the process.
5. Select a threshold between the recorded brightness values and save it in your configuration.

#### 5. Network Configuration

Ensure your computer and Epson VT6 are connected on the same network/subnet for proper communication.

#### 6. Module CLI Tools

Test individual components using provided CLI tools. Each module supports the `-h` or `--help` flag to display usage information:

- **Capture a single image:**

  ```bash
  py -m modules.Camera --take_picture
  ```

- **View live video feed:**

  ```bash
  py -m modules.Camera --live_feed
  ```

- **Live detection for calibration:**

  ```bash
  py -m modules.Camera --live_feed_detect
  ```

#### 7. Run the Main Program

Execute the main script:

```bash
py main.py
```

The script applies your configured brightness threshold, connects to the Epson VT6, and executes the detection-action pipeline.
