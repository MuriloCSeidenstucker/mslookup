from tkinter import Tk, Label

class MainWindow:
    m_window = Tk()
    
    lbl = Label(text='Janela Principal')
    lbl.pack()
    
    m_window.mainloop()