import asyncio
from typing import Dict, List, Optional
from .fibo_service import FIBOService
from .comfyui_service import ComfyUIService
from .nuke_service import NukeService

class IterationService:
    """
    Handles iterative design generation workflow.
    Generates multiple iterations, creates comparison panels, and enables AI selection.
    This service implements Point 8: iteration → comparison → AI selection workflow.
    """
    
    def __init__(self):
        self.fibo_service = FIBOService()
        self.comfyui_service = ComfyUIService()
        self.nuke_service = NukeService()
    
    async def generate_iterations(self, base_params: Dict, num_iterations: int = 4) -> List[Dict]:
        """
        Generate multiple iterations with subtle parameter variations.
        Each iteration adjusts lighting intensity, FOV, or composition slightly.
        
        Steps:
        1. Create parameter variations for each iteration
        2. Generate all iterations in parallel
        3. Collect results with iteration metadata
        4. Return complete iteration set
        """
        iterations = []
        
        for i in range(num_iterations):
            iteration_params = base_params.copy()
            
            variation_factor = (i + 1) / num_iterations
            
            if 'fov' in iteration_params:
                base_fov = iteration_params['fov']
                iteration_params['fov'] = base_fov * (0.9 + variation_factor * 0.2)
            
            if 'reflectivity' in iteration_params:
                base_reflectivity = iteration_params['reflectivity']
                iteration_params['reflectivity'] = base_reflectivity * (0.85 + variation_factor * 0.3)
            
            lighting_variations = ['studio', 'hdr', 'dramatic', 'soft']
            iteration_params['lighting'] = lighting_variations[i % len(lighting_variations)]
            
            iterations.append({
                'iteration_number': i + 1,
                'params': iteration_params,
                'variation_type': f'lighting_{iteration_params["lighting"]}_fov_{iteration_params["fov"]:.1f}'
            })
        
        tasks = []
        for iteration in iterations:
            design_json = {
                "prompt": iteration['params'].get('prompt', ''),
                "image_size": {
                    "width": iteration['params'].get('width', 1024),
                    "height": iteration['params'].get('height', 1024)
                },
                "num_images": 1,
                "sync_mode": True,
                "enable_safety_checks": True
            }
            tasks.append(self.fibo_service.generate_with_fal(design_json))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_iterations = []
        for idx, (iteration, result) in enumerate(zip(iterations, results)):
            if isinstance(result, Exception):
                final_iterations.append({
                    'success': False,
                    'iteration_number': iteration['iteration_number'],
                    'error': str(result)
                })
            else:
                final_iterations.append({
                    'success': True,
                    'iteration_number': iteration['iteration_number'],
                    'image_data': result['image_data'],
                    'image_url': result.get('image_url'),
                    'params': iteration['params'],
                    'variation_type': iteration['variation_type'],
                    'metadata': result.get('metadata', {})
                })
        
        return final_iterations
    
    async def create_iteration_comparison_panel(self, iteration_ids: List[str], iteration_data: List[Dict]) -> Dict:
        """
        Create visual comparison panel in both Nuke and ComfyUI for iterations.
        This implements the iteration → comparison workflow.
        
        Steps:
        1. Collect all iteration images
        2. Generate ComfyUI comparison workflow
        3. Generate Nuke comparison script with HDR nodes
        4. Return both workflow and script paths
        """
        image_paths = []
        for data in iteration_data:
            if data.get('success') and 'image_data' in data:
                from utils.helpers import save_image, generate_unique_id
                filename = f"iteration_{data['iteration_number']}_{generate_unique_id()}.png"
                filepath = save_image(data['image_data'], 'generated_designs', filename)
                image_paths.append(filepath)
        
        comfyui_result = await self.comfyui_service.create_comparison_workflow(iteration_ids)
        
        nuke_script_path = self.nuke_service.generate_comparison_script(
            image_paths,
            f"iteration_comparison_{generate_unique_id()}"
        )
        
        return {
            'success': True,
            'comfyui_workflow': comfyui_result,
            'nuke_script_path': nuke_script_path,
            'compared_iterations': len(iteration_ids),
            'image_paths': image_paths
        }
    
    async def ai_select_best_iteration(self, iterations: List[Dict]) -> Dict:
        """
        AI agent analyzes iterations and selects the best composition.
        This completes the iteration → comparison → AI selection workflow.
        
        Steps:
        1. Score each iteration based on multiple criteria
        2. Evaluate lighting effectiveness
        3. Assess composition balance
        4. Check technical quality metrics
        5. Return best iteration with detailed reasoning
        """
        scored_iterations = []
        
        for iteration in iterations:
            if not iteration.get('success'):
                continue
            
            score = 0.0
            reasons = []
            
            params = iteration.get('params', {})
            
            lighting = params.get('lighting', 'studio')
            if lighting == 'hdr':
                score += 30
                reasons.append("HDR lighting provides superior dynamic range")
            elif lighting == 'studio':
                score += 25
                reasons.append("Studio lighting ensures consistent illumination")
            elif lighting == 'dramatic':
                score += 20
                reasons.append("Dramatic lighting creates visual impact")
            
            fov = params.get('fov', 50)
            if 35 <= fov <= 55:
                score += 20
                reasons.append("Optimal FOV for product visualization")
            elif 25 <= fov <= 70:
                score += 15
                reasons.append("Acceptable FOV range")
            
            reflectivity = params.get('reflectivity', 0.8)
            if 0.7 <= reflectivity <= 0.9:
                score += 25
                reasons.append("Reflectivity enhances material perception")
            
            composition = params.get('composition_focus', 'centered')
            if composition in ['centered', 'rule_of_thirds']:
                score += 15
                reasons.append(f"Composition follows {composition} principles")
            
            texture_quality = params.get('texture_quality', 0.9)
            if texture_quality >= 0.85:
                score += 10
                reasons.append("High texture quality maintains detail")
            
            scored_iterations.append({
                'iteration': iteration,
                'score': score,
                'reasons': reasons
            })
        
        if not scored_iterations:
            return {
                'success': False,
                'message': 'No valid iterations to evaluate'
            }
        
        scored_iterations.sort(key=lambda x: x['score'], reverse=True)
        best = scored_iterations[0]
        
        return {
            'success': True,
            'best_iteration': best['iteration'],
            'score': best['score'],
            'reasoning': '. '.join(best['reasons']),
            'all_scores': [
                {
                    'iteration_number': s['iteration']['iteration_number'],
                    'score': s['score'],
                    'variation_type': s['iteration'].get('variation_type', 'unknown')
                }
                for s in scored_iterations
            ],
            'improvement_suggestions': self._generate_improvement_suggestions(best['iteration'])
        }
    
    def _generate_improvement_suggestions(self, best_iteration: Dict) -> List[str]:
        """Generate suggestions for further improvement based on best iteration"""
        suggestions = []
        params = best_iteration.get('params', {})
        
        if params.get('reflectivity', 0.8) < 0.75:
            suggestions.append("Consider increasing reflectivity for more premium appearance")
        
        if params.get('lighting') != 'hdr':
            suggestions.append("Try HDR lighting for enhanced dynamic range")
        
        if params.get('texture_quality', 0.9) < 0.9:
            suggestions.append("Increase texture quality to 0.9+ for production assets")
        
        if params.get('bit_depth', 16) < 16:
            suggestions.append("Use 16-bit depth for professional post-production")
        
        return suggestions