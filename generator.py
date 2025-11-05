import json
import argparse
import random
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import chess
import chess.svg
import cairosvg

def load_puzzles(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def draw_puzzle(fen, filename, size=200):
    """Render a chess FEN to PNG."""
    board = chess.Board(fen)
    svg = chess.svg.board(board, size=size)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=filename)

def generate_pdf(puzzles, pdf_file, per_page=9, shuffle=False, difficulty=None):
    if shuffle:
        random.shuffle(puzzles)

    if difficulty:
        puzzles = [p for p in puzzles if p.get("difficulty") == difficulty]

    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    cols = int(per_page ** 0.5)
    rows = per_page // cols
    cell_w = width / cols
    cell_h = height / rows

    for i, puzzle in enumerate(puzzles):
        fen = puzzle["fen"]
        tmpfile = f"temp_{i}.png"
        draw_puzzle(fen, tmpfile, size=int(min(cell_w, cell_h) - 20))

        col = i % cols
        row = (i // cols) % rows
        page = i // per_page

        if i > 0 and i % per_page == 0:
            c.showPage()

        x = col * cell_w + 10
        y = height - (row + 1) * cell_h + 10
        c.drawImage(tmpfile, x, y, width=cell_w-20, height=cell_h-20, preserveAspectRatio=True, anchor='c')

        os.remove(tmpfile)

    c.save()
    print(f"Saved PDF: {pdf_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file")
    parser.add_argument("pdf_file")
    parser.add_argument("--per-page", type=int, default=9)
    parser.add_argument("--filter", type=str, default="")
    parser.add_argument("--shuffle", action="store_true")
    args = parser.parse_args()

    puzzles = load_puzzles(args.json_file)
    generate_pdf(
        puzzles,
        args.pdf_file,
        per_page=args.per_page,
        shuffle=args.shuffle,
        difficulty=args.filter if args.filter else None
    )
