import os
import pickle
import hashlib
import pandas as pd

class CheckpointManager:
    def __init__(self, checkpoint_file: str = 'data_checkpoint.pkl', identifier_file: str = 'data_identifier.pkl'):
        self.checkpoint_file = checkpoint_file
        self.identifier_file = identifier_file

    def generate_identifier(self, df: pd.DataFrame) -> str:
        return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()

    def save_checkpoint(self, data, identifier):
        with open(self.checkpoint_file, 'wb') as f:
            pickle.dump({'data': data, 'identifier': identifier}, f)
        with open(self.identifier_file, 'w') as f:
            f.write(identifier)

    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_file) and os.path.exists(self.identifier_file):
            with open(self.identifier_file, 'r') as f:
                saved_identifier = f.read()
            with open(self.checkpoint_file, 'rb') as f:
                checkpoint = pickle.load(f)
            return checkpoint, saved_identifier
        return {'data': []}, None

    def delete_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
        if os.path.exists(self.identifier_file):
            os.remove(self.identifier_file)
