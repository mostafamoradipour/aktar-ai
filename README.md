# Aktar AI

Aktar AI is a Python orchestration package for multi-camera video analytics. Its modules coordinate video streaming, object detection, recognition, tracking, optional camera-to-world mapping, and Kafka output.

## Features

- Configurable processing pipeline for video streams.
- Detection, recognition, and tracking stages that can be enabled independently.
- Optional mapping using camera calibration and point correspondences.
- Heatmap and warning-zone settings in the runtime configuration.
- Optional Kafka message production.
- YAML-based configuration selected by profile.

## Requirements

The project targets a Linux environment and depends on the packages listed in `requirements.txt`. Some dependencies, including PyGObject and PyCairo, require operating-system development libraries. GPU inference also requires compatible drivers, CUDA, and model runtimes.

Install dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For native dependencies such as PyGObject, install the appropriate system packages for your distribution before installing Python requirements.

## Configuration

Edit `config.yaml` before running the application. The entry point selects the profile named by the top-level `user` value, then passes that profile's `ai` configuration to the orchestrator.

Configure stream URLs, model weight paths, calibration files, Kafka broker/topic, and tracking settings for your environment. The committed example configuration contains deployment-specific paths and stream addresses; replace them with values you are authorized to use. Do not commit credentials or private endpoints.

## Run

From the repository root, after configuring the required models and services:

```bash
python app.py
```

The orchestrator expects its configured streams and model/calibration files to be reachable. Kafka output also requires a running broker when enabled.

## Package build

The project includes a Cython-based `setup.py`. To build a wheel in an environment with the required build dependencies:

```bash
python setup.py bdist_wheel
```

## Project structure

- `app.py`: loads the selected YAML profile and starts the orchestrator.
- `aktarai/orchestrator.py`: coordinates processing and outputs.
- `aktarai/detection/`, `recognition/`, `tracking/`: analytics modules.
- `aktarai/streaming/`: video stream handling.
- `aktarai/mapping/`: camera mapping utilities.
- `config.yaml`: runtime profiles and pipeline configuration.
- `changelog.md`: release history.

## License

No license file is currently listed. Contact the repository owner before reusing or redistributing this code.
