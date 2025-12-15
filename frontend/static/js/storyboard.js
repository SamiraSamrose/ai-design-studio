class StoryboardManager {
    constructor() {
        this.frames = [];
        this.draggedFrame = null;
        this.initializeDropZone();
    }

    initializeDropZone() {
        const dropZone = document.getElementById('storyboard_drop');
        if (!dropZone) return;

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('click', () => {
            if (comparisonManager.allVariants.length > 0) {
                this.showFrameSelector();
            } else {
                alert('Please generate design variants first');
            }
        });
    }

    showFrameSelector() {
        const variants = comparisonManager.allVariants;
        let html = '<div class="frame-selector"><h4>Select designs for storyboard:</h4>';
        
        variants.forEach(variant => {
            html += `
                <div class="frame-option" data-variant-id="${variant.design_id}">
                    <img src="${variant.image_url}" alt="${variant.variant_id}">
                    <p>${variant.variant_id}</p>
                    <button class="btn btn-secondary" onclick="storyboardManager.addFrame('${variant.design_id}', '${variant.image_url}', '${variant.variant_id}')">Add to Storyboard</button>
                </div>
            `;
        });
        
        html += '</div>';
        
        document.getElementById('modal_title').textContent = 'Add to Storyboard';
        document.getElementById('modal_body').innerHTML = html;
        document.getElementById('modal_confirm').style.display = 'none';
        document.getElementById('modal_cancel').textContent = 'Close';
        document.getElementById('modal_overlay').style.display = 'flex';
    }

    addFrame(designId, imageUrl, variantId) {
        this.frames.push({
            id: designId,
            url: imageUrl,
            variant: variantId
        });
        
        this.renderFrames();
        document.getElementById('modal_overlay').style.display = 'none';
        document.querySelector('.storyboard-panel').style.display = 'block';
    }

    renderFrames() {
        const container = document.getElementById('storyboard_frames');
        container.innerHTML = '';

        this.frames.forEach((frame, index) => {
            const frameElement = document.createElement('div');
            frameElement.className = 'storyboard-frame';
            frameElement.draggable = true;
            frameElement.dataset.index = index;

            frameElement.innerHTML = `
                <img src="${frame.url}" alt="${frame.variant}">
                <div class="frame-number">${index + 1}</div>
                <button class="remove-frame" onclick="storyboardManager.removeFrame(${index})">×</button>
            `;

            frameElement.addEventListener('dragstart', (e) => {
                this.draggedFrame = index;
                e.dataTransfer.effectAllowed = 'move';
            });

            frameElement.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });

            frameElement.addEventListener('drop', (e) => {
                e.preventDefault();
                const targetIndex = parseInt(e.currentTarget.dataset.index);
                this.reorderFrames(this.draggedFrame, targetIndex);
            });

            container.appendChild(frameElement);
        });
    }

    reorderFrames(fromIndex, toIndex) {
        const [movedFrame] = this.frames.splice(fromIndex, 1);
        this.frames.splice(toIndex, 0, movedFrame);
        this.renderFrames();
    }

    removeFrame(index) {
        this.frames.splice(index, 1);
        this.renderFrames();
        
        if (this.frames.length === 0) {
            document.querySelector('.storyboard-panel').style.display = 'none';
        }
    }

    async generateStoryboardPreview() {
        if (this.frames.length === 0) {
            alert('No frames in storyboard');
            return;
        }

        dashboard.showLoading('AI agent translating storyboard to preview with HDR and 16-bit fidelity...');

        try {
            const designIds = this.frames.map(f => f.id);
            const result = await apiClient.createComparison(designIds);
            dashboard.hideLoading();

            if (result.success) {
                alert('Storyboard preview generated with HDR and 16-bit fidelity');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    }

    async exportStoryboardToNuke() {
        if (this.frames.length === 0) {
            alert('No frames in storyboard');
            return;
        }

        dashboard.showLoading('Exporting storyboard to Nuke with HDR workflow...');

        try {
            const designIds = this.frames.map(f => f.id);
            const result = await apiClient.createComparison(designIds);
            dashboard.hideLoading();

            if (result.success && result.nuke_script) {
                window.open(`/api/download-nuke/${result.nuke_script.split('/').pop()}`, '_blank');
                alert('Storyboard exported to Nuke successfully');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    }

    clearStoryboard() {
        this.frames = [];
        this.renderFrames();
        document.querySelector('.storyboard-panel').style.display = 'none';
    }
}

const storyboardManager = new StoryboardManager();
