import sys
import qrcode
from PIL import Image
import io
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QFileDialog, QMessageBox, QTabWidget, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import re
from datetime import datetime

class QRGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator")
        self.setGeometry(100, 100, 600, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.qr_image = None
        self.create_widgets()

    def create_widgets(self):
        main_layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # Main tab
        self.main_tab = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_tab.setLayout(self.main_layout)
        tab_widget.addTab(self.main_tab, "Generate QR")

        # About tab
        self.about_tab = QWidget()
        about_layout = QVBoxLayout()
        self.about_tab.setLayout(about_layout)
        tab_widget.addTab(self.about_tab, "About")
        self.create_about_page()

        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

        # Category selection
        self.category_label = QLabel("Select Category:")
        self.category_dropdown = QComboBox()
        self.categories = [
            "Select One",  # Placeholder item
            "Personal Information",
            "Contact Details",
            "Social Media",
            "Website URL",
            "Wi-Fi Network",
            "Event Details"
        ]
        self.category_dropdown.addItems(self.categories)
        
        # Disable the first item
        self.category_dropdown.setItemData(0, Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.UserRole)
        self.category_dropdown.setItemData(0, Qt.ItemDataRole.BackgroundRole, Qt.gray)
        self.category_dropdown.setItemData(0, Qt.ItemDataRole.TextColorRole, Qt.gray)
        
        # Set placeholder item
        self.category_dropdown.setCurrentIndex(0)

        self.category_dropdown.currentIndexChanged.connect(self.update_input_fields)

        self.main_layout.addWidget(self.category_label)
        self.main_layout.addWidget(self.category_dropdown)

        # Input frame
        self.input_frame = QFormLayout()
        self.main_layout.addLayout(self.input_frame)

        # QR Code display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.qr_label)

        # Generate button
        self.generate_button = QPushButton("Generate QR Code")
        self.generate_button.clicked.connect(self.generate_qr)
        self.main_layout.addWidget(self.generate_button)

        # Download buttons
        download_layout = QHBoxLayout()
        self.download_png_button = QPushButton("Download PNG")
        self.download_png_button.clicked.connect(self.download_png)
        self.download_pdf_button = QPushButton("Download PDF")
        self.download_pdf_button.clicked.connect(self.download_pdf)
        download_layout.addWidget(self.download_png_button)
        download_layout.addWidget(self.download_pdf_button)
        self.main_layout.addLayout(download_layout)


    def create_about_page(self):
        about_text = """
        QR Code Generator

        Version: 2.0
        
        This application allows you to generate QR codes for various purposes,
        including personal information, contact details, social media profiles,
        website URLs, Wi-Fi network details, and event information.

        Created by: Kyle Sin Lynn (@kylesinlynn)
        GitHub: https://github.com/kylesinlynn
        """
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignCenter)
        self.about_tab.layout().addWidget(about_label)

    def update_input_fields(self):
        category_index = self.category_dropdown.currentIndex()
        
        # Skip updating if the placeholder item is selected
        if category_index == 0:
            return

        # Clear previous input fields
        while self.input_frame.count() > 0:
            item = self.input_frame.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        category = self.category_dropdown.currentText()
        self.input_fields = {}

        fields = {
            "Personal Information": [("Name", self.validate_name), ("Date of Birth", self.validate_date), ("Address", self.validate_address)],
            "Contact Details": [("Name", self.validate_name), ("Phone", self.validate_phone), ("Email", self.validate_email)],
            "Social Media": [("Platform", self.validate_platform), ("Username", self.validate_username)],
            "Website URL": [("URL", self.validate_url)],
            "Wi-Fi Network": [("SSID", self.validate_ssid), ("Password", self.validate_password), ("Security Type", self.validate_security_type)],
            "Event Details": [("Event Name", self.validate_event_name), ("Date", self.validate_date), ("Time", self.validate_time), ("Location", self.validate_location)]
        }

        for field, validator in fields.get(category, []):
            self.input_frame.addRow(QLabel(field), self.create_input_widget(field, validator))


    def generate_qr(self):
        if not self.validate_fields():
            return

        category = self.category_dropdown.currentText()
        data = ""

        for i in range(self.input_frame.rowCount()):
            label_item = self.input_frame.itemAt(i, QFormLayout.LabelRole)
            field_item = self.input_frame.itemAt(i, QFormLayout.FieldRole)

            # Check if label_item and field_item are not None
            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()
                
                if field_widget:
                    value = field_widget.text().strip()
                    if not value:
                        QMessageBox.warning(self, "Error", "Please fill in all fields")
                        return
                    field_label = label_widget.text() if label_widget else "Unknown Field"
                    data += f"{field_label}: {value}\n"
            else:
                print(f"Warning: Label item or Field item at index {i} is None.")

        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            qr_image = qr.make_image(fill='black', back_color='white')

            # Apply a smooth gradient background
            background = Image.new('RGB', qr_image.size, (255, 255, 255))
            for y in range(background.height):
                for x in range(background.width):
                    r = int(255 * (1 - y / background.height))
                    g = int(200 * (1 - y / background.height))
                    b = int(255 * (1 - y / background.height))
                    background.putpixel((x, y), (r, g, b))

            qr_image = qr_image.convert("RGBA")
            background.paste(qr_image, (0, 0), qr_image)

            self.qr_image = background

            # Display the QR code
            with io.BytesIO() as buffer:
                self.qr_image.save(buffer, format="PNG")
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "Failed to load QR code image.")
                else:
                    self.qr_label.setPixmap(pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the QR code: {str(e)}")



    def create_input_widget(self, field, validator):
        entry = QLineEdit()
        if field == "Date of Birth":
            entry.setPlaceholderText("YYYY-MM-DD")
        entry.setObjectName(field)
        return entry

    def validate_fields(self):
        category = self.category_dropdown.currentText()
        fields = {
            "Personal Information": [("Name", self.validate_name), ("Date of Birth", self.validate_date), ("Address", self.validate_address)],
            "Contact Details": [("Name", self.validate_name), ("Phone", self.validate_phone), ("Email", self.validate_email)],
            "Social Media": [("Platform", self.validate_platform), ("Username", self.validate_username)],
            "Website URL": [("URL", self.validate_url)],
            "Wi-Fi Network": [("SSID", self.validate_ssid), ("Password", self.validate_password), ("Security Type", self.validate_security_type)],
            "Event Details": [("Event Name", self.validate_event_name), ("Date", self.validate_date), ("Time", self.validate_time), ("Location", self.validate_location)]
        }

        for i in range(self.input_frame.rowCount()):
            label_item = self.input_frame.itemAt(i, QFormLayout.LabelRole)
            field_item = self.input_frame.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if field_widget:
                    field_label = label_widget.text() if label_widget else "Unknown Field"
                    value = field_widget.text().strip()
                    validator = next((v for f, v in fields.get(category, []) if f == field_label), None)
                    if validator and not validator(value):
                        return False
            else:
                print(f"Warning: Label item or Field item at index {i} is None.")
        return True

    def download_png(self):
        if self.qr_image is None:
            QMessageBox.warning(self, "Error", "Please generate a QR code first")
            return

        # Default filename with date and time
        default_filename = f"qrcode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PNG", default_filename, "PNG files (*.png)")
        if file_path:
            self.qr_image.save(file_path, "PNG")
            QMessageBox.information(self, "Success", f"QR code saved as PNG: {file_path}")

    def download_pdf(self):
        if self.qr_image is None:
            QMessageBox.warning(self, "Error", "Please generate a QR code first")
            return

        # Default filename with date and time
        default_filename = f"qrcode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", default_filename, "PDF files (*.pdf)")
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            qr_width, qr_height = self.qr_image.size
            page_width, page_height = letter

            x = (page_width - qr_width) / 2
            y = (page_height - qr_height) / 2

            temp_image_path = "temp_qr.png"
            self.qr_image.save(temp_image_path, "PNG")

            c.drawImage(temp_image_path, x, y, width=qr_width, height=qr_height)
            c.save()

            os.remove(temp_image_path)

            QMessageBox.information(self, "Success", f"QR code saved as PDF: {file_path}")

    # Validation methods
    def validate_name(self, value):
        if re.match(r'^[A-Za-z\s]{2,50}$', value):
            return True

    # Validation methods
    def validate_name(self, value):
        if re.match(r'^[A-Za-z\s]{2,50}$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Name should contain only letters and spaces, 2-50 characters long.")
        return False

    def validate_date(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Date should be in YYYY-MM-DD format.")
            return False

    def validate_address(self, value):
        if 5 <= len(value) <= 100:
            return True
        QMessageBox.warning(self, "Invalid Input", "Address should be 5-100 characters long.")
        return False

    def validate_phone(self, value):
        if re.match(r'^\+?1?\d{9,15}$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Phone number should be 9-15 digits, optionally starting with +.")
        return False

    def validate_email(self, value):
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Please enter a valid email address.")
        return False

    def validate_platform(self, value):
        valid_platforms = ['Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'TikTok']
        if value in valid_platforms:
            return True
        QMessageBox.warning(self, "Invalid Input", f"Platform should be one of: {', '.join(valid_platforms)}")
        return False

    def validate_username(self, value):
        if re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Username should be 3-30 characters, containing only letters, numbers, and underscores.")
        return False

    def validate_url(self, value):
        if re.match(r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Please enter a valid URL starting with http:// or https://")
        return False

    def validate_ssid(self, value):
        if 1 <= len(value) <= 32:
            return True
        QMessageBox.warning(self, "Invalid Input", "SSID should be 1-32 characters long.")
        return False

    def validate_password(self, value):
        if 8 <= len(value) <= 63:
            return True
        QMessageBox.warning(self, "Invalid Input", "Wi-Fi password should be 8-63 characters long.")
        return False

    def validate_security_type(self, value):
        valid_types = ['WEP', 'WPA', 'WPA2', 'WPA3']
        if value in valid_types:
            return True
        QMessageBox.warning(self, "Invalid Input", f"Security type should be one of: {', '.join(valid_types)}")
        return False

    def validate_event_name(self, value):
        if 3 <= len(value) <= 50:
            return True
        QMessageBox.warning(self, "Invalid Input", "Event name should be 3-50 characters long.")
        return False

    def validate_time(self, value):
        if re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', value):
            return True
        QMessageBox.warning(self, "Invalid Input", "Time should be in HH:MM format (24-hour).")
        return False

    def validate_location(self, value):
        if 5 <= len(value) <= 100:
            return True
        QMessageBox.warning(self, "Invalid Input", "Location should be 5-100 characters long.")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRGeneratorApp()
    window.show()
    sys.exit(app.exec_())
