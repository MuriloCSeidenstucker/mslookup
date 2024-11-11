import logging
import os
import threading
from tkinter import Tk, filedialog, ttk
from mslookup.app.core import Core
from mslookup.app.logger_config import configure_logging

class MainWindow:
    def __init__(self, master: Tk) -> None:
        configure_logging()
        self.name = self.__class__.__name__
        logging.info(f'{self.name}: Instantiated.')
        
        self.master = master
        self.core = Core()
        self.file_path = ''
        self.entries = {}
        self.processing = False

        # Fixar o tamanho da janela
        self.master.geometry("300x600")
        self.master.resizable(False, False)
        self.master.title('MSLookup')
        
        style = ttk.Style()
        style.configure("Center.TButton", anchor="center")
        
        # Estilo personalizado para a barra de progresso
        style.configure(
            "TProgressbar",
            thickness=25,  # Aumentar a espessura
            troughcolor="#D3D3D3",  # Cor de fundo da barra
            background="#4CAF50"  # Cor da parte preenchida da barra
        )

        # Criar interface
        self.create_ui(self.master)
        
        # Associar evento global para pressionar "Enter" ao botão focado
        self.master.bind_all('<Return>', self.activate_focused_button)

    def create_ui(self, master):
        # Main Frame
        self.main_frame = ttk.Frame(master=master, name='main_frame')
        self.main_frame.configure(height=600, takefocus=True, width=300)

        # Status label para feedback - largura fixa e quebra de linha
        self.status_label = ttk.Label(self.main_frame, text="", foreground="red", anchor="center", width=250, wraplength=250)
        self.status_label.grid(column=0, row=6, padx=10, pady=10)

        # Componentes de entrada e botões
        self.lblf_sheet = self.create_labelframe(self.main_frame, 'Planilha:', 0)
        self.btn_select = ttk.Button(self.lblf_sheet, text="Selecionar Planilha", style="Center.TButton", command=self.select_file)
        self.btn_select.grid(column=0, ipadx=20, padx=10, row=0, sticky='ew')

        self.entries['prod_type'] = self.create_combobox_labelframe(self.main_frame, 'Tipo de Produto:', 1)
        self.entries['item_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente ao Item:', 2)
        self.entries['desc_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente a Descrição:', 3)
        self.entries['brand_col'] = self.create_entry_labelframe(self.main_frame, 'Nome da coluna referente a Marca:', 4)

        self.btn_process = ttk.Button(self.main_frame, text="Buscar Registros", style="Center.TButton", command=self.start_processing_thread)
        self.btn_process.grid(column=0, ipadx=20, padx=10, row=5, sticky='nsew')
        
        self.btn_select.focus_set()
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            mode="determinate",
            length=250,
            maximum=100,
            style="TProgressbar"
        )
        self.progress_bar.grid(column=0, row=7, padx=10, pady=10)

        # Pack Main Frame
        self.main_frame.pack(anchor="center", expand=True, fill="y", ipadx=10, ipady=10, padx=10, pady=10, side="top")

    def create_labelframe(self, parent, text, row):
        labelframe = ttk.Labelframe(parent, text=text)
        parent.grid_columnconfigure(0, weight=1)
        labelframe.configure(width=300)
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
        options = ['Medicamento']
        combobox = ttk.Combobox(labelframe, values=options, justify='center', state='readonly')  # Definindo state='readonly'
        combobox.set(options[0])
        combobox.grid(column=0, row=0, padx=10, pady=5, sticky='ew')
        labelframe.grid_columnconfigure(0, weight=1)
        return combobox
    
    def activate_focused_button(self, event):
        focused_widget = self.main_frame.focus_get()
        # Verifica se o foco está em um botão e, em caso positivo, ativa o comando do botão
        if isinstance(focused_widget, ttk.Button):
            focused_widget.invoke()
        else:
            # Só inicia uma nova thread se nenhuma estiver em andamento
            if not self.processing:
                self.start_processing_thread()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Planilhas", "*.xls *.xlsx *.xlsm *.csv")])
        if file_path:
            self.file_path = file_path
            file_name = os.path.basename(file_path)  # Extrai apenas o nome do arquivo
            self.status_label.config(text=f"Arquivo Selecionado: {file_name}", foreground="green")
            logging.info(f'{self.name}: File selected -> {file_name}')
        else:
            self.status_label.config(text="Nenhum arquivo selecionado.", foreground="red")
            logging.warning(f'{self.name}: File selection canceled.')

    def validate_entries(self):
        if not self.file_path:
            self.status_label.config(text="Por favor, selecione um arquivo primeiro.", foreground="red")
            logging.warning(f'{self.name}: Validation failed -> no file selected.')
            return False
        
        # Mensagens descritivas para cada campo obrigatório
        required_fields = {
            'prod_type': "O tipo de produto não pode estar vazio.",
            'item_col': "O nome da coluna referente ao item não pode estar vazio.",
            'desc_col': "O nome da coluna referente à descrição não pode estar vazio.",
            'brand_col': "O nome da coluna referente à marca não pode estar vazio."
        }

        for key, message in required_fields.items():
            if not self.entries[key].get():
                self.status_label.config(text=message, foreground="red")
                logging.warning(f'{self.name}: Validation failed -> {message}')
                return False

        self.status_label.config(text="Processando...", foreground="blue")
        logging.info(f'{self.name}: Validation successful.')
        return True

    def collect_entry_data(self):
        products_type = 'medicine' if self.entries['prod_type'].get() == 'Medicamento' else ''
        entry_data = {
            'file_path': self.file_path,
            'products_type': products_type,
            'item_col': self.entries['item_col'].get().strip(),
            'desc_col': self.entries['desc_col'].get().strip(),
            'brand_col': self.entries['brand_col'].get().strip()
        }
        
        logging.debug(f'{self.name}: Collected entry data -> {entry_data}')
        return entry_data

    def start_processing_thread(self):
        if self.validate_entries():
            self.processing = True # Atualiza para indicar que o processamento está em andamento
            self.set_interface('disabled')  # Desativar todos os elementos da interface
            self.progress_bar['value'] = 0  # Reset progress bar to 0%
            logging.info(f'{self.name}: Starting processing thread.')
            threading.Thread(target=self.get_data).start()
            
    def set_interface(self, state: str) -> None:
        self.btn_process.config(state=state)
        self.btn_select.config(state=state)
        for entry in self.entries.values():
            entry.config(state=state)
        logging.debug(f'{self.name}: Interface set to {state}.')

    def get_data(self):
        entry_data = self.collect_entry_data()
        
        try:
            # Chamada ao backend
            self.core.execute(entry_data, self.update_progress)  # Passa update_progress como callback
            self.update_status("Busca concluída com sucesso!\nOs PDFs encontrados foram salvos na pasta DOWNLOADS", "green")
            logging.info(f'{self.name}: Data processing completed successfully.')
        except Exception as e:
            self.update_status(f"Erro ao buscar registros: {e}", "red")
            logging.error(f'{self.name}: Error during data processing', exc_info=True)
        finally:
            self.processing = False  # Atualiza para indicar que o processamento terminou
            self.set_interface('normal')  # Reativar todos os elementos da interface
            logging.info(f'{self.name}: Data processing finished.')
            
    def update_progress(self, percent_complete):
        # Atualiza a barra de progresso e status_label
        self.progress_bar['value'] = percent_complete
        if percent_complete < 20:
            self.status_label.config(text=f"Processando dados da planilha... {int(percent_complete)}%")
        elif percent_complete >= 20 and percent_complete < 60:
            self.status_label.config(text=f"Buscando registros... {int(percent_complete)}%")
        elif percent_complete >= 60 and percent_complete < 95:
            self.status_label.config(text=f"Tentando obter PDFs... {int(percent_complete)}%")
        else:
            self.status_label.config(text=f"Gerando {int(percent_complete)}%")
        self.main_frame.update_idletasks()

    def update_status(self, message, color):
        # Atualiza a status_label na thread principal usando o método `after`
        self.status_label.after(0, lambda: self.status_label.config(text=message, foreground=color))
        logging.debug(f'{self.name}: Status updated - {message}')

    def run(self):
        self.master.mainloop()
        logging.info(f'{self.name}: Closing interface.')
