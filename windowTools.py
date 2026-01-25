import tkinter as tk
from tkinter import ttk
import main

def getText():
    print("\033c", end="")
    main.minimize()
    returnVal = input()
    main.maximize()
    return returnVal