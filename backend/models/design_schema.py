from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class CameraAngle(str, Enum):
    """Predefined camera angles for industrial design"""
    FRONT = "front"
    SIDE = "side"
    THREE_QUARTER = "three_quarter"
    TOP = "top"
    ISOMETRIC = "isometric"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"

class MaterialType(str, Enum):
    """Material types for product rendering"""
    METAL = "metal"
    PLASTIC = "plastic"
    GLASS = "glass"
    CARBON_FIBER = "carbon_fiber"
    LEATHER = "leather"
    FABRIC = "fabric"
    RUBBER = "rubber"

class LightingSetup(str, Enum):
    """Professional lighting configurations"""
    STUDIO = "studio"
    NATURAL = "natural"
    DRAMATIC = "dramatic"
    SOFT = "soft"
    HDR = "hdr"
    PRODUCT = "product"

class DesignRequest(BaseModel):
    """
    Main design generation request schema.
    Converts natural language requirements into structured JSON parameters.
    """
    prompt: str = Field(..., description="Natural language description of the product")
    product_type: str = Field(..., description="Type of product: car, electronics, appliance")
    camera_angle: CameraAngle = Field(default=CameraAngle.THREE_QUARTER)
    fov: float = Field(default=50.0, ge=10.0, le=120.0, description="Field of view in degrees")
    lighting: LightingSetup = Field(default=LightingSetup.STUDIO)
    material: MaterialType = Field(default=MaterialType.METAL)
    color_palette: List[str] = Field(default=["#1a1a1a", "#ffffff", "#c0c0c0"])
    reflectivity: float = Field(default=0.8, ge=0.0, le=1.0)
    texture_quality: float = Field(default=0.9, ge=0.0, le=1.0)
    composition_focus: str = Field(default="centered")
    background: str = Field(default="studio_white")
    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=1024, ge=512, le=2048)
    hdr_enabled: bool = Field(default=True)
    bit_depth: int = Field(default=16, description="8 or 16 bit color depth")
    
    def to_fibo_json(self) -> Dict:
        """
        Converts design request to FIBO API compatible JSON format.
        This method structures parameters for optimal FIBO generation.
        """
        return {
            "prompt": self.prompt,
            "image_size": {
                "width": self.width,
                "height": self.height
            },
            "num_images": 1,
            "sync_mode": True,
            "enable_safety_checks": True,
            "output_format": "png",
            "expand_prompt": True
        }
    
    def to_bria_json(self) -> Dict:
        """
        Converts design request to Bria API compatible JSON format.
        Includes advanced parameters for HDR and material control.
        """
        return {
            "prompt": self.prompt,
            "width": self.width,
            "height": self.height,
            "num_results": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
            "seed": None
        }

class RefineRequest(BaseModel):
    """
    Refinement request for iterative design improvements.
    Used with ComfyUI refine nodes.
    """
    image_id: str = Field(..., description="ID of the image to refine")
    refinement_prompt: str = Field(..., description="Specific refinement instructions")
    strength: float = Field(default=0.7, ge=0.1, le=1.0)
    preserve_composition: bool = Field(default=True)
    enhance_details: bool = Field(default=True)

class DesignVariant(BaseModel):
    """
    Design variant configuration for parallel agent generation.
    Each agent generates different perspectives or variations.
    """
    variant_id: str
    camera_angle: CameraAngle
    lighting: LightingSetup
    color_variation: List[str]
    priority: int = Field(default=1, ge=1, le=10)

class NukeExportConfig(BaseModel):
    """
    Configuration for Nuke script export with HDR settings.
    Preserves JSON-native control in Nuke environment.
    """
    export_format: str = Field(default="exr", description="exr, hdr, or tiff")
    color_space: str = Field(default="linear", description="linear or sRGB")
    bit_depth: int = Field(default=16)
    include_alpha: bool = Field(default=True)
    compression: str = Field(default="zip")