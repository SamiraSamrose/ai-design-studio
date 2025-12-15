# AI-Driven Industrial Product Design Studio

A full-stack visual AI system for industrial design teams to generate, iterate and refine product designs with HDR 16-bit quality using FIBO + ComfyUI + Nuke.

## Features

- **FIBO Integration**: Generate base product designs via FAL.AI, Bria.ai, and Replicate APIs
- **ComfyUI Workflows**: Iterative refinement with Generate and Refine nodes
- **Nuke Export**: Professional HDR 16-bit post-production scripts
- **Agentic Workflow**: Parallel design generation with multiple AI agents
- **JSON-Native Control**: Parameterized design attributes with real-time updates
- **Multimodal Control**: Independent control of lighting, camera, composition, and materials
- **Visual Comparison**: Side-by-side comparison panel with quality scoring
- **Manufacturability Analysis**: AI-driven production feasibility assessment

## Links

- **Site Demo**: https://samirasamrose.github.io/ai-design-studio/
- **Source Code**: https://github.com/SamiraSamrose/ai-design-studio
- **Video Demo**: https://youtu.be/j7YiqAua7pw


## Technology Stack

**Languages**: Python, JavaScript, HTML5, CSS3
**Frameworks**: Flask, asyncio
**Libraries**: Pillow, OpenCV, NumPy, aiohttp, Pydantic, requests
**Frontend**: Vanilla JavaScript, CSS Grid, Flexbox
**APIs**: FAL.AI FIBO API, Bria.ai Image Generation API, Replicate API, Runware API
**AI Models**: FIBO (Bria AI generative model)
**Tools**: ComfyUI (node-based workflow), Nuke (compositing software)
**Services**: FAL.AI, Bria.ai, Replicate, Runware
**Agents**: Variant suggestion agent, consistency check agent, quality scoring agent, manufacturability analysis agent
**Technologies**: REST API, JSON-native control, HDR image processing, 16-bit color depth conversion, async parallel processing
**Data Integrations**: API-based image generation services, file system storage
**Datasets**: User-provided design parameters, generated image metadata, JSON configuration files

## Usages of the Project:

- Generate product renderings for automotive designs
- Create marketing assets for consumer electronics
- Produce visualization for industrial hardware prototypes
- Generate multiple design variants for A/B testing
- Export production-ready Nuke scripts for compositing teams
- Validate design manufacturability before prototyping
- Build storyboards for product presentations
- Compare design iterations side-by-side
- Refine existing designs iteratively
- Convert natural language descriptions to structured design parameters
- Analyze consistency across design collections
- Select optimal compositions automatically
- Generate HDR-quality images for print and digital media
- Create color and material variations without regeneration
- Integrate AI-generated assets into professional post-production pipelines


## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys for FAL.AI, Bria.ai, Replicate (optional: Runware)

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/samirasamrose/ai-design-studio.git
cd ai-design-studio
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
````
FAL_API_KEY=your_fal_api_key
BRIA_API_KEY=your_bria_api_key
REPLICATE_API_KEY=your_replicate_api_key
RUNWARE_API_KEY=your_runware_api_key
DEBUG=True
````

5. **Create output directories:**

bashmkdir -p generated_designs refined_designs comparisons nuke_scripts temp exports

## Running the Application

### Start the Backend Server


bashcd backend
python app.py
The server will start on http://localhost:5000
Alternative: Use the Run Script
bashchmod +x run.sh
./run.sh
````

### Access the Dashboard

Open your browser and navigate to:
````
http://localhost:5000

## Usage Guide

### Basic Design Generation

- Enter Product Description: Describe your product in natural language
- Select Product Type: Choose from automotive, electronics, or appliance
- Configure Parameters:
  - Camera Angle (front, side, three-quarter, isometric, top)
  - Lighting Setup (studio, HDR, dramatic, natural, soft)
  - Material (metal, plastic, glass, carbon fiber, leather)
  - FOV, Reflectivity, Texture Quality
- Click "Generate Design": Wait for FIBO to generate your design
- View Results: Design appears in preview panel with metadata

### Advanced Features

Generate Variants with Parallel Agents
Click "Generate Variants" to create multiple design perspectives simultaneously:

- AI agent suggests optimal camera angles and lighting
- Multiple agents execute parallel API calls
- Consistency scoring across all variants
- Reduces iteration time by 4-6x

### Refine Existing Designs

Generate a base design
Click "Refine Design"
Enter refinement instructions (e.g., "enhance details", "adjust lighting")
ComfyUI executes refinement workflow

### Visual Comparison

Generate multiple variants
Select 2+ variants by clicking on cards
Click "Compare Variants"
View side-by-side comparison
Optional: Download Nuke comparison script

### AI Select Best Composition

Generate variants
Click "AI Select Best"
AI agent scores each variant based on:

Camera angle effectiveness
Lighting quality
Technical metrics
Composition rules


View selected design with reasoning

### Export to Nuke

Generate design
Click "Export to Nuke"
Download professional Nuke script with:

HDR color pipeline
16-bit processing nodes
JSON parameter preservation
Compositor-friendly controls



### Manufacturability Check

Generate design
Click "Check Manufacturability"
Receive AI analysis:

Production feasibility
Complexity scoring
Manufacturing methods
Cost estimation
Design recommendations



## API Documentation
POST /api/generate
Generate new product design
Request Body:
````
json{
  "prompt": "Modern electric sedan",
  "product_type": "car",
  "camera_angle": "three_quarter",
  "lighting": "studio",
  "material": "metal",
  "fov": 50.0,
  "reflectivity": 0.8,
  "texture_quality": 0.9,
  "width": 1024,
  "height": 1024,
  "hdr_enabled": true,
  "bit_depth": 16,
  "api_provider": "fal"
}
````
Response:
````
json{
  "success": true,
  "design_id": "20250101_120000_abc123",
  "filepath": "./generated_designs/design_20250101_120000_abc123.png",
  "image_url": "/api/images/design_20250101_120000_abc123.png",
  "parameters": {...},
  "metadata": {...}
}
````
POST /api/refine

Refine existing design
Request Body:
````
json{
  "image_id": "20250101_120000_abc123",
  "refinement_prompt": "Enhance details and increase sharpness",
  "strength": 0.7,
  "preserve_composition": true,
  "enhance_details": true
}
````
POST /api/variants

Generate multiple variants with parallel agents
Request Body:
````
json{
  "base_params": {...},
  "num_variants": 6
}
````
POST /api/select-best

AI agent selects best composition
Request Body:
````
json{
  "designs": [...]
}
````
POST /api/comparison


Create visual comparison panel
Request Body:
````
json{
  "design_ids": ["id1", "id2", "id3"]
}
POST /api/export-nuke
````

Export Nuke script with HDR workflow
Request Body:
````
json{
  "design_id": "20250101_120000_abc123",
  "config": {
    "export_format": "exr",
    "color_space": "linear",
    "bit_depth": 16
  }
}
POST /api/manufacturability
````
Analyze design for manufacturability
Request Body:
````
json{
  "design_data": {...}
}
````


### Configuration
API Providers
Configure which API to use in .env:

- FAL.AI: Best for production speed and reliability
- Bria.ai: Advanced HDR and material control
- Replicate: Scalable distributed rendering

Output Settings

- Modify in config.py:
- pythonDEFAULT_WIDTH= 1024
- DEFAULT_HEIGHT = 1024
- MAX_PARALLEL_AGENTS = 4
- HDR_BIT_DEPTH = 16

## Troubleshooting

### API Connection Issues

- Verify API keys in `.env`
- Check network connectivity
- Ensure API services are not rate-limited

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Port Already in Use

Change port in `config.py`:
```python
PORT = 5001  # Change from 5000
```

## Performance Optimization

- **Parallel Agents**: Adjust `MAX_PARALLEL_AGENTS` based on API rate limits
- **Image Resolution**: Lower resolution for faster iteration
- **HDR Processing**: Disable for non-production previews

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

MIT License - see LICENSE file for details


## Acknowledgments

- FIBO by Bria.ai for advanced image generation
- ComfyUI for node-based workflows
- Nuke by Foundry for professional compositing
