import importlib.util
import sys

def check_module(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"Module {module_name} is NOT installed")
        return False
    else:
        print(f"Module {module_name} is installed")
        return True

# List of required modules from requirements/prod.txt
required_modules = [
    "streamlit",
    "openai",
    "python-dotenv",
    "plotly",
    "pandas",
    "statsmodels"
]

print("Checking required modules:")
all_installed = True
for module in required_modules:
    if not check_module(module):
        all_installed = False

if all_installed:
    print("\nAll required modules are installed!")
else:
    print("\nSome required modules are missing. Please install them using:")
    print("pip install -r requirements/prod.txt")

print("\nPython version:", sys.version)
