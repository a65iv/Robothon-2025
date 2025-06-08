# RoboTechX MDX Dubai's Robothon 2025 Repository

### Team Members

- Judhi
- Bittu
- Ziad
- Sydney
- Aman

### Project History

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
