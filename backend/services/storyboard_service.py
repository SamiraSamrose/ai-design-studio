import asyncio
from typing import Dict, List, Optional
from .fibo_service import FIBOService
from .nuke_service import NukeService
import json

class StoryboardService:
    """
    Handles drag-and-drop storyboard workflow with AI translation.
    Implements Point 9: storyboard → AI translation → HDR preview → Nuke nodes.
    """
    
    def __init__(self):
        self.fibo_service = FIBOService()
        self.nuke_service = NukeService()
    
    async def translate_storyboard(self, storyboard_sequence: List[Dict]) -> Dict:
        """
        AI agent translates storyboard sequence into production parameters.
        Analyzes frame order, transitions, and narrative flow.
        
        Steps:
        1. Parse storyboard sequence and frame metadata
        2. Identify narrative progression patterns
        3. Generate optimized parameters for each frame
        4. Suggest transition effects and timing
        5. Return translated storyboard with AI enhancements
        """
        translated_frames = []
        
        for idx, frame in enumerate(storyboard_sequence):
            frame_position = idx / max(len(storyboard_sequence) - 1, 1)
            
            base_params = frame.get('params', {})
            
            if idx == 0:
                translated_params = {
                    **base_params,
                    'camera_angle': 'three_quarter',
                    'lighting': 'soft',
                    'composition_focus': 'centered',
                    'narrative_role': 'establishing_shot'
                }
            elif idx == len(storyboard_sequence) - 1:
                translated_params = {
                    **base_params,
                    'camera_angle': 'front',
                    'lighting': 'dramatic',
                    'composition_focus': 'centered',
                    'narrative_role': 'hero_shot'
                }
            else:
                translated_params = {
                    **base_params,
                    'camera_angle': self._progressive_camera_angle(frame_position),
                    'lighting': self._progressive_lighting(frame_position),
                    'composition_focus': 'dynamic',
                    'narrative_role': 'detail_shot'
                }
            
            transition = self._suggest_transition(idx, len(storyboard_sequence))
            
            translated_frames.append({
                'frame_number': idx + 1,
                'original_params': base_params,
                'translated_params': translated_params,
                'transition': transition,
                'duration_suggestion': self._suggest_duration(idx, len(storyboard_sequence)),
                'ai_notes': self._generate_frame_notes(translated_params, idx)
            })
        
        return {
            'success': True,
            'translated_frames': translated_frames,
            'total_frames': len(translated_frames),
            'estimated_duration': sum(f['duration_suggestion'] for f in translated_frames),
            'narrative_structure': self._analyze_narrative_structure(translated_frames)
        }
    
    def _progressive_camera_angle(self, position: float) -> str:
        """Determine camera angle based on position in sequence"""
        if position < 0.33:
            return 'side'
        elif position < 0.66:
            return 'three_quarter'
        else:
            return 'isometric'
    
    def _progressive_lighting(self, position: float) -> str:
        """Determine lighting based on position in sequence"""
        if position < 0.25:
            return 'soft'
        elif position < 0.5:
            return 'studio'
        elif position < 0.75:
            return 'hdr'
        else:
            return 'dramatic'
    
    def _suggest_transition(self, frame_index: int, total_frames: int) -> str:
        """Suggest transition effect between frames"""
        if frame_index == 0:
            return 'fade_in'
        elif frame_index == total_frames - 1:
            return 'fade_out'
        elif frame_index % 3 == 0:
            return 'cross_dissolve'
        else:
            return 'cut'
    
    def _suggest_duration(self, frame_index: int, total_frames: int) -> float:
        """Suggest frame duration in seconds"""
        if frame_index == 0 or frame_index == total_frames - 1:
            return 3.0
        else:
            return 2.0
    
    def _generate_frame_notes(self, params: Dict, frame_index: int) -> str:
        """Generate AI notes for each frame"""
        notes = []
        
        if params.get('narrative_role') == 'establishing_shot':
            notes.append("Opens sequence with contextual overview")
        elif params.get('narrative_role') == 'hero_shot':
            notes.append("Concludes with impactful final composition")
        else:
            notes.append("Provides detailed product perspective")
        
        lighting = params.get('lighting', 'studio')
        notes.append(f"Lighting progression to {lighting} maintains visual flow")
        
        camera = params.get('camera_angle', 'three_quarter')
        notes.append(f"Camera angle {camera} reveals key product features")
        
        return '. '.join(notes)
    
    def _analyze_narrative_structure(self, frames: List[Dict]) -> Dict:
        """Analyze overall narrative structure of storyboard"""
        structure = {
            'pacing': 'steady',
            'visual_progression': 'linear',
            'climax_frame': len(frames) - 1,
            'key_moments': []
        }
        
        for idx, frame in enumerate(frames):
            if frame['translated_params'].get('lighting') == 'dramatic':
                structure['key_moments'].append({
                    'frame': idx + 1,
                    'type': 'dramatic_emphasis'
                })
            
            if frame['translated_params'].get('camera_angle') == 'front':
                structure['key_moments'].append({
                    'frame': idx + 1,
                    'type': 'direct_engagement'
                })
        
        return structure
    
    async def generate_storyboard_preview(self, translated_storyboard: Dict) -> Dict:
        """
        Generate preview panel with HDR and 16-bit fidelity for storyboard.
        Creates complete sequence ready for final rendering.
        
        Steps:
        1. Extract translated parameters for each frame
        2. Generate images for all frames in parallel
        3. Apply HDR processing to maintain quality
        4. Create preview sequence with timing
        5. Return preview data with playback information
        """
        frames = translated_storyboard.get('translated_frames', [])
        
        generation_tasks = []
        for frame in frames:
            params = frame['translated_params']
            design_json = {
                "prompt": params.get('prompt', ''),
                "image_size": {
                    "width": params.get('width', 1024),
                    "height": params.get('height', 1024)
                },
                "num_images": 1,
                "sync_mode": True,
                "enable_safety_checks": True
            }
            generation_tasks.append(self.fibo_service.generate_with_fal(design_json))
        
        results = await asyncio.gather(*generation_tasks, return_exceptions=True)
        
        preview_frames = []
        for idx, (frame, result) in enumerate(zip(frames, results)):
            if isinstance(result, Exception):
                preview_frames.append({
                    'success': False,
                    'frame_number': frame['frame_number'],
                    'error': str(result)
                })
            else:
                hdr_image = self.fibo_service.enhance_to_hdr(result['image_data'], 16)
                
                from utils.helpers import save_image, generate_unique_id
                filename = f"storyboard_frame_{frame['frame_number']}_{generate_unique_id()}.png"
                filepath = save_image(hdr_image, 'generated_designs', filename)
                
                preview_frames.append({
                    'success': True,
                    'frame_number': frame['frame_number'],
                    'image_path': filepath,
                    'duration': frame['duration_suggestion'],
                    'transition': frame['transition'],
                    'hdr_processed': True,
                    'bit_depth': 16
                })
        
        return {
            'success': True,
            'preview_frames': preview_frames,
            'total_duration': sum(f.get('duration', 0) for f in preview_frames if f.get('success')),
            'hdr_enabled': True,
            'bit_depth': 16
        }
    
    async def export_storyboard_to_nuke(self, storyboard_preview: Dict, storyboard_name: str) -> Dict:
        """
        Export storyboard as Nuke-ready nodes with sequence controls.
        Generates complete compositing script with timing and transitions.
        
        Steps:
        1. Collect all frame image paths
        2. Generate Nuke script with Read nodes for each frame
        3. Add TimeClip nodes for frame duration control
        4. Insert Dissolve nodes for transitions
        5. Configure Write node for sequence export
        6. Return Nuke script with embedded storyboard data
        """
        frames = storyboard_preview.get('preview_frames', [])
        successful_frames = [f for f in frames if f.get('success')]
        
        if not successful_frames:
            return {
                'success': False,
                'message': 'No successful frames to export'
            }
        
        nuke_script = self._generate_storyboard_nuke_script(successful_frames, storyboard_name)
        
        from utils.helpers import generate_unique_id
        import os
        script_path = os.path.join('nuke_scripts', f"storyboard_{storyboard_name}_{generate_unique_id()}.nk")
        
        with open(script_path, 'w') as f:
            f.write(nuke_script)
        
        return {
            'success': True,
            'nuke_script_path': script_path,
            'total_frames': len(successful_frames),
            'sequence_duration': storyboard_preview.get('total_duration', 0),
            'hdr_workflow': True
        }
    
    def _generate_storyboard_nuke_script(self, frames: List[Dict], name: str) -> str:
        """Generate complete Nuke script for storyboard sequence"""
        script = f"""#! Nuke Version 14.0
# AI-Driven Industrial Product Design Studio
# Storyboard Sequence: {name}
# HDR 16-bit Workflow with Transition Controls

set cut_paste_input [stack 0]
version 14.0 v5

"""
        
        current_frame = 1
        previous_node = None
        
        for idx, frame in enumerate(frames):
            frame_num = frame['frame_number']
            image_path = frame['image_path']
            duration = int(frame['duration'] * 24)
            transition = frame['transition']
            
            read_node = f"""
Read {{
 inputs 0
 file {image_path}
 format "1024 1024 0 0 1024 1024 1 square_1K"
 origset true
 colorspace linear
 name Read_Frame_{frame_num}
 xpos {idx * 150}
 ypos 0
}}

TimeClip {{
 first {current_frame}
 last {current_frame + duration - 1}
 name TimeClip_Frame_{frame_num}
 xpos {idx * 150}
 ypos 50
}}

Colorspace {{
 colorspace_in linear
 colorspace_out AlexaV3LogC
 name ColorSpace_HDR_Frame_{frame_num}
 xpos {idx * 150}
 ypos 100
}}
"""
            script += read_node
            
            if previous_node and transition in ['cross_dissolve', 'fade_in', 'fade_out']:
                dissolve_node = f"""
Dissolve {{
 inputs 2
 which 0.5
 name Dissolve_{frame_num}
 xpos {idx * 150}
 ypos 150
}}
"""
                script += dissolve_node
            
            current_frame += duration
            previous_node = f"ColorSpace_HDR_Frame_{frame_num}"
        
        script += f"""
Write {{
 file "{name}_sequence.exr"
 file_type exr
 datatype "16 bit half"
 compression "Zip (1 scanline)"
 colorspace linear
 create_directories true
 name Write_Sequence
 xpos 300
 ypos 250
}}
"""
        
        return script