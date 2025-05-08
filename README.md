# Universal File Converter Mobile App

A cross-platform mobile application built with Python and Kivy for converting files between different formats.

## Features

- Convert images between JPG, PNG, WEBP, BMP, GIF, and PDF formats
- Convert documents between PDF, DOCX, and TXT formats
- Convert data files between CSV, XLSX, JSON, XML, and HTML formats  
- Simple and intuitive user interface
- Progress tracking during conversion
- Cross-platform (Android, iOS, and desktop systems)

## Prerequisites

- Python 3.8 or newer
- Kivy and KivyMD
- Required conversion libraries

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/universal-file-converter.git
   cd universal-file-converter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Generate app icons (optional):
   ```
   python generate_icons.py
   ```

## Development Setup

### Desktop Development

For desktop development and testing, simply run:

```
python run_app.py
```

### Android Development

1. Install Buildozer:
   ```
   pip install buildozer
   ```

2. Initialize Buildozer (if not already done):
   ```
   buildozer init
   ```

3. Update the `buildozer.spec` file with the correct requirements and permissions.

4. Build the APK:
   ```
   buildozer android debug
   ```

5. Install on connected Android device or emulator:
   ```
   buildozer android deploy run
   ```

### iOS Development

For iOS development, you'll need a Mac with Xcode installed:

1. Install the required tools:
   ```
   pip install kivy-ios
   ```

2. Use toolchain to create an iOS project:
   ```
   toolchain build kivy
   toolchain create universal-file-converter .
   ```

3. Open the resulting Xcode project and run on a simulator or device.

## Project Structure

```
universal-file-converter/
├── main.py              # Main application code
├── converters.py        # File conversion logic
├── permissions.py       # Permission handling for Android
├── fileconverter.kv     # Kivy UI design file
├── run_app.py           # Launcher script
├── buildozer.spec       # Android build specification
├── app_icon.svg         # Vector icon source
├── generate_icons.py    # Icon generator script
├── data/                # Generated assets (icons, splash screen)
└── README.md            # This file
```

## Adding New Converters

To add support for new file formats:

1. Update the `FORMAT_MAP` dictionary in `converters.py`
2. Implement the appropriate conversion function
3. Update the conversion logic in the `convert_file` function

## Building for Production

### Android Release Build

```
buildozer android release
```

This will generate an unsigned APK which can be signed for Play Store distribution.

### iOS Release Build

Use Xcode to create a release build and submit to the App Store.

## Troubleshooting

- **Permission issues on Android**: Make sure the app has the necessary permissions in the manifest
- **File not found errors**: Check file paths and ensure storage permissions are granted
- **Conversion failures**: Check the log for specific error messages from the converter functions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.