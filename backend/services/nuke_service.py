import os
import json
from typing import Dict, List
from pathlib import Path

class NukeService:
    """
    Nuke integration service for HDR finishing and 16-bit post-production.
    Generates Nuke scripts with JSON-native parameter preservation.
    Enables professional compositors to tweak parameters in Nuke environment.
    """
    
    def __init__(self, output_dir: str = "nuke_scripts"):
    self.output_dir = output_dir
    os.makedirs(output_dir, exist_ok=True)

    def generate_nuke_script(self, image_path: str, design_params: Dict, script_name: str) -> str:
    """
    Generate production-ready Nuke script with HDR workflow.
    Preserves JSON-native control for compositor adjustments.
    
    Steps:
    1. Create Nuke node tree with Read node for input image
    2. Add ColorSpace conversion nodes for HDR pipeline
    3. Insert Grade nodes with JSON-controlled parameters
    4. Add Reformat nodes for resolution handling
    5. Configure Write node for 16-bit EXR output
    6. Embed JSON metadata in script for parameter preservation
    """
    script_path = os.path.join(self.output_dir, f"{script_name}.nk")
    
    nuke_script = f"""#! Nuke Version 14.0
    AI-Driven Industrial Product Design Studio
Generated Nuke Script with JSON-Native Control
Design Parameters Embedded for Compositor Control
set cut_paste_input [stack 0]
version 14.0 v5
JSON Parameters Embedded
{json.dumps(design_params, indent=2)}
Read {{
inputs 0
file {image_path}
format "1024 1024 0 0 1024 1024 1 square_1K"
origset true
colorspace linear
name Read_Source
xpos 0
ypos 0
}}
ColorSpace Node - Linear to HDR
Colorspace {{
colorspace_in linear
colorspace_out AlexaV3LogC
name ColorSpace_HDR
xpos 0
ypos 100
}}
Grade Node - Lighting Control (JSON-Controlled)
Grade {{
white {design_params.get('lighting_intensity', 1.0)}
gamma {design_params.get('gamma', 1.0)}
black_clamp false
white_clamp false
name Grade_Lighting
label "JSON Control: lighting_intensity"
xpos 0
ypos 200
}}
Grade Node - Color Palette Control (JSON-Controlled)
Grade {{
whitepoint {{{design_params.get('color_temp_r', 1.0)} {design_params.get('color_temp_g', 1.0)} {design_params.get('color_temp_b', 1.0)} 1}}
name Grade_ColorPalette
label "JSON Control: color_palette"
xpos 0
ypos 300
}}
Grade Node - Reflectivity Control (JSON-Controlled)
Grade {{
white {design_params.get('reflectivity', 0.8)}
multiply {{{design_params.get('specular_r', 1.0)} {design_params.get('specular_g', 1.0)} {design_params.get('specular_b', 1.0)} 1}}
name Grade_Reflectivity
label "JSON Control: reflectivity"
xpos 0
ypos 400
}}
Sharpen Node - Texture Quality Enhancement
Sharpen {{
size {design_params.get('texture_quality', 0.9) * 10}
name Sharpen_Texture
label "JSON Control: texture_quality"
xpos 0
ypos 500
}}
Reformat Node - Resolution Control
Reformat {{
type "to box"
box_width {design_params.get('width', 1024)}
box_height {design_params.get('height', 1024)}
box_fixed true
filter Cubic
name Reformat_Output
xpos 0
ypos 600
}}
Write Node - 16-bit EXR Output
Write {{
file "{os.path.splitext(image_path)[0]}_nuke_output.exr"
file_type exr
datatype "16 bit half"
compression "Zip (1 scanline)"
channels all
colorspace linear
create_directories true
checkHashOnRead false
version 1
name Write_EXR_16bit
xpos 0
ypos 700
}}
"""

with open(script_path, 'w') as f:
        f.write(nuke_script)
    
    return script_path

def generate_comparison_script(self, image_paths: List[str], script_name: str) -> str:
    """
    Generate Nuke script for visual comparison of multiple design iterations.
    Creates side-by-side comparison panel with HDR fidelity.
    
    Steps:
    1. Create Read nodes for each design variant
    2. Set up ContactSheet node for grid layout
    3. Apply consistent color grading across all variants
    4. Add text overlays with variant metadata
    5. Configure comparison output with 16-bit depth
    """
    script_path = os.path.join(self.output_dir, f"{script_name}_comparison.nk")
    
    read_nodes = []
    for idx, img_path in enumerate(image_paths):
        xpos = idx * 200
        read_node = f"""
        Read {{
inputs 0
file {img_path}
format "1024 1024 0 0 1024 1024 1 square_1K"
origset true
colorspace linear
name Read_Variant_{idx}
xpos {xpos}
ypos 0
}}
Text2 {{
font_size_toolbar 42
font_width_toolbar 100
font_height_toolbar 100
message "Variant {idx + 1}"
old_message {{86 97 114 105 97 110 116 32 49}}
box {{0 0 1024 100}}
xjustify center
yjustify top
transforms {{0 2}}
cursor_position 9
font {{ Arial : Regular : arial.ttf : 0 }}
global_font_scale 0.5
center {{512 50}}
cursor_initialised true
autofit_bbox false
initial_cursor_position {{0 1080}}
group_animations {{0}}
animation_layers {{{{root {{% if nuke.thisNode().showPanel() %}} [{{% if dynamic %}} else read-only [{{% endif %}}] {{% endif %}}Animation 1}}}}}}
name Text_Variant_{idx}
xpos {xpos}
ypos 100
}}
"""
read_nodes.append(read_node)
num_cols = min(len(image_paths), 4)
    num_rows = (len(image_paths) + num_cols - 1) // num_cols
    
    contactsheet_inputs = " ".join([f"Read_Variant_{i}" for i in range(len(image_paths))])
    
    nuke_script = f"""#! Nuke Version 14.0
    Design Comparison Panel - HDR Workflow
set cut_paste_input [stack 0]
version 14.0 v5
{''.join(read_nodes)}
ContactSheet {{
inputs {len(image_paths)}
width 4096
height {1024 * num_rows}
rows {num_rows}
columns {num_cols}
center true
roworder TopBottom
name ContactSheet_Comparison
xpos 400
ypos 300
}}
Write {{
file "{os.path.join(self.output_dir, script_name)}_comparison_output.exr"
file_type exr
datatype "16 bit half"
compression "Zip (1 scanline)"
colorspace linear
create_directories true
name Write_Comparison
xpos 400
ypos 400
}}
"""
with open(script_path, 'w') as f:
        f.write(nuke_script)
    
    return script_path

def create_hdr_workflow(self, image_path: str, hdr_params: Dict) -> str:
    """
    Create advanced HDR processing workflow in Nuke.
    Implements tone mapping, color grading, and 16-bit finishing.
    
    Steps:
    1. Load source image in linear color space
    2. Apply ACES color transform for HDR
    3. Implement tone mapping with exposure control
    4. Add film-style color grading
    5. Apply final sharpening and detail enhancement
    6. Export as 16-bit EXR with full HDR range
    """
    script_name = f"hdr_workflow_{Path(image_path).stem}"
    script_path = os.path.join(self.output_dir, f"{script_name}.nk")
    
    nuke_script = f"""#! Nuke Version 14.0
    Advanced HDR Workflow for Product Design
Read {{
inputs 0
file {image_path}
format "1024 1024 0 0 1024 1024 1 square_1K"
origset true
colorspace linear
name Read_HDR_Source
xpos 0
ypos 0
}}
ACES Transform
OCIOColorSpace {{
in_colorspace linear
out_colorspace ACES - ACEScg
name OCIOColorSpace_ACES
xpos 0
ypos 100
}}
Exposure Control
EXPTool {{
mode Stops
red {hdr_params.get('exposure', 0.0)}
green {hdr_params.get('exposure', 0.0)}
blue {hdr_params.get('exposure', 0.0)}
name EXPTool_Exposure
xpos 0
ypos 200
}}
Tone Mapping
Grade {{
white {hdr_params.get('highlights', 1.0)}
black {hdr_params.get('shadows', 0.0)}
gamma {hdr_params.get('midtones', 1.0)}
black_clamp false
white_clamp false
name Grade_ToneMapping
xpos 0
ypos 300
}}
Film-Style Color Grade
HueCorrect {{
saturation {hdr_params.get('saturation', 1.0)}
name HueCorrect_ColorGrade
xpos 0
ypos 400
}}
Detail Enhancement
Sharpen {{
size {hdr_params.get('sharpness', 5.0)}
name Sharpen_Detail
xpos 0
ypos 500
}}
Final ACES to Linear
OCIOColorSpace {{
in_colorspace ACES - ACEScg
out_colorspace linear
name OCIOColorSpace_Linear
xpos 0
ypos 600
}}
16-bit EXR Output
Write {{
file "{os.path.splitext(image_path)[0]}_hdr_final.exr"
file_type exr
datatype "16 bit half"
compression "Zip (16 scanlines)"
channels all
colorspace linear
create_directories true
name Write_HDR_EXR
xpos 0
ypos 700
}}
"""
with open(script_path, 'w') as f:
        f.write(nuke_script)
    
    return script_path

def embed_json_metadata(self, nuke_script_path: str, metadata: Dict) -> None:
    """
    Embed JSON metadata into Nuke script for parameter preservation.
    Allows compositors to reference and modify original generation parameters.
    """
    with open(nuke_script_path, 'r') as f:
        script_content = f.read()
    
    metadata_comment = f"\n# JSON Metadata:\n# {json.dumps(metadata, indent=2)}\n\n"
    
    script_lines = script_content.split('\n')
    insert_position = 3
    script_lines.insert(insert_position, metadata_comment)
    
    with open(nuke_script_path, 'w') as f:
        f.write('\n'.join(script_lines))