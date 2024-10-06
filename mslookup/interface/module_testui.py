#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from mslookup.app.core import Core


class class_testUI:
    def __init__(self, master=None):
        self.file_path = ''
        self.item_col = ''
        self.desc_col = ''
        self.brand_col = ''
        self.core = Core()
        
        # build ui
        frame1 = ttk.Frame(master)
        frame1.configure(height=285, width=240)
        
        labelframe1 = ttk.Labelframe(frame1)
        labelframe1.configure(
            borderwidth=5,
            height=50,
            text='labelframe1',
            width=200)
        label1 = ttk.Label(labelframe1)
        label1.configure(text='file_path:')
        label1.grid(column=0, row=0)
        button2 = ttk.Button(labelframe1)
        button2.configure(text='button2', command=self.select_file)
        button2.grid(column=1, row=0)
        labelframe1.pack(ipadx=10, padx=10, pady=5, side="top")
        
        labelframe7 = ttk.Labelframe(frame1)
        labelframe7.configure(
            borderwidth=5,
            height=50,
            text='labelframe2',
            width=200)
        label2 = ttk.Label(labelframe7)
        label2.configure(text='item_col:')
        label2.grid(column=0, row=0)
        self.entry5 = ttk.Entry(labelframe7)
        self.entry5.grid(column=1, row=0)
        labelframe7.pack(ipadx=10, padx=10, pady=5, side="top")
        
        labelframe8 = ttk.Labelframe(frame1)
        labelframe8.configure(
            borderwidth=5,
            height=50,
            text='labelframe3',
            width=200)
        label3 = ttk.Label(labelframe8)
        label3.configure(
            cursor="arrow",
            justify="left",
            state="normal",
            text='desc_col:')
        label3.grid(column=0, row=0)
        self.entry6 = ttk.Entry(labelframe8)
        self.entry6.grid(column=1, row=0)
        labelframe8.pack(ipadx=10, padx=10, pady=5, side="top")
        
        labelframe9 = ttk.Labelframe(frame1)
        labelframe9.configure(
            borderwidth=5,
            height=50,
            text='labelframe4',
            width=200)
        label4 = ttk.Label(labelframe9)
        label4.configure(justify="left", state="normal", text='brand_col:')
        label4.grid(column=0, row=0)
        self.entry7 = ttk.Entry(labelframe9)
        self.entry7.grid(column=1, row=0)
        labelframe9.pack(ipadx=10, padx=10, pady=5, side="top")
        
        labelframe10 = ttk.Labelframe(frame1)
        labelframe10.configure(
            borderwidth=5,
            height=50,
            text='labelframe5',
            width=200)
        self.button1 = ttk.Button(labelframe10)
        self.button1.configure(text='button1', command=self.get_data)
        self.button1.pack(side="top")
        labelframe10.pack(ipadx=10, padx=10, pady=5, side="top")
        
        frame1.pack(side="top")

        # Main widget
        self.mainwindow = frame1
        
    def select_file(self):
        file_path = filedialog.askopenfilename()
        
        if file_path:
            self.file_path = file_path
            print(f"Arquivo Selecionado: {file_path}")
            
    def get_data(self):
        self.button1.configure(default='disabled')
        entry = {
            'file_path': self.file_path,
            'products_type': 'medicine',
            'item_col': self.entry5.get(),
            'desc_col': self.entry6.get(),
            'brand_col': self.entry7.get()
        }
        print(entry)
        self.core.execute(entry)

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = class_testUI(root)
    app.run()
