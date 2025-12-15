class ComparisonManager {
    constructor() {
        this.selectedVariants = [];
        this.allVariants = [];
    }

    displayVariants(variants) {
        this.allVariants = variants;
        this.selectedVariants = [];
        const container = document.getElementById('variants_container');
        container.innerHTML = '';

        variants.forEach((variant, index) => {
            const card = document.createElement('div');
            card.className = 'variant-card';
            card.dataset.variantId = variant.design_id;
            card.dataset.index = index;

            card.innerHTML = `
                <img src="${variant.image_url}" alt="Variant ${variant.variant_id}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22280%22 height=%22220%22%3E%3Crect fill=%22%23ddd%22 width=%22280%22 height=%22220%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%23999%22%3EImage%3C/text%3E%3C/svg%3E'">
                <div class="variant-info">
                    <p><strong>ID:</strong> ${variant.variant_id || variant.design_id}</p>
                    <p><strong>Camera:</strong> ${variant.camera_angle || 'N/A'}</p>
                    <p><strong>Lighting:</strong> ${variant.lighting || 'N/A'}</p>
                    <p><strong>Agent:</strong> ${variant.agent_id || 'agent_' + index}</p>
                </div>
            `;

            card.addEventListener('click', () => this.toggleVariantSelection(card, variant));
            container.appendChild(card);
        });

        document.querySelector('.variants-panel').style.display = 'block';
    }

    toggleVariantSelection(card, variant) {
        const isSelected = card.classList.contains('selected');
        
        if (isSelected) {
            card.classList.remove('selected');
            this.selectedVariants = this.selectedVariants.filter(v => v.design_id !== variant.design_id);
        } else {
            card.classList.add('selected');
            this.selectedVariants.push(variant);
        }

        console.log(`Selected variants: ${this.selectedVariants.length}`, this.selectedVariants);
    }

    getSelectedVariantIds() {
        return this.selectedVariants.map(v => v.design_id);
    }

    getSelectedVariants() {
        return this.selectedVariants;
    }

    displayComparison(comparisonResult) {
        const container = document.getElementById('comparison_container');
        container.innerHTML = '';

        if (comparisonResult.image_urls && comparisonResult.image_urls.length > 0) {
            comparisonResult.image_urls.forEach((url, index) => {
                const img = document.createElement('img');
                img.src = url;
                img.alt = `Comparison ${index + 1}`;
                img.onerror = function() {
                    this.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23ddd%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%23999%22%3EImage Not Found%3C/text%3E%3C/svg%3E';
                };
                container.appendChild(img);
            });
        } else {
            this.selectedVariants.forEach(variant => {
                const img = document.createElement('img');
                img.src = variant.image_url;
                img.alt = `Variant ${variant.variant_id}`;
                img.onerror = function() {
                    this.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23ddd%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 fill=%22%23999%22%3EImage Not Found%3C/text%3E%3C/svg%3E';
                };
                container.appendChild(img);
            });
        }

        document.querySelector('.comparison-panel').style.display = 'block';
        
        window.scrollTo({
            top: document.querySelector('.comparison-panel').offsetTop - 20,
            behavior: 'smooth'
        });
    }

    displayBestSelection(result) {
        if (result.success) {
            const bestDesign = result.best_design;
            const message = `Best Design Selected:\n\nVariant: ${bestDesign.variant_id || bestDesign.design_id}\nScore: ${result.score}/100\n\nReasoning: ${result.reasoning}\n\nAll Scores:\n${result.all_scores.map(s => `${s.variant_id}: ${s.score}/100`).join('\n')}`;
            alert(message);
        } else {
            alert('Selection failed: ' + (result.message || 'Unknown error'));
        }
    }

    clearSelection() {
        this.selectedVariants = [];
        document.querySelectorAll('.variant-card').forEach(card => {
            card.classList.remove('selected');
        });
    }
}

const comparisonManager = new ComparisonManager();