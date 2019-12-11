
function drawChart(chartData, canvasId)
    {
        let labels = [];
        let data = [];
        for(let i = 0; i < chartData.length; i++)
        {
            labels.push(chartData[i]['option_name']);
            data.push(chartData[i]['option_result']);
        }

        chartData = {
            datasets: [{
                data: data,
                backgroundColor: [
                    'red',
                    'green',
                    'blue',
                    'yellow',
                    'pink',
                    'orange',
                ],
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: labels
        };
        var ctx = document.getElementById(canvasId).getContext('2d');
        var myPieChart = new Chart(ctx, {
            type: 'doughnut',
            backgroundColor: 'rgb(255, 99, 132)',
            data: chartData
        });
    }