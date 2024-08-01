# QR Code Generator

## Description
A simple PyQt5 application to generate QR codes for various categories like personal information, contact details, and more.

## Features
- Generate QR codes for different data types
- Save QR codes as PNG or PDF
- User-friendly GUI

## Installation
Download the executable from the [releases page](https://github.com/kylesinlynn/qrcode-generator/releases).

## Usage
1. Select a category.
2. Fill in the required information.
3. Generate the QR code and save it as needed.

## Contact
For issues or suggestions, please contact [kylesinlynn@gmail.com](mailto:kylesinlynn@gmail.com).

## Building Executable

To create a standalone executable:
1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
2. Create a spec file:
   ```
   pyi-makespec --onefile --windowed main.py
   ```
3. Edit the spec file to include additional data files if needed
4. Build the executable:
   ```
   pyinstaller main.spec
   ```
5. The executable will be generated in the `dist` folder
6. (Optional) Use a tool like Inno Setup to create an installer for the generated executable

