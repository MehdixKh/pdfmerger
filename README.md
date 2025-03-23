# PDF Tools

A PySide6-based desktop app for managing PDFs with three features: merging PDFs, compressing PDFs, and converting images to PDFs.

## Features

- **PDF Merger**: Merge multiple PDFs with drag-and-drop reordering.
- **PDF Compressor**: Compress PDFs by resizing images (50%) and using lossy JPEG compression (quality 50).
- **Image to PDF**: Convert images (PNG, JPEG, BMP, GIF) to a single PDF with drag-and-drop reordering.

## Setup

1. **Clone/pdfmerger**: Clone or download the project.
2. **Create Virtual Environment**:
   ```bash
   cd path/to/pdfmerger
   python -m venv venv
   ```

3. **Activate Virtual Environment**:
   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the App:
```bash
python pdfmerger.py
```

### Features:
- **PDF Merger**: Add PDFs, reorder, and merge into one.
- **PDF Compressor**: Select a PDF, compress, and save.
- **Image to PDF**: Add images, reorder, and convert to PDF.

## Project Structure
```
pdfmerger/
│
├── venv/                    # Virtual environment
├── pdfmerger.py             # Main script
├── README.md                # Documentation
└── requirements.txt         # Dependencies
```

## License
MIT License. Use, modify, and distribute freely.

