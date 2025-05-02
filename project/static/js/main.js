document.addEventListener('DOMContentLoaded', function() {
    $('.data-table').DataTable({
        responsive: true,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/ru.json'
        },
        dom: '<"top"f>rt<"bottom"lip><"clear">',
        pageLength: 10,
        order: []
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const initCharts = () => {
        const chartElements = document.querySelectorAll('.chart-canvas');
        
        chartElements.forEach(chartEl => {
            const ctx = chartEl.getContext('2d');
            const chartType = chartEl.dataset.chartType || 'bar';
            const chartData = JSON.parse(chartEl.dataset.chartData);
            
            new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
    };
    
    if (typeof Chart !== 'undefined') {
        initCharts();
    }
});