# GitHooker

GitHooker is a simple service to manage git web hooks. It can run commands base on changes in repository

## Requirements

- Python 3.11+ (Since it uses `tomllib`)
- Systemd (optional)

## Installation

1. Create a virtual environment
   ```bash python3.11 -m venv venv```
2. Activate the virtual environment, install the requirements and exit
    ```
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    ```
3. Copy `config.toml.example` to `config.toml` and edit it where needed
4. Copy `githooker.service-example` to `githooker.service` and edit it where needed
5. Copy the service file to systemd directory and enable it
    ```
    sudo cp githooker.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable githooker
    sudo systemctl start githooker
    ```
