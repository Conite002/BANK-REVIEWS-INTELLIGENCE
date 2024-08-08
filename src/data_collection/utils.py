import json, re
import stat
import os
from loguru import logger
from datetime import datetime



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


def load_from_config(config_path='config.json', name='state'):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, config_path)
    
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            value = config.get(name)
            if isinstance(value, str) and name != 'state':
                try:
                    value = datetime.fromisoformat(value)  # Convert back to datetime if possible
                except ValueError:
                    logger.error(f"Invalid datetime string for {name}: {value}")
            return value
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        return None
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def save_to_config(name, value):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, 'config.json')
    
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        
        if isinstance(value, datetime):
            value = value.isoformat()
        
        config[name] = value
        
        with open(config_path, 'w') as file:  # Use config_path, not config.json
            json.dump(config, file, indent=4)
    
    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError while saving: {e}")
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError while saving: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while saving: {e}")