# QR Code Generator

## Description

QR Code Generator is a versatile and user-friendly desktop application that allows users to create QR codes for various purposes. Built with Python and Tkinter, this application provides an intuitive interface for generating QR codes across multiple categories.

## Features

- Generate QR codes for:
  - Personal Information
  - Contact Details
  - Social Media Profiles
  - Website URLs
  - Wi-Fi Network Details
  - Event Information
- User-friendly interface with category-specific input fields
- Input validation to ensure data integrity
- Option to download QR codes as PNG or PDF files
- About page with application information

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/kylesinlynn/qr-code-generator.git
   ```

2. Navigate to the project directory:
   ```
   cd qr-code-generator
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Select a category from the dropdown menu.
3. Fill in the required information in the input fields.
4. Click "Generate QR Code" to create your QR code.
5. Use the "Download PNG" or "Download PDF" buttons to save your QR code.

## Dependencies

- tkinter
- qrcode
- Pillow
- reportlab
- tkcalendar

For specific version requirements, please refer to the `requirements.txt` file.

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

