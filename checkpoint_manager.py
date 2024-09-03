import os
import pickle
import hashlib
from typing import Any, Callable, Tuple, Optional

class CheckpointManager:
    def __init__(self, checkpoint_file: str = 'data_checkpoint.pkl', identifier_file: str = 'data_identifier.pkl', hash_func: Optional[Callable[[Any], str]] = None):
        self.checkpoint_file = checkpoint_file
        self.identifier_file = identifier_file
        self.hash_func = hash_func or self.default_hash_func

    def default_hash_func(self, obj: Any) -> str:
        return hashlib.md5(pickle.dumps(obj)).hexdigest()

    def generate_identifier(self, data: Any) -> str:
        return self.hash_func(data)

    def save_checkpoint(self, data: Any, identifier: str):
        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump({'data': data, 'identifier': identifier}, f)
            with open(self.identifier_file, 'w') as f:
                f.write(identifier)
        except IOError as e:
            print(f"Error saving checkpoint: {e}")

    def load_checkpoint(self) -> Tuple[dict, Optional[str]]:
        if os.path.exists(self.checkpoint_file) and os.path.exists(self.identifier_file):
            try:
                with open(self.identifier_file, 'r') as f:
                    saved_identifier = f.read()
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint = pickle.load(f)
                return checkpoint, saved_identifier
            except (IOError, pickle.PickleError) as e:
                print(f"Error loading checkpoint: {e}")
        return {'data': None}, None

    def delete_checkpoint(self):
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
            if os.path.exists(self.identifier_file):
                os.remove(self.identifier_file)
        except IOError as e:
            print(f"Error deleting checkpoint: {e}")

