# append project root path to sys.path
import os
import sys

dirname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(dirname)
sys.path.append(dirname)