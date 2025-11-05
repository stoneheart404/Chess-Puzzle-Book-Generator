Windows install notes

1. Create and activate a virtual environment (PowerShell):

python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Upgrade pip and install dependencies:

python -m pip install --upgrade pip; pip install -r requirements.txt

3. Install Poppler (required by pdf2image) on Windows:

- Download poppler for Windows (e.g., from https://github.com/oschwartz10612/poppler-windows/releases).
- Extract and add the `bin` folder to your PATH, or pass the path to `convert_from_path(..., poppler_path='C:\path\to\poppler\bin')` in `app.py`.

4. Run generator directly to create the PDF:

python generator.py puzzles.json puzzle_book.pdf --per-page 9

5. Run the GUI app:

python app.py
