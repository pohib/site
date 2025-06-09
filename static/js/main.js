document.addEventListener('DOMContentLoaded', function() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.data-table').each(function() {
            if (!$.fn.DataTable.isDataTable(this)) {
                $(this).DataTable({
                    responsive: true,
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/ru.json'
                    },
                    dom: '<"top"f>rt<"bottom"lip><"clear">',
                    pageLength: 10,
                    order: [],
                    drawCallback: function() {
                        $('.paginate_button').addClass('btn btn-sm');
                        $('.dataTables_filter input').addClass('form-control form-control-sm');
                        $('.dataTables_length select').addClass('form-select form-select-sm');
                    }
                });
            }
        });
    } else {
        console.error('jQuery или DataTables не загружены');
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    const editors = document.querySelectorAll('.ck-content');
    editors.forEach(editor => {
        editor.style.color = '#000';
    });

    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    const initCharts = () => {
        if (typeof Chart === 'undefined') return;
        
        const chartElements = document.querySelectorAll('.chart-canvas');
        
        chartElements.forEach(chartEl => {
            if (!chartEl.dataset.chartData) return;
            
            try {
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
            } catch (e) {
                console.error('Ошибка инициализации графика:', e);
            }
        });
    };
    
    initCharts();
});