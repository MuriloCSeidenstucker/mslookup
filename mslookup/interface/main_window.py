from tkinter import Tk, filedialog, ttk

from mslookup.app.core import Core

class MainWindow:
    def __init__(self, master: Tk) -> None:
        self.core = Core()
        self.file_path = ''
        self.entries = {}
        
        master.resizable(False, False)
        master.title('MSLookup')
        self.create_ui(master)
    
    def create_ui(self, master):
        # Main Frame Start
        self.main_frame = ttk.Frame(master=master, name='main_frame')
        self.main_frame.configure(height=480, takefocus=True, width=560)
        
        # Cria os componentes da interface
        self.lblf_sheet = self.create_labelframe(self.main_frame, 'Planilha:', 0)
        self.btn_select = ttk.Button(self.lblf_sheet, text="Selecionar Planilha", command=self.select_file)
        self.btn_select.grid(column=0, ipadx=20, padx=10, row=0, sticky='ew')
        
        self.entries['prod_type'] = self.create_combobox_labelframe(self.main_frame, 'Tipo de Produto:', 1)
        self.entries['item_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente ao Item:', 2)
        self.entries['desc_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente a Descrição:', 3)
        self.entries['brand_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente a Marca:', 4)
        
        self.btn_process = ttk.Button(self.main_frame, text="Buscar Registros", command=self.get_data)
        self.btn_process.grid(column=0, ipadx=20, padx=10, row=5, sticky='nsew')
        
        # Main Frame End
        self.main_frame.pack(anchor="center", expand=True, fill="y", ipadx=10, ipady=10, padx=10, pady=10, side="top")
        
    
    def create_labelframe(self, parent, text, row):
        labelframe = ttk.Labelframe(parent, text=text)
        parent.grid_columnconfigure(0, weight=1)
        labelframe.configure(width=200)
        labelframe.grid(column=0, row=row, ipady=10, pady=10, padx=10, sticky='nsew')
        labelframe.grid_columnconfigure(0, weight=1)
        labelframe.grid_rowconfigure(0, weight=1)
        return labelframe
    
    def create_entry_labelframe(self, parent, text, row):
        labelframe = self.create_labelframe(parent, text, row)
        entry = ttk.Entry(labelframe, justify='center')
        entry.grid(column=0, ipadx=20, padx=10, row=0, sticky='ew')
        labelframe.grid_columnconfigure(0, weight=1)
        return entry
    
    def create_combobox_labelframe(self, parent, text, row):
        labelframe = self.create_labelframe(parent, text, row)
        
        # Cria um Combobox com opções pré-definidas
        options = ['Medicamento']
        combobox = ttk.Combobox(labelframe, values=options, justify='center')
        combobox.set(options[0])
        combobox.grid(column=0, row=0, padx=10, pady=5, sticky='ew')
        
        # Expande o Combobox para ocupar o espaço disponível
        labelframe.grid_columnconfigure(0, weight=1)
        
        return combobox  # Retorna o Combobox em vez de um Entry
    
    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            print(f"Arquivo Selecionado: {file_path}")
            
    def get_data(self):
        if not self.file_path:
            print("Nenhum arquivo selecionado!")
            return
        
        # Valida campos
        for key, entry in self.entries.items():
            if not entry.get():
                print(f"{key} está vazio!")
                return
        
        self.btn_process.configure(state='disabled')  # Desabilita botão após submissão
        products_type = 'medicine' if self.entries['prod_type'].get() == 'Medicamento' else ''
        entry = {
            'file_path': self.file_path,
            'products_type': products_type,
            'item_col': self.entries['item_col'].get(),
            'desc_col': self.entries['desc_col'].get(),
            'brand_col': self.entries['brand_col'].get()
        }
        print(entry)
        self.core.execute(entry)
    
    def run(self):
        self.main_frame.mainloop()