import os
import subprocess

test_dir = '../'
for file in os.listdir(test_dir):
    if file.endswith('.py'):
        file_path = os.path.join(test_dir, file)
        print(f"Running {file_path}")
        subprocess.run(['python', file_path], check=True)
