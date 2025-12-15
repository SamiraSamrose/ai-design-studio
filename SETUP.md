# Detailed Setup Guide

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for parallel generation)
- 2GB free disk space for generated designs
- Internet connection for API access

## Step-by-Step Installation

### 1. Environment Setup

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. API Key Configuration

Obtain API keys from:

- **FAL.AI**: https://fal.ai/dashboard
- **Bria.ai**: https://bria.ai/api
- **Replicate**: https://replicate.com/account
- **Runware** (optional): https://runware.ai

Create `.env` file:
```bash
cp .env.example .env
nano .env  # or use any text editor
```

Add your keys:
```
FAL_API_KEY=fal-xxxxxxxxxxxxxxxx
BRIA_API_KEY=bria_xxxxxxxxxxxxxxxx
REPLICATE_API_KEY=r8_xxxxxxxxxxxxxxxx
RUNWARE_API_KEY=rw_xxxxxxxxxxxxxxxx
```

### 4. Verify Installation
```bash
python app.py
```

Visit `http://localhost:5000` to confirm server is running.

## ComfyUI Integration (Optional)

For local ComfyUI workflows:

1. Install ComfyUI: https://github.com/comfyanonymous/ComfyUI
2. Install Bria nodes: https://github.com/Bria-AI/ComfyUI-BRIA-API
3. Update `comfyui_service.py` with your ComfyUI URL

## Nuke Integration

The system generates Nuke scripts automatically. To use:

1. Install Nuke (https://www.foundry.com/products/nuke)
2. Open generated `.nk` files in Nuke
3. Adjust parameters as needed
4. Render final output

## Troubleshooting

### ImportError: No module named 'flask'
```bash
pip install flask
```

### API Authentication Failed

- Verify API keys are correct
- Check API key has sufficient credits
- Ensure no leading/trailing spaces in `.env`

### Port 5000 Already in Use

Edit `config.py`:
```python
PORT = 5001
```

## Next Steps

See `USER_GUIDE.md` for usage instructions.