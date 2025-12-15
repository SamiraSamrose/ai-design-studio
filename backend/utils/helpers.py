import os
import uuid
from datetime import datetime
from pathlib import Path
from PIL import Image
import io

def generate_unique_id() -> str:
    """Generate unique identifier for designs and sessions"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_suffix = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_suffix}"

def save_image(image_data: bytes, output_dir: str, filename: str) -> str:
    """
    Save image data to disk with proper directory structure.
    Handles HDR and 16-bit formats appropriately.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'wb') as f:
        f.write(image_data)
    
    return filepath

def create_directory_structure(base_dir: str) -> Dict[str, str]:
    """
    Create complete directory structure for project outputs.
    Returns dictionary of created paths.
    """
    directories = {
        'generated_designs': os.path.join(base_dir, 'generated_designs'),
        'refined_designs': os.path.join(base_dir, 'refined_designs'),
        'comparisons': os.path.join(base_dir, 'comparisons'),
        'nuke_scripts': os.path.join(base_dir, 'nuke_scripts'),
        'temp': os.path.join(base_dir, 'temp'),
        'exports': os.path.join(base_dir, 'exports')
    }
    
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return directories

def validate_image_format(image_data: bytes) -> bool:
    """Validate that image data is in supported format"""
    try:
        img = Image.open(io.BytesIO(image_data))
        return img.format in ['PNG', 'JPEG', 'EXR', 'TIFF', 'HDR']
    except:
        return False
