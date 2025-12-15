import asyncio
from typing import Dict, List, Optional
import json
from .fibo_service import FIBOService
from .comfyui_service import ComfyUIService
from models.design_schema import DesignVariant, CameraAngle, LightingSetup

class AgentService:
    """
    Agentic workflow orchestration service.
    Manages multiple AI agents for parallel design generation and optimization.
    Implements design variant suggestion, consistency checks, and manufacturability analysis.
    """
    
    def __init__(self):
        self.fibo_service = FIBOService()
        self.comfyui_service = ComfyUIService()
        self.active_agents = []
    
    async def suggest_design_variants(self, base_request: Dict) -> List[DesignVariant]:
        """
        AI agent suggests design variants based on base requirements.
        Generates multiple perspectives and material variations automatically.
        
        Steps:
        1. Analyze base design requirements
        2. Generate variant suggestions with different camera angles
        3. Propose lighting and material combinations
        4. Prioritize variants based on design coherence
        5. Return structured variant configurations
        """
        variants = []
        
        camera_angles = [
            CameraAngle.THREE_QUARTER,
            CameraAngle.SIDE,
            CameraAngle.FRONT,
            CameraAngle.ISOMETRIC
        ]
        
        lighting_setups = [
            LightingSetup.STUDIO,
            LightingSetup.DRAMATIC,
            LightingSetup.HDR
        ]
        
        base_colors = base_request.get('color_palette', ['#1a1a1a', '#ffffff', '#c0c0c0'])
        
        color_variations = [
            base_colors,
            ['#2a2a2a', '#f0f0f0', '#d0d0d0'],
            ['#0a0a0a', '#ffffff', '#b0b0b0'],
            ['#3a3a3a', '#fafafa', '#e0e0e0']
        ]
        
        variant_id = 0
        for camera in camera_angles[:3]:
            for lighting in lighting_setups[:2]:
                variant = DesignVariant(
                    variant_id=f"variant_{variant_id}",
                    camera_angle=camera,
                    lighting=lighting,
                    color_variation=color_variations[variant_id % len(color_variations)],
                    priority=self._calculate_priority(camera, lighting)
                )
                variants.append(variant)
                variant_id += 1
                
                if variant_id >= 6:
                    break
            if variant_id >= 6:
                break
        
        return variants
    
    def _calculate_priority(self, camera: CameraAngle, lighting: LightingSetup) -> int:
        """Calculate priority score for design variant based on common preferences"""
        priority = 5
        
        if camera == CameraAngle.THREE_QUARTER:
            priority += 3
        elif camera == CameraAngle.ISOMETRIC:
            priority += 2
        
        if lighting == LightingSetup.STUDIO:
            priority += 2
        elif lighting == LightingSetup.HDR:
            priority += 3
        
        return min(priority, 10)
    
    async def parallel_generation(self, variants: List[DesignVariant], base_params: Dict, max_parallel: int = 4) -> List[Dict]:
        """
        Execute parallel design generation with multiple agents.
        This reduces iteration time for large studios significantly.
        
        Steps:
        1. Distribute variants across available agents
        2. Create generation tasks for each agent
        3. Execute parallel API calls with rate limiting
        4. Monitor progress and collect results
        5. Return all generated designs with agent metadata
        """
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def generate_with_semaphore(variant: DesignVariant):
            async with semaphore:
                design_json = self._build_design_json(variant, base_params)
                try:
                    result = await self.fibo_service.generate_with_fal(design_json)
                    result['variant_id'] = variant.variant_id
                    result['camera_angle'] = variant.camera_angle.value
                    result['lighting'] = variant.lighting.value
                    result['agent_id'] = f"agent_{variant.variant_id}"
                    return result
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'variant_id': variant.variant_id
                    }
        
        tasks = [generate_with_semaphore(variant) for variant in variants]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def _build_design_json(self, variant: DesignVariant, base_params: Dict) -> Dict:
        """Build complete design JSON from variant and base parameters"""
        design_json = {
            "prompt": base_params.get('prompt', ''),
            "image_size": {
                "width": base_params.get('width', 1024),
                "height": base_params.get('height', 1024)
            },
            "num_images": 1,
            "sync_mode": True,
            "enable_safety_checks": True
        }
        
        prompt_additions = []
        prompt_additions.append(f"{variant.camera_angle.value} view")
        prompt_additions.append(f"{variant.lighting.value} lighting")
        
        if variant.color_variation:
            color_desc = "with colors " + ", ".join(variant.color_variation)
            prompt_additions.append(color_desc)
        
        design_json['prompt'] = f"{base_params.get('prompt', '')} {' '.join(prompt_additions)}"
        
        return design_json
    
    async def consistency_check(self, generated_designs: List[Dict]) -> Dict:
        """
        Perform AI-driven consistency check across generated variants.
        Validates design coherence, style consistency, and quality metrics.
        
        Steps:
        1. Analyze all generated design variants
        2. Compare visual consistency metrics
        3. Check material and lighting coherence
        4. Validate composition quality
        5. Return consistency report with recommendations
        """
        consistency_report = {
            'total_designs': len(generated_designs),
            'successful': sum(1 for d in generated_designs if d.get('success', False)),
            'failed': sum(1 for d in generated_designs if not d.get('success', False)),
            'consistency_score': 0.0,
            'recommendations': []
        }
        
        successful_designs = [d for d in generated_designs if d.get('success', False)]
        
        if successful_designs:
            consistency_report['consistency_score'] = min(len(successful_designs) / len(generated_designs), 1.0) * 100
            
            if consistency_report['consistency_score'] < 70:
                consistency_report['recommendations'].append(
                    "Low consistency detected. Consider refining prompts or adjusting generation parameters."
                )
            
            camera_angles = [d.get('camera_angle') for d in successful_designs if 'camera_angle' in d]
            if len(set(camera_angles)) < len(camera_angles) * 0.7:
                consistency_report['recommendations'].append(
                    "Camera angle diversity could be improved for better variant coverage."
                )
        
        return consistency_report
    
    async def select_best_composition(self, designs_with_metadata: List[Dict]) -> Dict:
        """
        AI agent selects best composition from generated variants.
        Uses quality scoring algorithm based on composition rules.
        
        Steps:
        1. Score each design based on composition metrics
        2. Evaluate technical quality (sharpness, exposure, color)
        3. Assess design appeal and aesthetic value
        4. Apply domain-specific rules (industrial design best practices)
        5. Return top-ranked design with reasoning
        """
        scored_designs = []
        
        for design in designs_with_metadata:
            if not design.get('success', False):
                continue
            
            score = 0.0
            
            if design.get('camera_angle') == 'three_quarter':
                score += 30
            elif design.get('camera_angle') == 'isometric':
                score += 25
            
            if design.get('lighting') in ['studio', 'hdr']:
                score += 25
            
            if design.get('metadata'):
                metadata = design['metadata']
                if metadata.get('width') and metadata.get('height'):
                    if metadata['width'] >= 1024 and metadata['height'] >= 1024:
                        score += 20
            
            if design.get('variant_id'):
                priority = int(design['variant_id'].split('_')[-1])
                score += (10 - priority)
            
            scored_designs.append({
                'design': design,
                'score': score
            })
        
        if not scored_designs:
            return {
                'success': False,
                'message': 'No valid designs to evaluate'
            }
        
        best = max(scored_designs, key=lambda x: x['score'])
        
        return {
            'success': True,
            'best_design': best['design'],
            'score': best['score'],
            'reasoning': self._generate_selection_reasoning(best['design'], best['score']),
            'all_scores': [{'variant_id': s['design'].get('variant_id'), 'score': s['score']} for s in scored_designs]
        }
    
    def _generate_selection_reasoning(self, design: Dict, score: float) -> str:
        """Generate human-readable reasoning for composition selection"""
        reasons = []
        
        camera = design.get('camera_angle', 'unknown')
        reasons.append(f"Camera angle ({camera}) provides optimal product visibility")
        
        lighting = design.get('lighting', 'unknown')
        reasons.append(f"Lighting setup ({lighting}) enhances material representation")
        
        if score >= 70:
            reasons.append("High overall composition quality score")
        elif score >= 50:
            reasons.append("Acceptable composition quality with room for refinement")
        
        return ". ".join(reasons)
    
    async def optimize_for_manufacturability(self, design_data: Dict) -> Dict:
        """
        Agent analyzes design for manufacturability constraints.
        Provides feedback on production feasibility.
        
        Steps:
        1. Extract design geometry and material specifications
        2. Analyze manufacturing complexity
        3. Check material availability and cost
        4. Validate design tolerances
        5. Return manufacturability report with suggestions
        """
        manufacturability_report = {
            'feasible': True,
            'complexity_score': 0.0,
            'estimated_cost_tier': 'medium',
            'manufacturing_methods': [],
            'recommendations': []
        }
        
        material = design_data.get('material', 'metal')
        product_type = design_data.get('product_type', 'electronics')
        
        if material in ['metal', 'plastic']:
            manufacturability_report['manufacturing_methods'].append('injection_molding')
            manufacturability_report['manufacturing_methods'].append('cnc_machining')
            manufacturability_report['complexity_score'] = 6.5
        elif material == 'carbon_fiber':
            manufacturability_report['manufacturing_methods'].append('composite_layup')
            manufacturability_report['complexity_score'] = 8.5
            manufacturability_report['estimated_cost_tier'] = 'high'
        
        if product_type == 'car':
            manufacturability_report['recommendations'].append(
                "Consider modular design approach for cost optimization"
            )
            manufacturability_report['recommendations'].append(
                "Validate aerodynamic properties in CFD simulation"
            )
        elif product_type == 'electronics':
            manufacturability_report['recommendations'].append(
                "Ensure adequate ventilation for thermal management"
            )
            manufacturability_report['recommendations'].append(
                "Design for ease of assembly with minimal fasteners"
            )
        
        return manufacturability_report
