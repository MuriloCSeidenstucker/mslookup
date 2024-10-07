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
        
        # Main Frame Start
        self.frame_main = ttk.Frame(master, name="frame_main")
        self.frame_main.configure(height=480, takefocus=True, width=560)
        
        # Label_Sheet
        self.LblF_Sheet = ttk.Labelframe(self.frame_main, name="lblf_sheet")
        self.LblF_Sheet.configure(
            borderwidth=5,
            height=50,
            text='labelframe1',
            width=200)
        label1 = ttk.Label(self.LblF_Sheet)
        label1.configure(text='file_path:')
        label1.grid(column=0, row=0)
        self.button2 = ttk.Button(self.LblF_Sheet)
        self.button2.configure(text='button2', command=self.select_file)
        self.button2.grid(column=1, ipadx=10, padx=10, row=0)
        self.LblF_Sheet.grid(column=0, ipady=10, pady=10, row=0)
        self.LblF_Sheet.grid_anchor("center")
        
        # Label Item
        self.LblF_ItemCol = ttk.Labelframe(
            self.frame_main, name="lblf_itemcol")
        self.LblF_ItemCol.configure(
            borderwidth=5,
            height=50,
            text='labelframe2',
            width=200)
        label2 = ttk.Label(self.LblF_ItemCol)
        label2.configure(text='item_col:')
        label2.grid(column=0, row=0)
        self.entry5 = ttk.Entry(self.LblF_ItemCol)
        self.entry5.grid(column=1, ipadx=20, padx=10, row=0)
        self.LblF_ItemCol.grid(column=0, ipady=10, pady=10, row=2)
        self.LblF_ItemCol.grid_anchor("center")
        
        # Label Description
        self.LblF_DescCol = ttk.Labelframe(
            self.frame_main, name="lblf_desccol")
        self.LblF_DescCol.configure(
            borderwidth=5,
            height=50,
            text='labelframe3',
            width=200)
        label3 = ttk.Label(self.LblF_DescCol)
        label3.configure(
            cursor="arrow",
            justify="left",
            state="normal",
            text='desc_col:')
        label3.grid(column=0, row=0)
        self.entry6 = ttk.Entry(self.LblF_DescCol)
        self.entry6.grid(column=1, ipadx=20, padx=10, row=0)
        self.LblF_DescCol.grid(column=0, ipady=10, pady=10, row=3)
        self.LblF_DescCol.grid_anchor("center")
        
        # Label Brand
        self.LblF_BrandCol = ttk.Labelframe(
            self.frame_main, name="lblf_brandcol")
        self.LblF_BrandCol.configure(
            borderwidth=5,
            height=50,
            text='labelframe4',
            width=200)
        label4 = ttk.Label(self.LblF_BrandCol)
        label4.configure(justify="left", state="normal", text='brand_col:')
        label4.grid(column=0, row=0)
        self.entry7 = ttk.Entry(self.LblF_BrandCol)
        self.entry7.grid(column=1, ipadx=20, padx=10, row=0)
        self.LblF_BrandCol.grid(column=0, ipady=10, pady=10, row=4)
        self.LblF_BrandCol.grid_anchor("center")
        
        # Label Main Button
        self.LblF_ProcessBtn = ttk.Labelframe(
            self.frame_main, name="lblf_processbtn")
        self.LblF_ProcessBtn.configure(
            borderwidth=5, height=50, text='labelframe5', width=200)
        self.button1 = ttk.Button(self.LblF_ProcessBtn)
        self.button1.configure(text='button1', command=self.get_data)
        self.button1.pack(anchor="center", expand=True, side="top")
        self.LblF_ProcessBtn.grid(column=0, ipady=10, pady=10, row=5)
        
        # Label Type
        self.LblF_Type = ttk.Labelframe(self.frame_main, name="lblf_type")
        self.LblF_Type.configure(
            borderwidth=5,
            height=50,
            text='labelframe2',
            width=200)
        label5 = ttk.Label(self.LblF_Type)
        label5.configure(text='prod_type:')
        label5.grid(column=0, row=0)
        self.entry1 = ttk.Entry(self.LblF_Type)
        self.entry1.configure(state="normal")
        self.entry1.grid(column=1, ipadx=20, padx=10, row=0)
        self.LblF_Type.grid(column=0, ipady=10, pady=10, row=1)
        self.LblF_Type.grid_anchor("center")
        
        # Main Frame End
        self.frame_main.pack(
            anchor="center",
            expand=True,
            fill="y",
            ipadx=10,
            ipady=10,
            padx=10,
            pady=10,
            side="top")
        self.frame_main.grid_anchor("center")

        # Main widget
        self.mainwindow = self.frame_main
        
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
