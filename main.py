#!/usr/bin/env python3
"""
Dr. AppInventor – Static Analysis Tool for MIT App Inventor 2 Projects
Entry point.
"""

import tkinter as tk
from gui.app_gui import DrAppInventorApp

def main():
    root = tk.Tk()
    DrAppInventorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()