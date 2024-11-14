class MissingColumnsError(Exception):
    def __init__(self, missing_columns):
        self.missing_columns = missing_columns
        message = f"As seguintes colunas estão ausentes no arquivo: {', '.join(missing_columns)}"
        super().__init__(message)
