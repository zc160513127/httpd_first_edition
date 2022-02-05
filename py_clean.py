
import os, shutil

def traversal(path):
    for file_name in os.listdir(path):
        abs_path = os.path.join(path, file_name)
        if file_name == '__pycache__':
            print(abs_path)
            shutil.rmtree(abs_path)
        elif os.path.isdir(abs_path):
            traversal(abs_path)
traversal(os.getcwd())