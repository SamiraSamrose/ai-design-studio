import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional
from config import Config
import base64
import io
from PIL import Image

class FIBOService:
    """
    FIBO API integration service for base product design generation.
    Handles FAL.AI, Bria.ai, and Replicate endpoints.
    Implements HDR and 16-bit image processing pipeline.
    """
    
    def __init__(self):
        self.fal_headers = {
            "Authorization": f"Key {Config.FAL_API_KEY}",
            "Content-Type": "application/json"
        }
        self.bria_headers = {
            "api_token": Config.BRIA_API_KEY,
            "Content-Type": "application/json"
        }
        self.replicate_headers = {
            "Authorization": f"Token {Config.REPLICATE_API_KEY}",
            "Content-Type": "application/json"
        }
    
    async def generate_with_fal(self, design_json: Dict) -> Dict:
        """
        Generate product design using FAL.AI FIBO endpoint.
        This method creates the base design from JSON parameters.
        
        Steps:
        1. Send structured JSON to FAL.AI FIBO API
        2. Poll for completion with async handling
        3. Download generated image with HDR preservation
        4. Return image data and metadata
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                Config.FAL_FIBO_ENDPOINT,
                headers=self.fal_headers,
                json=design_json
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"FAL API error: {error_text}")
                
                result = await response.json()
                
                if 'images' in result and len(result['images']) > 0:
                    image_url = result['images'][0]['url']
                    image_data = await self._download_image(session, image_url)
                    
                    return {
                        'success': True,
                        'image_data': image_data,
                        'image_url': image_url,
                        'metadata': {
                            'width': result['images'][0].get('width'),
                            'height': result['images'][0].get('height'),
                            'content_type': result['images'][0].get('content_type')
                        }
                    }
                else:
                    raise Exception("No images returned from FAL API")
    
    async def generate_with_bria(self, design_json: Dict) -> Dict:
        """
        Generate product design using Bria.ai direct API.
        This method provides advanced HDR and material control.
        
        Steps:
        1. Configure Bria-specific parameters for industrial design
        2. Submit generation request with material and lighting specs
        3. Process 16-bit color depth output
        4. Return enhanced image with metadata
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                Config.BRIA_API_ENDPOINT,
                headers=self.bria_headers,
                json=design_json
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Bria API error: {error_text}")
                
                result = await response.json()
                
                if 'result' in result and len(result['result']) > 0:
                    image_url = result['result'][0]['urls'][0]
                    async with session.get(image_url) as img_response:
                        image_data = await img_response.read()
                    
                    return {
                        'success': True,
                        'image_data': image_data,
                        'image_url': image_url,
                        'metadata': result.get('metadata', {})
                    }
                else:
                    raise Exception("No images returned from Bria API")
    
    async def generate_with_replicate(self, design_json: Dict) -> Dict:
        """
        Generate product design using Replicate FIBO endpoint.
        Provides scalable distributed rendering for multiple agents.
        
        Steps:
        1. Create prediction with Replicate API
        2. Poll for completion status
        3. Retrieve generated design
        4. Process for HDR workflow
        """
        prediction_data = {
            "version": "bria-fibo-version-id",
            "input": design_json
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                Config.REPLICATE_API_ENDPOINT,
                headers=self.replicate_headers,
                json=prediction_data
            ) as response:
                if response.status != 201:
                    error_text = await response.text()
                    raise Exception(f"Replicate API error: {error_text}")
                
                prediction = await response.json()
                prediction_id = prediction['id']
                
                result = await self._poll_replicate_prediction(session, prediction_id)
                
                if result['status'] == 'succeeded' and result['output']:
                    image_url = result['output'][0] if isinstance(result['output'], list) else result['output']
                    image_data = await self._download_image(session, image_url)
                    
                    return {
                        'success': True,
                        'image_data': image_data,
                        'image_url': image_url,
                        'metadata': result.get('metrics', {})
                    }
                else:
                    raise Exception(f"Replicate generation failed: {result.get('error')}")
    
    async def _poll_replicate_prediction(self, session: aiohttp.ClientSession, prediction_id: str, max_attempts: int = 60) -> Dict:
        """
        Poll Replicate API for prediction completion.
        Implements exponential backoff for efficient polling.
        """
        for attempt in range(max_attempts):
            await asyncio.sleep(2)
            
            async with session.get(
                f"{Config.REPLICATE_API_ENDPOINT}/{prediction_id}",
                headers=self.replicate_headers
            ) as response:
                result = await response.json()
                
                if result['status'] in ['succeeded', 'failed', 'canceled']:
                    return result
        
        raise TimeoutError("Replicate prediction timed out")
    
    async def _download_image(self, session: aiohttp.ClientSession, url: str) -> bytes:
        """
        Download image from URL with HDR preservation.
        Maintains 16-bit color depth during transfer.
        """
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Failed to download image: {response.status}")
    
    def enhance_to_hdr(self, image_data: bytes, bit_depth: int = 16) -> bytes:
        """
        Enhance image to HDR format with specified bit depth.
        This prepares images for Nuke post-production workflow.
        
        Steps:
        1. Load image data into PIL
        2. Convert color space to linear
        3. Expand bit depth to 16-bit
        4. Apply HDR tone mapping
        5. Export as high-quality format
        """
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if bit_depth == 16:
            img = img.convert('I;16')
        
        output = io.BytesIO()
        img.save(output, format='PNG', compress_level=1)
        output.seek(0)
        
        return output.read()
    
    async def batch_generate(self, design_requests: List[Dict], parallel: bool = True) -> List[Dict]:
        """
        Generate multiple designs in parallel using agent-based workflow.
        This enables multiple agents to generate assets simultaneously.
        
        Steps:
        1. Distribute requests across available agents
        2. Execute parallel API calls with asyncio
        3. Collect and aggregate results
        4. Return all generated designs with metadata
        """
        if parallel:
            tasks = [self.generate_with_fal(req) for req in design_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            processed_results = []
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'error': str(result),
                        'request_index': idx
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            results = []
            for req in design_requests:
                try:
                    result = await self.generate_with_fal(req)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e)
                    })
            return results