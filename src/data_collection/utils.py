import json, re
import stat
import os


# Function to load cities
def load_cities(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to handle errors
def throw_error(e, location):
    print(f"Error from {location}: {e}")

def set_permissions(path):
    """Set write permissions for the user on the user on the given path."""
    os.chmod(path, stat.S_IRWXU)


def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        set_permissions(path)
    else:
        print(f"Directory already exists; {path}")
    
def is_phone_number(text):
    phone_pattern = re.compile(r"^\+?\d[\d\s-]{8,}\d$")
    return bool(phone_pattern.match(text))

def is_website_url(text):
    url_pattern = re.compile(
        r'^(https?:\/\/)?'
        r'([\da-z\.-]+)\.'
        r'([a-z\.]{2,6})'
        r'([\/\w \.-]*)*\/?$'
    )
    return bool(url_pattern.match(text))

