from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import messagebox
import os

def export_report(filename, content):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, "Mental Health Group Report")
        y = 720
        for line in content:
            c.drawString(100, y, line)
            y -= 20
        c.save()
        messagebox.showinfo("Success", f"Report successfully exported to {os.path.abspath(filename)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export report: {e}")