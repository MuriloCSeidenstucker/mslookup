import hashlib
import os
import pickle
from typing import Any, Callable, Optional, Tuple


class CheckpointManager:
    def __init__(
        self,
        checkpoint_dir: str = 'tmp/',
        hash_func: Optional[Callable[[Any], str]] = None,
    ):
        self.checkpoint_dir = checkpoint_dir
        self.hash_func = hash_func or self.default_hash_func
        self.checkpoints_to_delete = []
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)

    def default_hash_func(self, obj: Any) -> str:
        return hashlib.md5(pickle.dumps(obj)).hexdigest()

    def generate_identifier(self, data: Any) -> str:
        return self.hash_func(data)

    def save_checkpoint(self, data: Any, stage: str, identifier: str):
        checkpoint_file = os.path.join(
            self.checkpoint_dir, f'{stage}_checkpoint.pkl'
        )
        identifier_file = os.path.join(
            self.checkpoint_dir, f'{stage}_identifier.txt'
        )

        self.checkpoints_to_delete.extend([checkpoint_file, identifier_file])

        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump({'data': data, 'identifier': identifier}, f)
            with open(identifier_file, 'w') as f:
                f.write(identifier)
        except IOError as e:
            print(f'Error saving checkpoint for stage {stage}: {e}')

    def load_checkpoint(self, stage: str) -> Tuple[dict, Optional[str]]:
        checkpoint_file = os.path.join(
            self.checkpoint_dir, f'{stage}_checkpoint.pkl'
        )
        identifier_file = os.path.join(
            self.checkpoint_dir, f'{stage}_identifier.txt'
        )

        if os.path.exists(checkpoint_file) and os.path.exists(identifier_file):
            try:
                with open(identifier_file, 'r') as f:
                    saved_identifier = f.read()
                with open(checkpoint_file, 'rb') as f:
                    checkpoint = pickle.load(f)
                return checkpoint, saved_identifier
            except (IOError, pickle.PickleError) as e:
                print(f'Error loading checkpoint for stage {stage}: {e}')
        return {'data': None}, None

    def delete_checkpoints(self):
        try:
            for file_path in self.checkpoints_to_delete:
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.checkpoints_to_delete = []
        except IOError as e:
            print(f'Error deleting checkpoints: {e}')
