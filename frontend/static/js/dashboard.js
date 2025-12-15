class Dashboard {
    constructor() {
        this.currentDesignId = null;
        this.currentDesignParams = null;
        this.initializeEventListeners();
        this.updateSliderValues();
        this.updateJSONPreview();
    }

    initializeEventListeners() {
        const sliders = ['fov', 'reflectivity', 'texture_quality'];
        sliders.forEach(id => {
            document.getElementById(id).addEventListener('input', (e) => {
                const suffix = id === 'fov' ? '°' : '%';
                document.getElementById(`${id}_value`).textContent = `${e.target.value}${suffix}`;
                this.updateJSONPreview();
            });
        });

        const colorInputs = ['color1', 'color2', 'color3'];
        colorInputs.forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateColorPalettePreview();
                this.updateJSONPreview();
            });
        });

        const formElements = document.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            element.addEventListener('change', () => this.updateJSONPreview());
        });

        document.getElementById('modal_cancel').addEventListener('click', () => {
            document.getElementById('modal_overlay').style.display = 'none';
        });
    }

    updateSliderValues() {
        document.getElementById('fov_value').textContent = `${document.getElementById('fov').value}°`;
        document.getElementById('reflectivity_value').textContent = `${document.getElementById('reflectivity').value}%`;
        document.getElementById('texture_quality_value').textContent = `${document.getElementById('texture_quality').value}%`;
    }

    updateColorPalettePreview() {
        const colors = [
            document.getElementById('color1').value,
            document.getElementById('color2').value,
            document.getElementById('color3').value
        ];

        const preview = document.getElementById('palette_preview');
        preview.style.background = `linear-gradient(to right, ${colors[0]} 0%, ${colors[0]} 33%, ${colors[1]} 33%, ${colors[1]} 66%, ${colors[2]} 66%, ${colors[2]} 100%)`;
    }

    updateJSONPreview() {
        const formData = this.getFormData();
        const jsonContent = document.getElementById('json_content');
        jsonContent.textContent = JSON.stringify(formData, null, 2);
        
        this.updateColorPalettePreview();
    }

    getFormData() {
        return {
            prompt: document.getElementById('prompt').value,
            product_type: document.getElementById('product_type').value,
            api_provider: document.getElementById('api_provider').value,
            camera_angle: document.getElementById('camera_angle').value,
            lighting: document.getElementById('lighting').value,
            material: document.getElementById('material').value,
            composition_focus: document.getElementById('composition_focus').value,
            fov: parseFloat(document.getElementById('fov').value),
            reflectivity: parseFloat(document.getElementById('reflectivity').value) / 100,
            texture_quality: parseFloat(document.getElementById('texture_quality').value) / 100,
            color_palette: [
                document.getElementById('color1').value,
                document.getElementById('color2').value,
                document.getElementById('color3').value
            ],
            background: document.getElementById('background').value,
            width: parseInt(document.getElementById('width').value),
            height: parseInt(document.getElementById('height').value),
            hdr_enabled: document.getElementById('hdr_enabled').checked,
            bit_depth: parseInt(document.getElementById('bit_depth').value)
        };
    }

    showLoading(message = 'Generating design...', subtext = '') {
        document.getElementById('loading_overlay').style.display = 'flex';
        document.getElementById('loading_text').textContent = message;
        document.getElementById('loading_subtext').textContent = subtext;
    }

    hideLoading() {
        document.getElementById('loading_overlay').style.display = 'none';
    }

    displayDesign(result) {
        this.currentDesignId = result.design_id;
        this.currentDesignParams = result.parameters;

        const previewContainer = document.getElementById('preview_container');
        previewContainer.innerHTML = `<img src="${result.image_url}" alt="Generated Design">`;

        document.getElementById('preview_controls').style.display = 'flex';

        this.displayMetadata(result.parameters, result.metadata);
    }

    displayMetadata(parameters, metadata) {
        const metadataContainer = document.getElementById('metadata_container');
        let html = '<div class="metadata-grid">';

        for (const [key, value] of Object.entries(parameters)) {
            html += `<p><strong>${key}:</strong> ${value}</p>`;
        }

        if (metadata && metadata.metadata) {
            html += '<hr style="margin: 15px 0;"><p><strong>Technical Metadata:</strong></p>';
            for (const [key, value] of Object.entries(metadata.metadata)) {
                html += `<p><strong>${key}:</strong> ${value}</p>`;
            }
        }

        html += '</div>';
        metadataContainer.innerHTML = html;
    }

    clearForm() {
        document.getElementById('prompt').value = 'Modern electric sedan with sleek aerodynamic body, LED headlights, and premium metallic finish';
        document.getElementById('product_type').value = 'car';
        document.getElementById('api_provider').value = 'fal';
        document.getElementById('camera_angle').value = 'three_quarter';
        document.getElementById('lighting').value = 'studio';
        document.getElementById('material').value = 'metal';
        document.getElementById('composition_focus').value = 'centered';
        document.getElementById('fov').value = 50;
        document.getElementById('reflectivity').value = 80;
        document.getElementById('texture_quality').value = 90;
        document.getElementById('color1').value = '#1a1a1a';
        document.getElementById('color2').value = '#ffffff';
        document.getElementById('color3').value = '#c0c0c0';
        document.getElementById('background').value = 'studio_white';
        document.getElementById('width').value = 1024;
        document.getElementById('height').value = 1024;
        document.getElementById('hdr_enabled').checked = true;
        document.getElementById('bit_depth').value = 16;
        this.updateSliderValues();
        this.updateJSONPreview();
    }

    showError(message) {
        alert(`Error: ${message}`);
    }

    showSuccess(message) {
        alert(`Success: ${message}`);
    }
}

const dashboard = new Dashboard();
