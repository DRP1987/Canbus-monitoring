# CAN Bus Monitoring Application

A comprehensive Python application for monitoring CAN bus signals using PCAN drivers and PyQt5. This application provides automatic baud rate detection, configurable signal monitoring, and real-time message logging.

## Features

- **Automatic Baud Rate Detection**: Automatically detects the correct CAN bus baud rate (125k, 250k, 500k, 1000k)
- **Configuration Management**: Load and select from multiple monitoring configurations via JSON
- **Real-time Signal Monitoring**: Visual LED indicators showing signal match status (green = match, red = no match)
- **Two Signal Matching Types**:
  - **Exact Match**: Matches specific CAN ID with exact data pattern
  - **Range Match**: Matches specific CAN ID with data byte value within a specified range
- **Live CAN Bus Logging**: Real-time display of all CAN messages with timestamp, ID, and data
- **User-Friendly GUI**: Clean PyQt5 interface with tabbed layout

## Prerequisites

### Hardware
- PCAN USB interface device (e.g., PCAN-USB, PEAK-System)
- CAN bus connection with active traffic

### Software
- Python 3.8 or higher
- PCAN drivers installed on your system

#### Installing PCAN Drivers

**Windows:**
1. Download PCAN drivers from [PEAK-System](https://www.peak-system.com/Drivers.523.0.html?&L=1)
2. Install the PCAN-Basic driver package
3. Restart your computer

**Linux:**
1. Install SocketCAN and PCAN driver:
   ```bash
   sudo apt-get install can-utils
   sudo modprobe peak_usb
   ```

**macOS:**
1. Download and install PCAN drivers from [PEAK-System](https://www.peak-system.com/Drivers.523.0.html?&L=1)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DRP1987/Canbus-monitoring.git
   cd Canbus-monitoring
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python main.py
```

### Application Workflow

1. **Baud Rate Detection Screen**
   - Click "Detect Baud Rate" to automatically scan for the correct baud rate
   - The application will test common rates: 125k, 250k, 500k, 1000k
   - Once detected, click "Confirm" to proceed

2. **Configuration Selection Screen**
   - Select a monitoring configuration from the list
   - Click "Load Configuration" to start monitoring

3. **Monitoring Screen**
   - **Signal Status Tab**: Shows each configured signal with LED indicator
     - Green LED: Signal matched (CAN ID exists and data matches criteria)
     - Red LED: Signal not matched
   - **CAN Bus Log Tab**: Displays all received CAN messages in real-time
     - Format: `Timestamp | CAN ID | Data bytes`
   - Click "Clear Log" to clear the message log

## Configuration File

### Structure

The application uses `configurations.json` to define monitoring configurations. Each configuration contains multiple signals to monitor.

### Example Configuration

```json
{
  "configurations": [
    {
      "name": "Configuration 1",
      "signals": [
        {
          "name": "Signal 1",
          "can_id": "0x123",
          "match_type": "exact",
          "data": [1, 2, 3, 4, 5, 6, 7, 8]
        },
        {
          "name": "Signal 2",
          "can_id": "0x456",
          "match_type": "range",
          "data_byte_index": 0,
          "min_value": 10,
          "max_value": 50
        }
      ]
    }
  ]
}
```

### Signal Types

#### Exact Match Signal
Matches when CAN ID and all data bytes match exactly.

```json
{
  "name": "Signal Name",
  "can_id": "0x123",
  "match_type": "exact",
  "data": [1, 2, 3, 4, 5, 6, 7, 8]
}
```

#### Range Match Signal
Matches when CAN ID exists and a specific data byte is within the defined range.

```json
{
  "name": "Signal Name",
  "can_id": "0x456",
  "match_type": "range",
  "data_byte_index": 0,
  "min_value": 10,
  "max_value": 50
}
```

### Adding Custom Configurations

1. Edit `configurations.json`
2. Add a new configuration object to the `configurations` array
3. Define signals with appropriate match types
4. Save the file and restart the application

## Project Structure

```
canbus-monitoring/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Documentation
├── configurations.json              # Signal configurations
├── gui/
│   ├── __init__.py
│   ├── main_window.py              # Main application window
│   ├── baudrate_screen.py          # Baud rate detection screen
│   ├── config_selection_screen.py  # Configuration selection screen
│   ├── monitoring_screen.py        # Signal monitoring with tabs
│   └── widgets.py                  # Custom widgets (LED indicator)
├── canbus/
│   ├── __init__.py
│   ├── pcan_interface.py           # PCAN driver interface
│   └── signal_matcher.py           # Signal matching logic
└── config/
    ├── __init__.py
    └── config_loader.py            # JSON configuration loader
```

## Troubleshooting

### Issue: "Failed to connect to CAN bus"
**Solution:**
- Ensure PCAN device is properly connected to USB
- Check that PCAN drivers are installed correctly
- Verify CAN bus has proper termination (120Ω resistors)
- Try reconnecting the PCAN device

### Issue: "Baud rate detection failed"
**Solution:**
- Ensure there is active CAN traffic on the bus
- Check physical connections to CAN bus
- Verify bus termination is correct
- Try manually connecting at a known baud rate by modifying the code

### Issue: "Configuration file not found"
**Solution:**
- Ensure `configurations.json` exists in the same directory as `main.py`
- Check file permissions
- Verify JSON syntax is correct

### Issue: "No configurations found"
**Solution:**
- Open `configurations.json` and verify it contains valid configurations
- Check JSON syntax using a JSON validator
- Ensure the file structure matches the example above

### Issue: Python package import errors
**Solution:**
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Ensure you're using Python 3.8 or higher: `python --version`
- Try using a virtual environment

## Development

### Code Style
- Follows PEP 8 Python style guidelines
- Docstrings for all classes and methods
- Type hints for function parameters and returns

### Thread Safety
- GUI updates use Qt signals/slots for thread-safe communication
- CAN message reception runs in a background thread
- Proper synchronization between CAN interface and GUI

## License

This project is open-source and available for modification and distribution.

## Author

DRP1987

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository. 
