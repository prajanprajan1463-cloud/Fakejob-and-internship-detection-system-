/**
 * Main application client-side script for Fake Job & Internship Detection System
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Password Visibility Toggle
    const togglePasswordBtns = document.querySelectorAll('.toggle-password-btn');
    togglePasswordBtns.forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                const icon = this.querySelector('i');
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                }
            }
        });
    });

    // 2. Prevent Double Submissions & Display Loading Spinner for Analyze Form
    const analyzeForm = document.getElementById('analyze-job-form');
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (analyzeForm && loadingOverlay) {
        analyzeForm.addEventListener('submit', function (e) {
            const submitBtn = document.getElementById('submitAnalyzeBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing Posting...';
            }
            loadingOverlay.classList.add('active');
        });
    }

    // 3. Render Dashboard Chart if canvas and data exist
    const chartCanvas = document.getElementById('riskDistributionChart');
    if (chartCanvas && typeof Chart !== 'undefined') {
        const highCount = parseInt(chartCanvas.getAttribute('data-high') || '0', 10);
        const mediumCount = parseInt(chartCanvas.getAttribute('data-medium') || '0', 10);
        const lowCount = parseInt(chartCanvas.getAttribute('data-low') || '0', 10);
        const total = highCount + mediumCount + lowCount;

        if (total > 0) {
            new Chart(chartCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['High Risk', 'Needs Verification', 'Lower Risk'],
                    datasets: [{
                        data: [highCount, mediumCount, lowCount],
                        backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 14,
                                font: { size: 12, family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto' }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const val = context.parsed;
                                    const pct = ((val / total) * 100).toFixed(1);
                                    return ` ${context.label}: ${val} (${pct}%)`;
                                }
                            }
                        }
                    },
                    cutout: '68%'
                }
            });
        }
    }

    // 4. Print Report Handler
    const printBtn = document.getElementById('printReportBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function () {
            window.print();
        });
    }
});

