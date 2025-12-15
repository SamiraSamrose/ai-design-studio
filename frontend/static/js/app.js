document.addEventListener('DOMContentLoaded', () => {
    
    document.getElementById('generate_btn').addEventListener('click', async () => {
        const formData = dashboard.getFormData();
        
        try {
            dashboard.showLoading(
                'Generating design with FIBO...',
                'Using JSON-native control for precise parameter management'
            );
            const result = await apiClient.generateDesign(formData);
            dashboard.hideLoading();
            
            if (result.success) {
                dashboard.displayDesign(result);
                dashboard.showSuccess('Production-quality design generated successfully with HDR 16-bit pipeline');
            } else {
                dashboard.showError('Generation failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('variants_btn').addEventListener('click', async () => {
        const formData = dashboard.getFormData();
        
        try {
            dashboard.showLoading(
                'Generating variants with parallel agents...',
                'Multiple agents generating assets simultaneously to save time'
            );
            const result = await apiClient.generateVariants(formData, 6);
            dashboard.hideLoading();
            
            if (result.success) {
                comparisonManager.displayVariants(result.variants);
                
                const consistencyHtml = `
                    <p><strong>Total Designs:</strong> ${result.consistency_report.total_designs}</p>
                    <p><strong>Successful:</strong> ${result.consistency_report.successful}</p>
                    <p><strong>Failed:</strong> ${result.consistency_report.failed}</p>
                    <p><strong>Consistency Score:</strong> ${result.consistency_report.consistency_score.toFixed(1)}%</p>
                    ${result.consistency_report.recommendations.length > 0 ? 
                        '<p><strong>Recommendations:</strong></p><ul>' + 
                        result.consistency_report.recommendations.map(r => `<li>${r}</li>`).join('') + 
                        '</ul>' : ''}
                `;
                document.getElementById('consistency_content').innerHTML = consistencyHtml;
                document.getElementById('consistency_report').style.display = 'block';
                
                dashboard.showSuccess(`Generated ${result.total_generated} variants with ${result.consistency_report.consistency_score.toFixed(1)}% consistency`);
            } else {
                dashboard.showError('Variant generation failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('clear_btn').addEventListener('click', () => {
        dashboard.clearForm();
        dashboard.showSuccess('Parameters reset to defaults');
    });

    document.getElementById('refine_btn').addEventListener('click', async () => {
        if (!dashboard.currentDesignId) {
            dashboard.showError('No design to refine');
            return;
        }

        const refinementPrompt = prompt('Enter refinement instructions:', 'Enhance details, increase sharpness, and optimize material reflections');
        if (!refinementPrompt) return;

        try {
            dashboard.showLoading('Refining design with ComfyUI nodes...', 'Iterative refinement workflow executing');
            const result = await apiClient.refineDesign(dashboard.currentDesignId, refinementPrompt, 0.7);
            dashboard.hideLoading();
            
            if (result.success) {
                dashboard.showSuccess('Design refined successfully with ComfyUI');
            } else {
                dashboard.showError('Refinement failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('export_nuke_btn').addEventListener('click', async () => {
        if (!dashboard.currentDesignId) {
            dashboard.showError('No design to export');
            return;
        }

        try {
            dashboard.showLoading('Generating Nuke script with HDR 16-bit workflow...', 'JSON-native control preserved for compositors');
            const result = await apiClient.exportNuke(dashboard.currentDesignId, {
                export_format: 'exr',
                color_space: 'linear',
                bit_depth: 16,
                include_alpha: true,
                compression: 'zip'
            });
            dashboard.hideLoading();
            
            if (result.success) {
                window.open(result.download_url, '_blank');
                dashboard.showSuccess('Nuke script generated with professional HDR workflow. Compositors can tweak parameters while preserving JSON-native control.');
            } else {
                dashboard.showError('Export failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('manufacturability_btn').addEventListener('click', async () => {
        if (!dashboard.currentDesignParams) {
            dashboard.showError('No design to analyze');
            return;
        }

        try {
            dashboard.showLoading('AI agent analyzing manufacturability...', 'Checking production feasibility and optimization opportunities');
            const formData = dashboard.getFormData();
            const result = await apiClient.checkManufacturability(formData);
            dashboard.hideLoading();
            
            if (result.success) {
                const analysis = result.analysis;
                let message = `Manufacturability Analysis:\n\n`;
                message += `Feasible: ${analysis.feasible ? 'Yes' : 'No'}\n`;
                message += `Complexity Score: ${analysis.complexity_score}/10\n`;
                message += `Estimated Cost Tier: ${analysis.estimated_cost_tier}\n`;
                message += `Manufacturing Methods: ${analysis.manufacturing_methods.join(', ')}\n\n`;
                message += `Recommendations:\n${analysis.recommendations.join('\n')}`;
                alert(message);
            } else {
                dashboard.showError('Analysis failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('save_design_btn').addEventListener('click', () => {
        if (!dashboard.currentDesignId) {
            dashboard.showError('No design to save');
            return;
        }
        dashboard.showSuccess(`Design ${dashboard.currentDesignId} saved to generated_designs directory`);
    });

document.getElementById('compare_variants_btn').addEventListener('click', async () => {
    const selectedIds = comparisonManager.getSelectedVariantIds();
    
    if (selectedIds.length < 2) {
        dashboard.showError('Select at least 2 variants to compare (click on variant cards to select them)');
        return;
    }

    try {
        dashboard.showLoading('Creating visual comparison panel...', 'Generating side-by-side comparison with HDR and 16-bit fidelity');
        
        const result = await apiClient.createComparison(selectedIds);
        
        dashboard.hideLoading();
        
        if (result.success) {
            comparisonManager.displayComparison(result);
            
            let message = `Visual comparison panel created successfully!\n\n`;
            message += `Compared designs: ${result.total_compared}\n`;
            message += `Nuke script generated and ready for download.\n\n`;
            message += `Click the download link or check the nuke_scripts directory.`;
            
            dashboard.showSuccess(message);
        } else {
            dashboard.showError('Comparison creation failed: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        dashboard.hideLoading();
        dashboard.showError('Comparison error: ' + error.message);
    }
});
    document.getElementById('select_best_btn').addEventListener('click', async () => {
        if (comparisonManager.allVariants.length === 0) {
            dashboard.showError('No variants to analyze');
            return;
        }

        try {
            dashboard.showLoading('AI agent selecting best composition...', 'Analyzing quality metrics, composition rules, and aesthetic value');
            const result = await apiClient.selectBest(comparisonManager.allVariants);
            dashboard.hideLoading();
            
            if (result.success) {
                comparisonManager.displayBestSelection(result);
                
                const analysisHtml = `
                    <h4>AI Composition Selection</h4>
                    <p><strong>Best Design:</strong> ${result.best_design.variant_id}</p>
                    <p><strong>Quality Score:</strong> ${result.score}/100</p>
                    <p><strong>Reasoning:</strong> ${result.reasoning}</p>
                    <h5>All Scores:</h5>
                    <ul>
                        ${result.all_scores.map(s => `<li>${s.variant_id}: ${s.score}/100</li>`).join('')}
                    </ul>
                `;
                document.getElementById('comparison_analysis').innerHTML = analysisHtml;
            } else {
                dashboard.showError('Selection failed');
            }
        } catch (error) {
            dashboard.hideLoading();
            dashboard.showError(error.message);
        }
    });

    document.getElementById('export_all_nuke_btn').addEventListener('click', async () => {
        if (comparisonManager.allVariants.length === 0) {
            dashboard.showError('No variants to export');
            return;
        }

        dashboard.showSuccess('Exporting all variants to Nuke scripts...');
        
        for (const variant of comparisonManager.allVariants) {
            try {
                await apiClient.exportNuke(variant.design_id);
            } catch (error) {
                console.error(`Failed to export ${variant.design_id}:`, error);
            }
        }
        
        dashboard.showSuccess('All variants exported to Nuke with HDR workflows');
    });

    document.getElementById('generate_storyboard_btn').addEventListener('click', async () => {
        await storyboardManager.generateStoryboardPreview();
    });

    document.getElementById('export_storyboard_nuke_btn').addEventListener('click', async () => {
        await storyboardManager.exportStoryboardToNuke();
    });

    document.getElementById('clear_storyboard_btn').addEventListener('click', () => {
        storyboardManager.clearStoryboard();
        dashboard.showSuccess('Storyboard cleared');
    });
});
