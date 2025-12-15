import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional
import json

class ComfyUIService:
    """
    ComfyUI integration for iterative refinement workflow.
    Implements Generate and Refine nodes for design iteration.
    Manages node-based processing pipeline.
    """
    
    def __init__(self, comfyui_url: str = "http://localhost:8188"):
        self.base_url = comfyui_url
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.refine_endpoint = f"{self.base_url}/api/refine"
        self.workflow_endpoint = f"{self.base_url}/api/workflow"
    
    async def generate_node(self, design_params: Dict) -> Dict:
        """
        Execute ComfyUI Generate Node for initial design creation.
        This node creates base product designs with controllable parameters.
        
        Steps:
        1. Construct ComfyUI workflow JSON with generate node
        2. Configure node parameters from design schema
        3. Submit workflow to ComfyUI API
        4. Monitor execution and retrieve output
        5. Return generated design with node metadata
        """
        workflow = {
            "nodes": [
                {
                    "id": "generate_1",
                    "type": "BriaGenerateNode",
                    "inputs": {
                        "prompt": design_params.get('prompt'),
                        "width": design_params.get('width', 1024),
                        "height": design_params.get('height', 1024),
                        "api_token": design_params.get('api_token'),
                        "guidance_scale": design_params.get('guidance_scale', 7.5),
                        "num_inference_steps": design_params.get('num_inference_steps', 50),
                        "seed": design_params.get('seed', -1)
                    },
                    "outputs": ["IMAGE"]
                },
                {
                    "id": "save_1",
                    "type": "SaveImage",
                    "inputs": {
                        "images": "generate_1.IMAGE",
                        "filename_prefix": "design_output"
                    }
                }
            ],
            "links": [
                ["generate_1", 0, "save_1", 0]
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    prompt_id = result['prompt_id']
                    
                    output = await self._wait_for_completion(session, prompt_id)
                    
                    return {
                        'success': True,
                        'prompt_id': prompt_id,
                        'output': output,
                        'workflow': workflow
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ComfyUI Generate Node error: {error_text}")
    
    async def refine_node(self, image_id: str, refine_params: Dict) -> Dict:
        """
        Execute ComfyUI Refine Node for iterative design improvements.
        This node performs targeted refinements on existing designs.
        
        Steps:
        1. Load existing design by image_id
        2. Construct refinement workflow with ControlNet nodes
        3. Apply refinement parameters (strength, focus areas)
        4. Execute refinement pipeline
        5. Return refined design with comparison data
        """
        workflow = {
            "nodes": [
                {
                    "id": "load_1",
                    "type": "LoadImage",
                    "inputs": {
                        "image": image_id
                    },
                    "outputs": ["IMAGE", "MASK"]
                },
                {
                    "id": "refine_1",
                    "type": "BriaRefineNode",
                    "inputs": {
                        "image": "load_1.IMAGE",
                        "prompt": refine_params.get('refinement_prompt'),
                        "strength": refine_params.get('strength', 0.7),
                        "api_token": refine_params.get('api_token'),
                        "preserve_composition": refine_params.get('preserve_composition', True),
                        "enhance_details": refine_params.get('enhance_details', True)
                    },
                    "outputs": ["IMAGE"]
                },
                {
                    "id": "save_2",
                    "type": "SaveImage",
                    "inputs": {
                        "images": "refine_1.IMAGE",
                        "filename_prefix": "refined_design"
                    }
                }
            ],
            "links": [
                ["load_1", 0, "refine_1", 0],
                ["refine_1", 0, "save_2", 0]
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    prompt_id = result['prompt_id']
                    
                    output = await self._wait_for_completion(session, prompt_id)
                    
                    return {
                        'success': True,
                        'prompt_id': prompt_id,
                        'output': output,
                        'workflow': workflow,
                        'original_image_id': image_id
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ComfyUI Refine Node error: {error_text}")
    
    async def _wait_for_completion(self, session: aiohttp.ClientSession, prompt_id: str, timeout: int = 300) -> Dict:
        """
        Wait for ComfyUI workflow completion with status polling.
        Monitors node execution progress and retrieves final output.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"ComfyUI workflow {prompt_id} timed out")
            
            async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
                if response.status == 200:
                    history = await response.json()
                    
                    if prompt_id in history:
                        prompt_history = history[prompt_id]
                        
                        if 'outputs' in prompt_history:
                            return prompt_history['outputs']
            
            await asyncio.sleep(2)
    
    async def create_comparison_workflow(self, image_ids: List[str]) -> Dict:
        """
        Create visual comparison panel workflow for multiple design iterations.
        This enables AI agent to select best composition.
        
        Steps:
        1. Load all design variants
        2. Create side-by-side comparison layout
        3. Apply consistent color grading
        4. Generate comparison matrix
        5. Return comparison panel with metadata
        """
        nodes = []
        links = []
        
        for idx, image_id in enumerate(image_ids):
            load_node = {
                "id": f"load_{idx}",
                "type": "LoadImage",
                "inputs": {"image": image_id},
                "outputs": ["IMAGE", "MASK"]
            }
            nodes.append(load_node)
        
        comparison_node = {
            "id": "comparison_grid",
            "type": "ImageBatch",
            "inputs": {
                "images": [f"load_{i}.IMAGE" for i in range(len(image_ids))]
            },
            "outputs": ["IMAGE"]
        }
        nodes.append(comparison_node)
        
        save_node = {
            "id": "save_comparison",
            "type": "SaveImage",
            "inputs": {
                "images": "comparison_grid.IMAGE",
                "filename_prefix": "comparison_panel"
            }
        }
        nodes.append(save_node)
        
        for idx in range(len(image_ids)):
            links.append([f"load_{idx}", 0, "comparison_grid", idx])
        links.append(["comparison_grid", 0, "save_comparison", 0])
        
        workflow = {
            "nodes": nodes,
            "links": links
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    prompt_id = result['prompt_id']
                    
                    output = await self._wait_for_completion(session, prompt_id)
                    
                    return {
                        'success': True,
                        'prompt_id': prompt_id,
                        'output': output,
                        'compared_images': image_ids
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ComfyUI Comparison workflow error: {error_text}")
    
    def build_controlnet_workflow(self, base_image: str, control_params: Dict) -> Dict:
        """
        Build advanced ControlNet workflow for fine-grained control.
        Each aspect (lighting, angle, composition, palette) independently controllable.
        
        Steps:
        1. Load base design image
        2. Configure ControlNet preprocessors for each control aspect
        3. Set up independent control layers
        4. Apply multimodal control parameters
        5. Generate controlled output with preserved artistic freedom
        """
        workflow = {
            "nodes": [
                {
                    "id": "load_base",
                    "type": "LoadImage",
                    "inputs": {"image": base_image},
                    "outputs": ["IMAGE", "MASK"]
                },
                {
                    "id": "controlnet_lighting",
                    "type": "ControlNetApply",
                    "inputs": {
                        "conditioning": "positive_prompt",
                        "control_net": "lighting_control",
                        "image": "load_base.IMAGE",
                        "strength": control_params.get('lighting_strength', 0.8)
                    },
                    "outputs": ["CONDITIONING"]
                },
                {
                    "id": "controlnet_angle",
                    "type": "ControlNetApply",
                    "inputs": {
                        "conditioning": "controlnet_lighting.CONDITIONING",
                        "control_net": "angle_control",
                        "image": "load_base.IMAGE",
                        "strength": control_params.get('angle_strength', 0.7)
                    },
                    "outputs": ["CONDITIONING"]
                },
                {
                    "id": "controlnet_composition",
                    "type": "ControlNetApply",
                    "inputs": {
                        "conditioning": "controlnet_angle.CONDITIONING",
                        "control_net": "composition_control",
                        "image": "load_base.IMAGE",
                        "strength": control_params.get('composition_strength', 0.6)
                    },
                    "outputs": ["CONDITIONING"]
                },
                {
                    "id": "generate_controlled",
                    "type": "KSampler",
                    "inputs": {
                        "model": "fibo_model",
                        "positive": "controlnet_composition.CONDITIONING",
                        "negative": "negative_prompt",
                        "latent_image": "load_base.IMAGE",
                        "seed": control_params.get('seed', -1),
                        "steps": control_params.get('steps', 30),
                        "cfg": control_params.get('cfg', 7.5),
                        "sampler_name": "euler_a",
                        "scheduler": "normal",
                        "denoise": control_params.get('denoise', 0.75)
                    },
                    "outputs": ["LATENT"]
                },
                {
                    "id": "vae_decode",
                    "type": "VAEDecode",
                    "inputs": {
                        "samples": "generate_controlled.LATENT",
                        "vae": "fibo_vae"
                    },
                    "outputs": ["IMAGE"]
                },
                {
                    "id": "save_controlled",
                    "type": "SaveImage",
                    "inputs": {
                        "images": "vae_decode.IMAGE",
                        "filename_prefix": "controlnet_design"
                    }
                }
            ]
        }
        
        return workflow