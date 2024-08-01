import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import qrcode
from PIL import Image, ImageTk
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import re
from datetime import datetime
import sys
from tkcalendar import DateEntry

class QRGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("QR Code Generator")
        self.master.geometry("600x700")  # Increased height to accommodate QR code
        self.master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=10, relief="flat", background="#4CAF50", foreground="white")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 12))
        self.style.configure("TEntry", padding=5)

        self.categories = [
            "Personal Information",
            "Contact Details",
            "Social Media",
            "Website URL",
            "Wi-Fi Network",
            "Event Details"
        ]

        self.qr_image = None
        self.create_widgets()

    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # Main tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Generate QR")

        # Category selection
        ttk.Label(self.main_frame, text="Select Category:").pack(pady=10)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.main_frame, textvariable=self.category_var, values=self.categories, state="readonly")
        self.category_dropdown.pack(pady=5)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.update_input_fields)

        # Input frame
        self.input_frame = ttk.Frame(self.main_frame, padding="10")
        self.input_frame.pack(pady=10, fill="x", padx=20)

        # QR Code display
        self.qr_frame = ttk.Frame(self.main_frame)
        self.qr_frame.pack(pady=10, expand=True, fill="both")  # Allow QR frame to expand
        self.qr_label = ttk.Label(self.qr_frame)
        self.qr_label.pack(expand=True)  # Center the QR code vertically

        # Generate button
        self.generate_button = ttk.Button(self.main_frame, text="Generate QR Code", command=self.generate_qr)
        self.generate_button.pack(pady=10)

        # Download buttons
        self.download_frame = ttk.Frame(self.main_frame)
        self.download_frame.pack(pady=10)
        self.download_png_button = ttk.Button(self.download_frame, text="Download PNG", command=lambda: self.download_png("qr_code.png"))
        self.download_png_button.pack(side=tk.LEFT, padx=5)
        self.download_pdf_button = ttk.Button(self.download_frame, text="Download PDF", command=lambda: self.download_pdf("qr_code.pdf"))
        self.download_pdf_button.pack(side=tk.LEFT, padx=5)

        # About tab
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="About")
        self.create_about_page()

    def create_about_page(self):
        about_text = """
        QR Code Generator

        Version: 1.0
        
        This application allows you to generate QR codes for various purposes,
        including personal information, contact details, social media profiles,
        website URLs, Wi-Fi network details, and event information.

        Created by: Kyle Sin Lynn (@kylesinlynn)
        GitHub: https://github.com/kylesinlynn
        """
        about_label = ttk.Label(self.about_frame, text=about_text, wraplength=500, justify="center")
        about_label.pack(expand=True, fill="both", padx=20, pady=20)

    def update_input_fields(self, event=None):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        category = self.category_var.get()
        self.input_fields = {}

        if category == "Personal Information":
            fields = [("Name", self.validate_name), ("Date of Birth", self.validate_date), ("Address", self.validate_address)]
        elif category == "Contact Details":
            fields = [("Name", self.validate_name), ("Phone", self.validate_phone), ("Email", self.validate_email)]
        elif category == "Social Media":
            fields = [("Platform", self.validate_platform), ("Username", self.validate_username)]
        elif category == "Website URL":
            fields = [("URL", self.validate_url)]
        elif category == "Wi-Fi Network":
            fields = [("SSID", self.validate_ssid), ("Password", self.validate_password), ("Security Type", self.validate_security_type)]
        elif category == "Event Details":
            fields = [("Event Name", self.validate_event_name), ("Date", self.validate_date), ("Time", self.validate_time), ("Location", self.validate_location)]

        for field, validator in fields:
            ttk.Label(self.input_frame, text=field).pack(anchor="w")
            if field == "Date of Birth":
                entry = DateEntry(self.input_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            else:
                entry = ttk.Entry(self.input_frame, width=40, validate="focusout", validatecommand=(self.master.register(validator), '%P'))
            entry.pack(pady=5, fill="x")
            self.input_fields[field] = entry

    def generate_qr(self):
        category = self.category_var.get()
        if not category:
            messagebox.showerror("Error", "Please select a category")
            return

        data = ""
        for field, entry in self.input_fields.items():
            if isinstance(entry, DateEntry):
                value = entry.get_date().strftime('%Y-%m-%d')
            else:
                value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"Please fill in the {field} field")
                return
            data += f"{field}: {value}\n"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Apply a smooth gradient background
        background = Image.new('RGB', qr_image.size, (255, 255, 255))
        for y in range(background.height):
            for x in range(background.width):
                r = int(255 * (1 - y / background.height))
                g = int(200 * (1 - y / background.height))
                b = int(255 * (1 - y / background.height))
                background.putpixel((x, y), (r, g, b))

        # Blend QR code with background
        qr_image = qr_image.convert("RGBA")
        background.paste(qr_image, (0, 0), qr_image)

        self.qr_image = background

        # Display the QR code
        photo = ImageTk.PhotoImage(self.qr_image)
        self.qr_label.config(image=photo)
        self.qr_label.image = photo

    def download_png(self):
        if self.qr_image is None:
            messagebox.showerror("Error", "Please generate a QR code first")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.qr_image.save(file_path, "PNG")
            messagebox.showinfo("Success", f"QR code saved as PNG: {file_path}")

    def download_pdf(self):
        if self.qr_image is None:
            messagebox.showerror("Error", "Please generate a QR code first")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            # Create a PDF with the QR code
            c = canvas.Canvas(file_path, pagesize=letter)
            qr_width, qr_height = self.qr_image.size
            page_width, page_height = letter

            # Calculate position to center the QR code
            x = (page_width - qr_width) / 2
            y = (page_height - qr_height) / 2

            # Save QR image to a temporary file
            temp_image_path = "temp_qr.png"
            self.qr_image.save(temp_image_path, "PNG")

            # Draw the QR code on the PDF
            c.drawImage(temp_image_path, x, y, width=qr_width, height=qr_height)
            c.save()

            # Remove the temporary file
            os.remove(temp_image_path)

            messagebox.showinfo("Success", f"QR code saved as PDF: {file_path}")

    # Validation methods
    def validate_name(self, value):
        if re.match(r'^[A-Za-z\s]{2,50}$', value):
            return True
        messagebox.showerror("Invalid Input", "Name should contain only letters and spaces, 2-50 characters long.")
        return False

    def validate_date(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            messagebox.showerror("Invalid Input", "Date should be in YYYY-MM-DD format.")
            return False

    def validate_address(self, value):
        if 5 <= len(value) <= 100:
            return True
        messagebox.showerror("Invalid Input", "Address should be 5-100 characters long.")
        return False

    def validate_phone(self, value):
        if re.match(r'^\+?1?\d{9,15}$', value):
            return True
        messagebox.showerror("Invalid Input", "Phone number should be 9-15 digits, optionally starting with +.")
        return False

    def validate_email(self, value):
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return True
        messagebox.showerror("Invalid Input", "Please enter a valid email address.")
        return False

    def validate_platform(self, value):
        valid_platforms = ['Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'TikTok']
        if value in valid_platforms:
            return True
        messagebox.showerror("Invalid Input", f"Platform should be one of: {', '.join(valid_platforms)}")
        return False

    def validate_username(self, value):
        if re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
            return True
        messagebox.showerror("Invalid Input", "Username should be 3-30 characters, containing only letters, numbers, and underscores.")
        return False

    def validate_url(self, value):
        if re.match(r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$', value):
            return True
        messagebox.showerror("Invalid Input", "Please enter a valid URL starting with http:// or https://")
        return False

    def validate_ssid(self, value):
        if 1 <= len(value) <= 32:
            return True
        messagebox.showerror("Invalid Input", "SSID should be 1-32 characters long.")
        return False

    def validate_password(self, value):
        if 8 <= len(value) <= 63:
            return True
        messagebox.showerror("Invalid Input", "Wi-Fi password should be 8-63 characters long.")
        return False

    def validate_security_type(self, value):
        valid_types = ['WEP', 'WPA', 'WPA2', 'WPA3']
        if value in valid_types:
            return True
        messagebox.showerror("Invalid Input", f"Security type should be one of: {', '.join(valid_types)}")
        return False

    def validate_event_name(self, value):
        if 3 <= len(value) <= 50:
            return True
        messagebox.showerror("Invalid Input", "Event name should be 3-50 characters long.")
        return False

    def validate_time(self, value):
        if re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', value):
            return True
        messagebox.showerror("Invalid Input", "Time should be in HH:MM format (24-hour).")
        return False

    def validate_location(self, value):
        if 5 <= len(value) <= 100:
            return True
        messagebox.showerror("Invalid Input", "Location should be 5-100 characters long.")
        return False

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()
