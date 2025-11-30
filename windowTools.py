import tkinter as tk
from tkinter import ttk

class MinimalEditor(tk.Toplevel):
    def __init__(self, master=None, width=400, height=120, fontPath="resources/outfit.ttf"):
        super().__init__(master)
        
        self.title("minimal editor")
        self.geometry(f"{width}x{height}")
        self.configure(bg="#1b1b1b")

        # register font
        try:
            self.tk.call("font", "create", "Outfit", "-family", fontPath)
        except tk.TclError:
            pass  # fallback if font fails

        # style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#000000")
        style.configure(
            "TEntry",
            fieldbackground="#000000",
            foreground="#ffffff",
            insertcolor="#ffffff",
            borderwidth=0,
            padding=10
        )

        # frame
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        # entry (main element)
        self.entry = ttk.Entry(frame, font=("Outfit", 14), justify="center")
        self.entry.pack(fill="both", expand=True)

    def getText(self):
        return self.entry.get()

    def setText(self, text):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)