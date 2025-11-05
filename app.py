import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import shutil
from pdf2image import convert_from_path
from PIL import Image, ImageTk

class ChessPuzzleBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Puzzle Book Generator")
        self.root.geometry("1300x900")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)

        # Set window icon if queen.ico exists
        if os.path.exists("queen.ico"):
            self.root.iconbitmap("queen.ico")

        # --- Styles ---
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('.', background='#1e1e1e', foreground='white', font=('Helvetica', 12))
        style.map('TButton', background=[('active', '#333333')], foreground=[('active', 'white')])
        style.map('TCheckbutton', background=[('active', '#1e1e1e')], foreground=[('active', 'white')])

        # Main frame
        self.main_frame = tk.Frame(root, bg="#1e1e1e", bd=0, highlightthickness=0)
        self.main_frame.pack(fill="both", expand=True)

        # Left control panel
        self.control_frame = tk.Frame(self.main_frame, bg="#1e1e1e", width=350, bd=0, highlightthickness=0)
        self.control_frame.pack(side="left", fill="y", padx=20, pady=20)

        # Right PDF preview panel
        self.preview_frame = tk.Frame(self.main_frame, bg="#1e1e1e", bd=0, highlightthickness=0)
        self.preview_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # --- Controls ---
        tk.Label(self.control_frame, text="Chess Puzzle Book", font=("Helvetica", 18, "bold"),
                 bg="#1e1e1e", fg="white").pack(pady=10)

        tk.Label(self.control_frame, text="Puzzles per page:", bg="#1e1e1e", fg="white").pack(pady=5)
        self.per_page_var = tk.StringVar(value="9")
        per_page_options = ["1", "2", "4", "6", "9"]
        ttk.OptionMenu(self.control_frame, self.per_page_var, *per_page_options).pack(pady=5)

        tk.Label(self.control_frame, text="Filter by Difficulty:", bg="#1e1e1e", fg="white").pack(pady=5)
        self.difficulty_var = tk.StringVar(value="")
        difficulty_options = ["", "Easy", "Medium", "Hard"]
        ttk.OptionMenu(self.control_frame, self.difficulty_var, *difficulty_options).pack(pady=5)

        self.shuffle_var = tk.BooleanVar()
        ttk.Checkbutton(self.control_frame, text="Shuffle puzzles", variable=self.shuffle_var).pack(pady=5)

        ttk.Button(self.control_frame, text="Generate Puzzle Book", command=self.generate_puzzle_book).pack(pady=20)
        ttk.Button(self.control_frame, text="Preview PDF", command=self.update_preview).pack(pady=5)

        # PDF preview canvas
        self.canvas = tk.Canvas(
            self.preview_frame,
            bg="#1e1e1e",
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind resize event
        self.preview_frame.bind("<Configure>", lambda event: self.update_preview())

        self.current_image = None
        self.poppler_path = self.find_poppler()

    def find_poppler(self):
        """Try to auto-detect Poppler install path."""
        # Check PATH
        pdftoppm = shutil.which("pdftoppm")
        if pdftoppm:
            return os.path.dirname(pdftoppm)

        # Common Windows locations
        guesses = [
            r"C:\Program Files\poppler-23.11.0\Library\bin",
            r"C:\Program Files\poppler-0.68.0\bin",
            r"C:\poppler\bin"
        ]
        for path in guesses:
            if os.path.exists(os.path.join(path, "pdftoppm.exe")):
                return path

        return None

    def generate_puzzle_book(self):
        """Generate PDF and update preview."""
        per_page = self.per_page_var.get()
        difficulty = self.difficulty_var.get()
        shuffle = self.shuffle_var.get()

        json_file = "puzzles.json"
        pdf_file = "puzzle_book.pdf"

        command = [sys.executable, "generator.py", json_file, pdf_file, "--per-page", per_page]
        if difficulty:
            command.extend(["--filter", difficulty])
        if shuffle:
            command.append("--shuffle")

        try:
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", f"Puzzle book '{pdf_file}' generated successfully.")
            self.update_preview()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to generate puzzle book:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")

    def update_preview(self):
        """Render first page of PDF as true A4 inside frame, or outline if empty."""
        pdf_file = "puzzle_book.pdf"
        frame_width = self.preview_frame.winfo_width()
        frame_height = self.preview_frame.winfo_height()

        a4_ratio = 595 / 842
        if frame_width <= 0 or frame_height <= 0:
            return

        if frame_width / frame_height > a4_ratio:
            new_height = frame_height
            new_width = int(new_height * a4_ratio)
        else:
            new_width = frame_width
            new_height = int(new_width / a4_ratio)

        x0 = (frame_width - new_width) // 2
        y0 = (frame_height - new_height) // 2

        self.canvas.delete("all")

        if os.path.exists(pdf_file) and self.poppler_path:
            try:
                pages = convert_from_path(
                    pdf_file,
                    dpi=100,
                    first_page=1,
                    last_page=1,
                    poppler_path=self.poppler_path
                )
                img = pages[0].resize((new_width, new_height), Image.LANCZOS)
                self.current_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(x0, y0, anchor="nw", image=self.current_image)
            except Exception as e:
                self.canvas.create_text(
                    frame_width//2, frame_height//2,
                    text=f"⚠ Could not preview PDF:\n{e}",
                    fill="red", font=("Helvetica", 14), justify="center"
                )
        else:
            # Friendly message if Poppler missing
            if not self.poppler_path:
                self.canvas.create_text(
                    frame_width//2, frame_height//2,
                    text="⚠ Poppler not found!\nDownload from: \nhttps://github.com/oschwartz10612/poppler-windows/releases/",
                    fill="red", font=("Helvetica", 14), justify="center"
                )

        # Always draw A4 outline
        self.canvas.create_rectangle(
            x0, y0, x0 + new_width, y0 + new_height,
            outline="white",
            width=2
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessPuzzleBookApp(root)
    root.mainloop()
