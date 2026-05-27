# se_models

FastAPI servers, common Python clients, and ROS2 integration for running GroundingDINO and SAM2.

---

## Repository Structure

```text
se_models/
├── .env                       # Shared port configurations (source of truth)
├── docker-compose.yml         # Compose configuration to start all models
├── pyproject.toml             # Package configuration for local 'src' module
├── models/                    # Model-specific servers, configurations and Docker setup
│   ├── grounding_dino/
│   │   ├── Dockerfile         # Runs FastAPI server internally on port 8080
│   │   └── api.py             # FastAPI server endpoint definitions
│   └── sam2/
│       ├── Dockerfile         # Runs FastAPI server internally on port 8080
│       └── api.py             # FastAPI server endpoint definitions
├── src/                       # Common python client wrappers and types
│   ├── types/                 # Shared Pydantic types for API schemas
│   │   ├── grounding_dino.py
│   │   └── sam2.py
│   ├── grounding_dino_client.py # Client wrapper (verifies /health check on __init__)
│   └── sam2_client.py         # Client wrapper (verifies /health check on __init__)
├── ros2_interface/            # ROS2 workspace
│   └── src/
│       ├── se_models_msgs/    # ROS2 interface package (custom Msg/Srv definitions)
│       │   ├── msg/
│       │   │   ├── BoundingBox.msg
│       │   │   ├── Detection.msg
│       │   │   └── Segmentation.msg
│       │   └── srv/
│       │       ├── GetDetections.srv
│       │       └── GetSegmentation.srv
│       └── se_models/         # ROS2 node package invoking client classes
│           ├── launch/
│           │   └── models.launch.py # Launches all model nodes (reads ports from env)
│           └── se_models/
│               ├── grounding_dino_node.py
│               └── sam2_node.py
└── _test/                     # Standalone Python verification scripts
    ├── test_grounding_dino.py
    └── test_sam2.py
```

---

## Port Sharing and Configuration

A shared `.env` file at the root of the project specifies the host ports that are mapped to the internal container ports (which default to `8080` internally for all models).

Default `.env` settings:
```env
GROUNDING_DINO_PORT=8000
SAM2_PORT=8001
CPU_ONLY=1  # Set to 1 for CPU-only execution, 0 for Nvidia GPU on Linux
```

---

## 1. How to Build and Run Model Dockers

To spin up all model servers (FastAPI) at the same time using Docker Compose:

```bash
# Build and start all model containers
docker compose up --build

# Start in background
docker compose up -d
```

---

## 2. Using it Without ROS (Python Clients)

The `src/` directory is packaged as a standard Python module.

### Installation
First, install the package in editable mode within your virtual environment:
```bash
# Using uv (fastest)
uv pip install -e .

# Or using standard pip
pip install -e .
```

### Direct Python Invocation
You can invoke the models directly in your python scripts using the provided clients:
```python
from src.grounding_dino_client import GroundingDinoClient

# Instantiating automatically runs a health check against the server
client = GroundingDinoClient("http://localhost:8000")

# Run prediction
with open("image.jpg", "rb") as f:
    image_bytes = f.read()

response = client.predict(image_bytes=image_bytes, prompt="person")
for detection in response.detections:
    print(f"Detected {detection.label} with confidence {detection.confidence}")
```

### Running Tests
Execute the standalone test scripts in the `_test` folder:
```bash
python _test/test_grounding_dino.py
python _test/test_sam2.py
```

---

## 3. Using it With ROS 2

You can run the ROS 2 workspace either inside a dedicated ROS 2 Development Docker Container or directly on your host machine (if ROS 2 is installed locally).

### Option A: Using the Docker Development Container (Recommended)

This utilizes the custom ROS 2 development environment defined in `ros2_interface/Dockerfile`.

#### 1. Managing Multiple Docker Compose Files
You have two options to manage the model servers and the ROS 2 container:
* **Independent Stacks (Recommended)**: Run the model servers and the ROS 2 dev container separately. Since the ROS 2 container uses `network_mode: host`, it can seamlessly communicate with the FastAPI servers running on localhost ports `8000`/`8001`:
  ```bash
  # Terminal 1: Spin up model servers
  docker compose up -d

  # Terminal 2: Spin up ROS 2 development container
  docker compose -f docker-compose.ros2.yml up -d
  ```
* **Combined Stack**: Run both compose files together using the `-f` flag to manage them as a single group:
  ```bash
  # Spin up models and ROS 2 container together
  docker compose -f docker-compose.yml -f docker-compose.ros2.yml up -d
  ```

#### 2. Start and Enter the Container
To start the ROS 2 development container (building it if necessary) with your user's exact UID and GID so that files remain writeable:
```bash
# Start the container in the background
UID=$(id -u) GID=$(id -g) docker compose -f docker-compose.ros2.yml up -d --build
UID=$(id -u) GID=$(id -g) ROS2_PROJECTS_DIR=~/projects docker compose -f docker-compose.ros2.yml up -d --build

# Open an interactive shell inside the container as the 'ros' user
docker exec -it ros2_dev bash
```

#### 3. Install the se_models Package
Once inside the container shell, install the package in editable mode:
```bash
sudo pip install -e /home/ros/projects/se_models
```

#### 4. Opening Additional Shell Sessions
If you need to open multiple terminal windows inside the same running container (e.g., to run multiple launch files or CLI commands in parallel), execute this command in a new host terminal window:
```bash
docker exec -it ros2_dev bash
```

#### 5. Building the Workspace Inside the Container
Once inside the container shell:
```bash
# Navigate to the workspace
cd /home/ros/ws

# Build the workspace
colcon build --symlink-install

# Source the setup script
source install/setup.bash
```

#### 5. Launching All Nodes
Within one of your container shell sessions:
```bash
ros2 launch se_models models.launch.py
```

---

### Option B: Local Host Workspace (ROS 2 Installed on Host)

#### Prerequisites
Make sure ROS 2 (e.g. Humble) is installed and sourced in your current host shell.

#### Building the ROS 2 Workspace
```bash
cd ros2_interface
colcon build --symlink-install
source install/setup.zsh
```

#### Launching All Nodes
```bash
# Launch grounding_dino_node and sam2_node
ros2 launch se_models models.launch.py
```
This launcher reads the `.env` file ports at runtime to connect to the active FastAPI servers.


### Calling ROS 2 Services
You can interact with the running nodes via the command line:

- **GroundingDINO (GetDetections)**:
  ```bash
  ros2 service call /get_detections se_models_msgs/srv/GetDetections "{prompt: 'person', box_threshold: 0.35}"
  ```
- **SAM 2 (GetSegmentation)**:
  ```bash
  ros2 service call /get_segmentation se_models_msgs/srv/GetSegmentation "{bboxes_json: '[]'}"
  ```

---

## Guide: How to Add a New Model

Adding a new model to this project follows a structured process to keep the codebase clean and unified:

### Step 1: Create the Server Folder
Create a folder under `models/` (e.g. `models/yolov8/`). Add:
1. **`api.py`**: A FastAPI application. Define a `/health` endpoint returning `{"status": "healthy"}` and your prediction endpoints. Ensure it runs on port `8080`.
2. **`Dockerfile`**: Configure system/CUDA libraries and installation. Ensure it copies `src/` to `/home/${USERNAME}/app/src/` and sets `PYTHONPATH="/home/${USERNAME}/app:${PYTHONPATH}"`. Make sure to use the root of the repository as the docker build context so it has access to copy `src/`.

### Step 2: Define Schemas & Clients in `src/`
1. Create a schema file under `src/types/yolov8.py` containing Pydantic models for request and response formats.
2. In `models/yolov8/api.py`, import the Pydantic schemas from `src.types.yolov8`.
3. Create `src/yolov8_client.py`. Include a class `Yolov8Client` that checks `health` in `__init__` and wraps requests to your API endpoint.

### Step 3: Add to Root Configuration
1. Append the port mapping to `.env` (e.g. `YOLOV8_PORT=8002`).
2. Add the service to `docker-compose.yml` linking target port `8080` to the new environment variable port.

### Step 4: Integrate with ROS 2
1. **Interface definitions (`se_models_msgs`)**: Add any new message (`.msg`) or service (`.srv`) files to `ros2_interface/src/se_models_msgs/msg/` and `srv/` and register them in `CMakeLists.txt`.
2. **ROS 2 Node (`se_models`)**: Create `ros2_interface/src/se_models/se_models/yolov8_node.py` implementing the ROS2 service using your new client class in `src`. Register the entry point in `setup.py`.
3. **Launch file**: Add your node to `ros2_interface/src/se_models/launch/models.launch.py`, passing the URL parameters using `os.getenv('YOLOV8_PORT', '8002')`.
