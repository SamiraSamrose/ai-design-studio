class APIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async generateDesign(params) {
        return this.request('/api/generate', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    }

    async refineDesign(imageId, refinementPrompt, strength = 0.7) {
        return this.request('/api/refine', {
            method: 'POST',
            body: JSON.stringify({
                image_id: imageId,
                refinement_prompt: refinementPrompt,
                strength: strength
            })
        });
    }

    async generateVariants(baseParams, numVariants = 4) {
        return this.request('/api/variants', {
            method: 'POST',
            body: JSON.stringify({
                base_params: baseParams,
                num_variants: numVariants
            })
        });
    }

    async selectBest(designs) {
        return this.request('/api/select-best', {
            method: 'POST',
            body: JSON.stringify({ designs })
        });
    }

    async createComparison(designIds) {
        return this.request('/api/comparison', {
            method: 'POST',
            body: JSON.stringify({ design_ids: designIds })
        });
    }

    async exportNuke(designId, config = {}) {
        return this.request('/api/export-nuke', {
            method: 'POST',
            body: JSON.stringify({ design_id: designId, config })
        });
    }

    async checkManufacturability(designData) {
        return this.request('/api/manufacturability', {
            method: 'POST',
            body: JSON.stringify({ design_data: designData })
        });
    }

    getImageURL(filename) {
        return `${this.baseURL}/api/images/${filename}`;
    }
}

const apiClient = new APIClient();
