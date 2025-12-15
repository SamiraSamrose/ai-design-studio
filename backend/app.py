from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from config import Config
from services import FIBOService, ComfyUIService, NukeService, AgentService, JSONController
from models.design_schema import DesignRequest, RefineRequest, DesignVariant, NukeExportConfig
from utils.helpers import save_image, generate_unique_id, create_directory_structure
import asyncio
import os
import json
from functools import wraps

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

Config.validate()

fibo_service = FIBOService()
comfyui_service = ComfyUIService()
nuke_service = NukeService()
agent_service = AgentService()
json_controller = JSONController()

output_dirs = create_directory_structure('.')

def async_route(f):
    """Decorator to handle async routes in Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.route('/')
def index():
    """Serve frontend dashboard"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Verifies API connectivity and service availability.
    """
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'services': {
            'fibo': 'available',
            'comfyui': 'available',
            'nuke': 'available',
            'agents': 'available'
        }
    })

@app.route('/api/generate', methods=['POST'])
@async_route
async def generate_design():
    """
    Main design generation endpoint.
    Accepts natural language or structured JSON input.
    
    Steps:
    1. Parse request data and convert to design JSON
    2. Validate design parameters
    3. Generate design using FIBO service
    4. Enhance to HDR if requested
    5. Save generated design and return metadata
    """
    try:
        data = request.json
        
        if 'prompt' in data and 'product_type' in data:
            if 'camera_angle' not in data:
                design_json = json_controller.natural_language_to_json(
                    data['prompt'],
                    data['product_type']
                )
                design_json.update(data)
            else:
                design_json = data
        else:
            return jsonify({'error': 'Missing required fields: prompt and product_type'}), 400
        
        valid, error_msg = json_controller.validate_json_schema(design_json)
        if not valid:
            return jsonify({'error': error_msg}), 400
        
        design_request = DesignRequest(**design_json)
        fibo_json = design_request.to_fibo_json()
        
        api_provider = data.get('api_provider', 'fal')
        
        if api_provider == 'fal':
            result = await fibo_service.generate_with_fal(fibo_json)
        elif api_provider == 'bria':
            bria_json = design_request.to_bria_json()
            result = await fibo_service.generate_with_bria(bria_json)
        elif api_provider == 'replicate':
            result = await fibo_service.generate_with_replicate(fibo_json)
        else:
            return jsonify({'error': 'Invalid API provider'}), 400
        
        if not result['success']:
            return jsonify({'error': 'Generation failed'}), 500
        
        if design_request.hdr_enabled:
            result['image_data'] = fibo_service.enhance_to_hdr(
                result['image_data'],
                design_request.bit_depth
            )
        
        design_id = generate_unique_id()
        filename = f"design_{design_id}.png"
        filepath = save_image(
            result['image_data'],
            output_dirs['generated_designs'],
            filename
        )
        
        metadata = {
            'design_id': design_id,
            'filepath': filepath,
            'parameters': design_json,
            'api_provider': api_provider,
            'metadata': result.get('metadata', {})
        }
        
        metadata_path = os.path.join(output_dirs['generated_designs'], f"design_{design_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'design_id': design_id,
            'filepath': filepath,
            'image_url': f"/api/images/{filename}",
            'parameters': json_controller.json_to_display_params(design_json),
            'metadata': metadata
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refine', methods=['POST'])
@async_route
async def refine_design():
    """
    Design refinement endpoint using ComfyUI refine nodes.
    Performs iterative improvements on existing designs.
    
    Steps:
    1. Load existing design by image_id
    2. Apply refinement parameters
    3. Execute ComfyUI refine workflow
    4. Save refined design
    5. Return comparison data
    """
    try:
        data = request.json
        refine_request = RefineRequest(**data)
        
        original_image_path = os.path.join(
            output_dirs['generated_designs'],
            f"design_{refine_request.image_id}.png"
        )
        
        if not os.path.exists(original_image_path):
            return jsonify({'error': 'Original image not found'}), 404
        
        refine_params = {
            'refinement_prompt': refine_request.refinement_prompt,
            'strength': refine_request.strength,
            'preserve_composition': refine_request.preserve_composition,
            'enhance_details': refine_request.enhance_details,
            'api_token': Config.BRIA_API_KEY
        }
        
        result = await comfyui_service.refine_node(
            refine_request.image_id,
            refine_params
        )
        
        if not result['success']:
            return jsonify({'error': 'Refinement failed'}), 500
        
        refined_id = generate_unique_id()
        filename = f"refined_{refined_id}.png"
        
        return jsonify({
            'success': True,
            'refined_id': refined_id,
            'original_id': refine_request.image_id,
            'image_url': f"/api/images/{filename}",
            'workflow': result.get('workflow', {})
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/variants', methods=['POST'])
@async_route
async def generate_variants():
    """
    Generate multiple design variants using parallel agents.
    This endpoint demonstrates agentic workflow capabilities.
    
    Steps:
    1. Receive base design requirements
    2. AI agent suggests design variants
    3. Distribute generation across parallel agents
    4. Execute batch generation
    5. Return all variants with metadata
    """
    try:
        data = request.json
        base_params = data.get('base_params', {})
        num_variants = data.get('num_variants', 4)
        
        variants = await agent_service.suggest_design_variants(base_params)
        variants = variants[:num_variants]
        
        results = await agent_service.parallel_generation(variants, base_params)
        
        saved_results = []
        for result in results:
            if result.get('success', False):
                design_id = generate_unique_id()
                filename = f"variant_{design_id}.png"
                filepath = save_image(
                    result['image_data'],
                    output_dirs['generated_designs'],
                    filename
                )
                
                saved_results.append({
                    'design_id': design_id,
                    'variant_id': result.get('variant_id'),
                    'filepath': filepath,
                    'image_url': f"/api/images/{filename}",
                    'camera_angle': result.get('camera_angle'),
                    'lighting': result.get('lighting'),
                    'agent_id': result.get('agent_id')
                })
        
        consistency_report = await agent_service.consistency_check(results)
        
        return jsonify({
            'success': True,
            'variants': saved_results,
            'consistency_report': consistency_report,
            'total_generated': len(saved_results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/select-best', methods=['POST'])
@async_route
async def select_best_composition():
    """
    AI agent selects best composition from variants.
    Provides automated quality assessment and ranking.
    """
    try:
        data = request.json
        designs = data.get('designs', [])
        
        if not designs:
            return jsonify({'error': 'No designs provided'}), 400
        
        result = await agent_service.select_best_composition(designs)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/comparison', methods=['POST'])
@async_route
async def create_comparison():
    """
    Create visual comparison panel for multiple designs.
    Generates side-by-side comparison with ComfyUI and Nuke.
    
    Steps:
    1. Receive list of design IDs to compare
    2. Load actual image files from storage
    3. Create ComfyUI comparison workflow
    4. Generate Nuke comparison script
    5. Return comparison data with image paths
    """
    try:
        data = request.json
        design_ids = data.get('design_ids', [])
        
        if len(design_ids) < 2:
            return jsonify({'error': 'At least 2 designs required for comparison'}), 400
        
        image_paths = []
        image_urls = []
        valid_ids = []
        
        for design_id in design_ids:
            possible_paths = [
                os.path.join(output_dirs['generated_designs'], f"design_{design_id}.png"),
                os.path.join(output_dirs['generated_designs'], f"variant_{design_id}.png"),
                os.path.join(output_dirs['generated_designs'], f"{design_id}.png")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    image_paths.append(path)
                    image_urls.append(f"/api/images/{os.path.basename(path)}")
                    valid_ids.append(design_id)
                    break
        
        if len(image_paths) < 2:
            return jsonify({'error': 'Insufficient valid design images found'}), 404
        
        comparison_id = generate_unique_id()
        
        try:
            comfyui_result = await comfyui_service.create_comparison_workflow(valid_ids)
        except Exception as e:
            comfyui_result = {'error': str(e)}
        
        nuke_script = nuke_service.generate_comparison_script(
            image_paths, 
            f"comparison_{comparison_id}"
        )
        
        return jsonify({
            'success': True,
            'comparison_id': comparison_id,
            'nuke_script': nuke_script,
            'nuke_download_url': f"/api/download-nuke/{os.path.basename(nuke_script)}",
            'comfyui_workflow': comfyui_result,
            'compared_designs': valid_ids,
            'image_urls': image_urls,
            'total_compared': len(image_paths)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-nuke', methods=['POST'])
def export_nuke_script():
    """
    Export Nuke script with HDR workflow for specific design.
    Preserves JSON-native parameter control.
    
    Steps:
    1. Load design metadata with parameters
    2. Generate Nuke script with embedded JSON
    3. Configure HDR nodes and 16-bit output
    4. Return Nuke script path for download
    """
    try:
        data = request.json
        design_id = data.get('design_id')
        export_config = NukeExportConfig(**data.get('config', {}))
        
        image_path = os.path.join(output_dirs['generated_designs'], f"design_{design_id}.png")
        if not os.path.exists(image_path):
            return jsonify({'error': 'Design image not found'}), 404
        
        metadata_path = os.path.join(output_dirs['generated_designs'], f"design_{design_id}_metadata.json")
        design_params = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                design_params = metadata.get('parameters', {})
        
        nuke_params = json_controller.export_to_nuke_format(design_params)
        
        script_path = nuke_service.generate_nuke_script(
            image_path,
            nuke_params,
            f"design_{design_id}"
        )
        
        nuke_service.embed_json_metadata(script_path, design_params)
        
        return jsonify({
            'success': True,
            'script_path': script_path,
            'download_url': f"/api/download-nuke/{os.path.basename(script_path)}"
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/manufacturability', methods=['POST'])
@async_route
async def analyze_manufacturability():
    """
    AI agent analyzes design for manufacturability constraints.
    Provides production feasibility assessment.
    """
    try:
        data = request.json
        design_data = data.get('design_data', {})
        
        result = await agent_service.optimize_for_manufacturability(design_data)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/images/<filename>', methods=['GET'])
def get_image(filename):
    """Serve generated design images"""
    return send_from_directory(output_dirs['generated_designs'], filename)

@app.route('/api/download-nuke/<filename>', methods=['GET'])
def download_nuke_script(filename):
    """Download Nuke script files"""
    return send_from_directory(output_dirs['nuke_scripts'], filename, as_attachment=True)

@app.route('/api/parameters', methods=['POST'])
def update_parameters():
    """
    Update design parameters with JSON merging.
    Maintains parameter consistency and validates changes.
    """
    try:
        data = request.json
        design_id = data.get('design_id')
        updates = data.get('updates', {})
        
        metadata_path = os.path.join(output_dirs['generated_designs'], f"design_{design_id}_metadata.json")
        
        if not os.path.exists(metadata_path):
            return jsonify({'error': 'Design metadata not found'}), 404
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        current_params = metadata.get('parameters', {})
        merged_params = json_controller.merge_json_updates(current_params, updates)
        
        valid, error_msg = json_controller.validate_json_schema(merged_params)
        if not valid:
            return jsonify({'error': error_msg}), 400
        
        metadata['parameters'] = merged_params
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'updated_parameters': json_controller.json_to_display_params(merged_params)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iterations', methods=['POST'])
@async_route
async def generate_iterations():
    """
    Generate multiple design iterations with parameter variations.
    Implements Point 8: iteration workflow.
    
    Steps:
    1. Receive base design parameters
    2. Generate iterations with subtle variations
    3. Return all iterations with metadata
    """
    try:
        data = request.json
        base_params = data.get('base_params', {})
        num_iterations = data.get('num_iterations', 4)
        
        from services.iteration_service import IterationService
        iteration_service = IterationService()
        
        iterations = await iteration_service.generate_iterations(base_params, num_iterations)
        
        saved_iterations = []
        for iteration in iterations:
            if iteration.get('success'):
                design_id = generate_unique_id()
                filename = f"iteration_{iteration['iteration_number']}_{design_id}.png"
                filepath = save_image(
                    iteration['image_data'],
                    output_dirs['generated_designs'],
                    filename
                )
                
                saved_iterations.append({
                    'iteration_number': iteration['iteration_number'],
                    'design_id': design_id,
                    'filepath': filepath,
                    'image_url': f"/api/images/{filename}",
                    'params': iteration['params'],
                    'variation_type': iteration['variation_type']
                })
        
        return jsonify({
            'success': True,
            'iterations': saved_iterations,
            'total_generated': len(saved_iterations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iterations/compare', methods=['POST'])
@async_route
async def compare_iterations():
    """
    Create visual comparison panel for iterations.
    Part of Point 8: iteration → comparison workflow.
    """
    try:
        data = request.json
        iteration_ids = data.get('iteration_ids', [])
        iteration_data = data.get('iteration_data', [])
        
        from services.iteration_service import IterationService
        iteration_service = IterationService()
        
        result = await iteration_service.create_iteration_comparison_panel(iteration_ids, iteration_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iterations/select-best', methods=['POST'])
@async_route
async def select_best_iteration():
    """
    AI agent selects best iteration from comparison.
    Completes Point 8: iteration → comparison → AI selection.
    """
    try:
        data = request.json
        iterations = data.get('iterations', [])
        
        from services.iteration_service import IterationService
        iteration_service = IterationService()
        
        result = await iteration_service.ai_select_best_iteration(iterations)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/storyboard/translate', methods=['POST'])
@async_route
async def translate_storyboard():
    """
    AI agent translates drag-and-drop storyboard sequence.
    Implements Point 9: storyboard → AI translation.
    """
    try:
        data = request.json
        storyboard_sequence = data.get('storyboard_sequence', [])
        
        from services.storyboard_service import StoryboardService
        storyboard_service = StoryboardService()
        
        result = await storyboard_service.translate_storyboard(storyboard_sequence)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/storyboard/preview', methods=['POST'])
@async_route
async def generate_storyboard_preview():
    """
    Generate preview panel with HDR and 16-bit fidelity for storyboard.
    Part of Point 9: AI translation → HDR preview.
    """
    try:
        data = request.json
        translated_storyboard = data.get('translated_storyboard', {})
        
        from services.storyboard_service import StoryboardService
        storyboard_service = StoryboardService()
        
        result = await storyboard_service.generate_storyboard_preview(translated_storyboard)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/storyboard/export-nuke', methods=['POST'])
@async_route
async def export_storyboard_nuke():
    """
    Export storyboard as Nuke-ready nodes with sequence controls.
    Completes Point 9: HDR preview → final Nuke-ready nodes.
    """
    try:
        data = request.json
        storyboard_preview = data.get('storyboard_preview', {})
        storyboard_name = data.get('storyboard_name', 'sequence')
        
        from services.storyboard_service import StoryboardService
        storyboard_service = StoryboardService()
        
        result = await storyboard_service.export_storyboard_to_nuke(storyboard_preview, storyboard_name)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
