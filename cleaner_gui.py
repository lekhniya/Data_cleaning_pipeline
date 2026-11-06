"""Simple Tkinter app: upload a CSV/Excel file, clean it, download the result.

Run with:  python cleaner_gui.py
Keep this file in the same folder as clean_comments.py.
"""

import time
import tkinter as tk
from tkinter import filedialog, messagebox

from clean_comments import load, process, summary

WINE, AMBER, BLUSH, INK = "#5B1A3A", "#F2A33A", "#FBEDEA", "#2B1220"


class CleanerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customer Comment Cleaner")
        self.geometry("560x460")
        self.configure(bg=BLUSH)
        self.df = None
        self.result = None

        tk.Label(self, text="Customer Input Data Cleaning Pipeline", bg=WINE, fg="white",
                 font=("Lucida Console", 12, "bold"), pady=14).pack(fill="x")
        tk.Frame(self, bg=AMBER, height=4).pack(fill="x")

        body = tk.Frame(self, bg=BLUSH, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        self.file_label = tk.Label(body, text="No file selected", bg=BLUSH, fg=INK,
                                   font=("Lucida Console", 9), anchor="w")
        self.file_label.pack(fill="x", pady=(0, 10))

        self.upload_btn = self._button(body, "1. Upload CSV or Excel file", self.upload)
        self.clean_btn = self._button(body, "2. Clean comments", self.clean, state="disabled")
        self.save_btn = self._button(body, "3. Download cleaned CSV", self.save, state="disabled")

        self.output = tk.Text(body, height=9, bg="white", fg=INK, relief="flat",
                              font=("Lucida Console", 9), state="disabled")
        self.output.pack(fill="both", expand=True, pady=(12, 0))

    def _button(self, parent, text, command, state="normal"):
        btn = tk.Button(parent, text=text, command=command, state=state, bg=AMBER, fg=INK,
                        font=("Lucida Console", 10), relief="flat", pady=8)
        btn.pack(fill="x", pady=4)
        return btn

    def _show(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def upload(self):
        path = filedialog.askopenfilename(filetypes=[("CSV or Excel", "*.csv *.xlsx *.xls")])
        if not path:
            return
        try:
            self.df = load(path)
            if "Comment" not in self.df.columns:
                raise KeyError(f'Column "Comment" not found. Columns: {list(self.df.columns)}')
        except Exception as error:
            messagebox.showerror("Could not load file", str(error))
            self.df = None
            return
        self.file_label.configure(text=path.split("/")[-1].split("\\")[-1])
        self.clean_btn.configure(state="normal")
        self.save_btn.configure(state="disabled")
        self._show(f"Loaded {len(self.df)} rows. Click 'Clean comments'.")

    def clean(self):
        start = time.time()
        self.result = process(self.df)
        self._show(summary(self.result, time.time() - start))
        self.save_btn.configure(state="normal")

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="cleaned_output.csv",
                                            filetypes=[("CSV file", "*.csv")])
        if path:
            self.result.to_csv(path, index=False)
            messagebox.showinfo("Saved", f"Cleaned file saved to:\n{path}")


if __name__ == "__main__":
    CleanerApp().mainloop()
