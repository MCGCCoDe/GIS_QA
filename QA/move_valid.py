import os
import shutil 


def move_valid(path1, valid_path, extensions):
    for root, dirs, file in os.walk(path1):
            for name in file:
                for ex in extensions:
                    if name.endswith(ex):
                        shutil.move(f'{root}/{name}', f'{valid_path}/{name}')