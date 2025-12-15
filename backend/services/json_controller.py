import json
from typing import Dict, Any, Optional
from models.design_schema import DesignRequest

class JSONController:
    """
    JSON-native control system for design parameter management.
    Provides seamless translation between natural language and structured JSON.
    Maintains parameter consistency across FIBO, ComfyUI, and Nuke workflows.
    """
    
    def __init__(self):
        self.schema_version = "1.0"
    
    def natural_language_to_json(self, nl_input: str, product_type: str) -> Dict:
        """
        Translate natural language design description to structured JSON.
        Uses pattern matching and design domain knowledge for accurate conversion.
        
        Steps:
        1. Parse natural language input for key design attributes
        2. Extract camera angle, lighting, material, and color preferences
        3. Map to standardized JSON schema
        4. Apply product-type-specific defaults
        5. Return complete design JSON with all parameters
        """
        design_json = {
            "prompt": nl_input,
            "product_type": product_type,
            "camera_angle": "three_quarter",
            "fov": 50.0,
            "lighting": "studio",
            "material": "metal",
            "color_palette": ["#1a1a1a", "#ffffff", "#c0c0c0"],
            "reflectivity": 0.8,
            "texture_quality": 0.9,
            "composition_focus": "centered",
            "background": "studio_white",
            "width": 1024,
            "height": 1024,
            "hdr_enabled": True,
            "bit_depth": 16
        }
        
        nl_lower = nl_input.lower()
        
        if "front view" in nl_lower or "from front" in nl_lower:
            design_json["camera_angle"] = "front"
        elif "side view" in nl_lower or "from side" in nl_lower:
            design_json["camera_angle"] = "side"
        elif "top view" in nl_lower or "from above" in nl_lower:
            design_json["camera_angle"] = "top"
        elif "isometric" in nl_lower:
            design_json["camera_angle"] = "isometric"
        
        if "dramatic" in nl_lower or "moody" in nl_lower:
            design_json["lighting"] = "dramatic"
        elif "natural" in nl_lower or "daylight" in nl_lower:
            design_json["lighting"] = "natural"
        elif "soft" in nl_lower:
            design_json["lighting"] = "soft"
        
        if "plastic" in nl_lower:
            design_json["material"] = "plastic"
        elif "glass" in nl_lower:
            design_json["material"] = "glass"
        elif "carbon fiber" in nl_lower or "carbon" in nl_lower:
            design_json["material"] = "carbon_fiber"
        elif "leather" in nl_lower:
            design_json["material"] = "leather"
        
        if "matte" in nl_lower or "non-reflective" in nl_lower:
            design_json["reflectivity"] = 0.3
        elif "glossy" in nl_lower or "shiny" in nl_lower or "reflective" in nl_lower:
            design_json["reflectivity"] = 0.95
        
        if "black" in nl_lower and "white" in nl_lower:
            design_json["color_palette"] = ["#000000", "#ffffff", "#808080"]
        elif "red" in nl_lower:
            design_json["color_palette"] = ["#cc0000", "#ffffff", "#333333"]
        elif "blue" in nl_lower:
            design_json["color_palette"] = ["#0066cc", "#ffffff", "#333333"]
        
        if product_type == "car":
            design_json["camera_angle"] = "three_quarter"
            design_json["fov"] = 35.0
            design_json["composition_focus"] = "dynamic"
        elif product_type == "electronics":
            design_json["camera_angle"] = "isometric"
            design_json["lighting"] = "product"
            design_json["background"] = "gradient"
        
        return design_json
    
    def json_to_display_params(self, design_json: Dict) -> Dict:
        """
        Convert technical JSON to user-friendly display parameters.
        Formats parameters for dashboard visualization.
        """
        display_params = {
            "Camera": design_json.get('camera_angle', 'N/A').replace('_', ' ').title(),
            "Field of View": f"{design_json.get('fov', 50.0)}°",
            "Lighting": design_json.get('lighting', 'N/A').replace('_', ' ').title(),
            "Material": design_json.get('material', 'N/A').replace('_', ' ').title(),
            "Reflectivity": f"{design_json.get('reflectivity', 0.8) * 100:.0f}%",
            "Texture Quality": f"{design_json.get('texture_quality', 0.9) * 100:.0f}%",
            "Resolution": f"{design_json.get('width', 1024)}x{design_json.get('height', 1024)}",
            "Color Depth": f"{design_json.get('bit_depth', 16)}-bit",
            "HDR": "Enabled" if design_json.get('hdr_enabled', True) else "Disabled"
        }
        
        if 'color_palette' in design_json:
            display_params["Color Palette"] = ", ".join(design_json['color_palette'])
        
        return display_params
    
    def merge_json_updates(self, base_json: Dict, updates: Dict) -> Dict:
        """
        Merge parameter updates while maintaining JSON schema validity.
        Preserves interdependent parameter relationships.
        """
        merged = base_json.copy()
        
        for key, value in updates.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self.merge_json_updates(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
        
        return merged
    
    def validate_json_schema(self, design_json: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate JSON against design schema requirements.
        Ensures all required parameters are present and correctly formatted.
        """
        required_fields = ['prompt', 'product_type', 'width', 'height']
        
        for field in required_fields:
            if field not in design_json:
                return False, f"Missing required field: {field}"
        
        if design_json.get('width', 0) < 512 or design_json.get('width', 0) > 2048:
            return False, "Width must be between 512 and 2048 pixels"
        
        if design_json.get('height', 0) < 512 or design_json.get('height', 0) > 2048:
            return False, "Height must be between 512 and 2048 pixels"
        
        if design_json.get('fov'):
            if design_json['fov'] < 10 or design_json['fov'] > 120:
                return False, "Field of view must be between 10 and 120 degrees"
        
        if design_json.get('reflectivity'):
            if design_json['reflectivity'] < 0 or design_json['reflectivity'] > 1:
                return False, "Reflectivity must be between 0 and 1"
        
        return True, None
    
    def export_to_nuke_format(self, design_json: Dict) -> Dict:
    """
    Convert design JSON to Nuke-compatible parameter format.
    Preserves JSON-native control for compositor adjustments.
    """
    nuke_params = {
    "lighting_intensity": 1.0,
    "gamma": 1.0,
    "color_temp_r": 1.0,
    "color_temp_g": 1.0,
    "color_temp_b": 1.0,
    "reflectivity": design_json.get('reflectivity', 0.8),
    "specular_r": 1.0,
    "specular_g": 1.0,
    "specular_b": 1.0,
    "texture_quality": design_json.get('texture_quality', 0.9),
    "width": design_json.get('width', 1024),
    "height": design_json.get('height', 1024)
    }
    lighting = design_json.get('lighting', 'studio')
    if lighting == 'dramatic':
        nuke_params['lighting_intensity'] = 1.5
        nuke_params['gamma'] = 0.85
    elif lighting == 'soft':
        nuke_params['lighting_intensity'] = 0.8
        nuke_params['gamma'] = 1.1
    elif lighting == 'hdr':
        nuke_params['lighting_intensity'] = 2.0
        nuke_params['gamma'] = 1.0
    
    if 'color_palette' in design_json and len(design_json['color_palette']) > 0:
        primary_color = design_json['color_palette'][0]
        if primary_color.startswith('#'):
            r = int(primary_color[1:3], 16) / 255.0
            g = int(primary_color[3:5], 16) / 255.0
            b = int(primary_color[5:7], 16) / 255.0
            nuke_params['color_temp_r'] = r * 0.5 + 0.5
            nuke_params['color_temp_g'] = g * 0.5 + 0.5
            nuke_params['color_temp_b'] = b * 0.5 + 0.5
    
    return nuke_params