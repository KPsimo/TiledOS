from windowTools import MinimalEditor
import tkinter as tk

root = tk.Tk()
root.withdraw()   # hide main window if you don't need it

editor = MinimalEditor(master=root)

print("Initial text in editor:", editor.getText())

root.mainloop()
