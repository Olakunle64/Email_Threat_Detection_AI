document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('metricsChart');
    const metricsData = JSON.parse(document.getElementById('metricsData').textContent);
  
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
        datasets: [{
          label: 'Metric Value',
          data: metricsData,
          backgroundColor: [
            '#0d6efd',
            '#20c997',
            '#ffc107',
            '#6610f2'
          ],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 1.0
          }
        }
      }
    });
  });
  