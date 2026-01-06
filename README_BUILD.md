# Building Executable

## Requirements

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- All project dependencies installed

## Quick Build

### Windows:
```batch
build_executable.bat
```

### Linux/Mac:
```bash
chmod +x build_executable.sh
./build_executable.sh
```

## Manual Build

```bash
pyinstaller CANBusMonitor.spec
```

## Output

Executable will be in: `dist/CANBusMonitor.exe` (Windows) or `dist/CANBusMonitor` (Linux/Mac)

## Distribution Requirements

Target system must have:
- PCAN drivers installed (https://www.peak-system.com/)
- Windows 10 or later (for Windows builds)

## Troubleshooting

### Issue: Config file not found
- Ensure `configurations.json` exists before building
- Check PyInstaller output for "WARNING: file not found"

### Issue: Logo not showing
- Ensure `assets/logo.png` exists before building
- Check file is included in `datas` section of .spec file

### Issue: PCAN not detected
- PCAN drivers must be installed on target PC
- PCANBasic.dll must be accessible

### Debug Build

To see console output and error messages:

1. Edit `CANBusMonitor.spec`
2. Change `console=False` to `console=True`
3. Rebuild: `pyinstaller CANBusMonitor.spec`
