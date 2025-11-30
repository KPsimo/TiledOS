import tkinter as tk
from tkinter import ttk

def getText():
    result = {"text": ""}  # container to hold the value

    root = tk.Tk()
    root.geometry("500x500")
    root.configure(bg="#1b1b1b")

    root.tk.call("font", "create", "Outfit", "-family", "resources/outfit.ttf")

    style = ttk.Style(root)
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

    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)

    entry = ttk.Entry(frame, font=("Outfit", 14), justify="center")
    entry.pack(fill="both", expand=True)

    def onEnter(event):
        result["text"] = entry.get()
        root.destroy()  # this ends wait_window()

    root.bind("<Return>", onEnter)
    entry.focus()

    root.wait_window()  # waits until destroy() happens

    return result["text"]