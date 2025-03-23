import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QFileDialog, QListWidget, QMessageBox, 
                              QTabWidget, QLabel)
from PySide6.QtCore import Qt
from PyPDF2 import PdfMerger
import fitz  # PyMuPDF
import os
from PIL import Image
import io

class PDFToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Tools")
        self.setGeometry(100, 100, 600, 400)

        # Main widget and tab widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Merger Tab
        self.merger_tab = QWidget()
        self.setup_merger_tab()
        self.tabs.addTab(self.merger_tab, "PDF Merger")

        # Compressor Tab
        self.compressor_tab = QWidget()
        self.setup_compressor_tab()
        self.tabs.addTab(self.compressor_tab, "PDF Compressor")

        # Image to PDF Tab
        self.image_to_pdf_tab = QWidget()
        self.setup_image_to_pdf_tab()
        self.tabs.addTab(self.image_to_pdf_tab, "Image to PDF")

    def setup_merger_tab(self):
        layout = QVBoxLayout()
        self.merger_tab.setLayout(layout)

        self.pdf_list = QListWidget()
        self.pdf_list.setDragDropMode(QListWidget.InternalMove)
        self.pdf_list.model().rowsMoved.connect(self.update_pdf_order)
        layout.addWidget(self.pdf_list)

        self.add_button = QPushButton("Add PDFs")
        self.add_button.clicked.connect(self.add_pdfs)
        layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_pdf)
        layout.addWidget(self.remove_button)

        self.merge_button = QPushButton("Merge PDFs")
        self.merge_button.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.merge_button)

        self.pdf_files = []

    def setup_compressor_tab(self):
        layout = QVBoxLayout()
        self.compressor_tab.setLayout(layout)

        self.label = QLabel("Select a PDF file to compress")
        layout.addWidget(self.label)
        
        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.select_button)
        
        self.compress_button = QPushButton("Compress and Save")
        self.compress_button.clicked.connect(self.compress_pdf)
        self.compress_button.setEnabled(False)
        layout.addWidget(self.compress_button)
        
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

    def setup_image_to_pdf_tab(self):
        layout = QVBoxLayout()
        self.image_to_pdf_tab.setLayout(layout)

        self.image_list = QListWidget()
        self.image_list.setDragDropMode(QListWidget.InternalMove)
        self.image_list.model().rowsMoved.connect(self.update_image_order)
        layout.addWidget(self.image_list)

        self.add_image_button = QPushButton("Add Images")
        self.add_image_button.clicked.connect(self.add_images)
        layout.addWidget(self.add_image_button)

        self.remove_image_button = QPushButton("Remove Selected")
        self.remove_image_button.clicked.connect(self.remove_image)
        layout.addWidget(self.remove_image_button)

        self.convert_button = QPushButton("Convert to PDF")
        self.convert_button.clicked.connect(self.convert_to_pdf)
        layout.addWidget(self.convert_button)

        self.image_files = []

    # Merger Functions
    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.pdf_list.addItem(file)

    def remove_pdf(self):
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            index = self.pdf_list.row(item)
            self.pdf_list.takeItem(index)
            self.pdf_files.pop(index)

    def update_pdf_order(self):
        new_order = []
        for i in range(self.pdf_list.count()):
            new_order.append(self.pdf_list.item(i).text())
        self.pdf_files = new_order

    def merge_pdfs(self):
        if len(self.pdf_files) < 2:
            QMessageBox.warning(self, "Error", "Please add at least 2 PDFs to merge")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )
        
        if not output_file:
            return

        try:
            merger = PdfMerger()
            for pdf_path in self.pdf_files:
                merger.append(pdf_path)
            merger.write(output_file)
            merger.close()
            QMessageBox.information(self, "Success", "PDFs merged successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    # Compressor Functions
    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")
            self.compress_button.setEnabled(True)

    def compress_pdf(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Compressed PDF", "", "PDF Files (*.pdf)"
        )
        
        if save_path:
            original_size = os.path.getsize(self.pdf_path) / 1024  # Size in KB
            
            # Open the PDF
            doc = fitz.open(self.pdf_path)
            
            # Iterate through pages and downscale images
            for page in doc:
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    img_ext = base_image["ext"]
                    
                    # Convert image to PIL for resizing
                    image = Image.open(io.BytesIO(image_bytes))
                    # Reduce image size by 50% for significant size reduction
                    image = image.resize((image.width // 2, image.height // 2), Image.LANCZOS)
                    
                    # Convert back to bytes, using JPEG for lossy compression
                    img_io = io.BytesIO()
                    image.save(img_io, format="JPEG", quality=50, optimize=True)  # Lossy JPEG with moderate quality
                    compressed_image_bytes = img_io.getvalue()
                    
                    # Replace image stream in PDF
                    doc.update_stream(xref, compressed_image_bytes)
            
            # Save the compressed PDF with aggressive optimization
            doc.save(save_path, garbage=4, deflate=True)
            doc.close()
            
            compressed_size = os.path.getsize(save_path) / 1024  # Size in KB
            saved_space = original_size - compressed_size
            
            if saved_space > 0:
                self.result_label.setText(f"Compression saved {saved_space:.2f} KB (Original: {original_size:.2f} KB, Compressed: {compressed_size:.2f} KB)")
            else:
                self.result_label.setText(f"No size reduction (Original: {original_size:.2f} KB, Compressed: {compressed_size:.2f} KB). PDF may be already optimized.")
            
            self.label.setText("Select a PDF file to compress")
            self.compress_button.setEnabled(False)

    # Image to PDF Functions
    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if files:
            for file in files:
                if file not in self.image_files:
                    self.image_files.append(file)
                    self.image_list.addItem(file)

    def remove_image(self):
        selected_items = self.image_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            index = self.image_list.row(item)
            self.image_list.takeItem(index)
            self.image_files.pop(index)

    def update_image_order(self):
        new_order = []
        for i in range(self.image_list.count()):
            new_order.append(self.image_list.item(i).text())
        self.image_files = new_order

    def convert_to_pdf(self):
        if not self.image_files:
            QMessageBox.warning(self, "Error", "Please add at least one image to convert")
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )
        
        if not output_file:
            return

        try:
            # Create a new PDF document
            doc = fitz.open()

            for img_path in self.image_files:
                # Open the image with PIL to get dimensions
                img = Image.open(img_path)
                width, height = img.size

                # Create a new page with dimensions matching the image
                page = doc.new_page(width=width, height=height)

                # Insert the image into the page
                page.insert_image(page.rect, filename=img_path)

            # Save the PDF
            doc.save(output_file)
            doc.close()

            QMessageBox.information(self, "Success", "Images converted to PDF successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = PDFToolsApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
