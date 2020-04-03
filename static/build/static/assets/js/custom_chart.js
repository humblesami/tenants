(function(){
    window['chart_colors'] = [
        '#EF6262',
        '#7CD122',
        '#F9BB10',
        '#05B0D8',
        '#fdff09',
        '#e900fb',
        '#FAEBD7',
        '#A52A2A',
        '#FF7F50',
        '#6495ED',
        '#FFF8DC',
        '#DC143C',
        '#00FFFF',
        '#00008B',
        '#008B8B',
        '#B8860B',
        '#A9A9A9',
        '#BDB76B',
        '#8B008B',
        '#556B2F',
        '#FF8C00',
        '#9932CC',
        '#8B0000',
        '#483D8B',
    ];
    function drawChart(chartData, canvas_selector)
    {
        // console.log($(canvas_selector).length, canvas_selector);
        let labels = [];
        let data = [];
        let total_votings = 0;
        let chart_type = '';
        for(let i = 0; i < chartData.length; i++)
        {
            total_votings += chartData[i]['option_result']
        }
        for(let i = 0; i < chartData.length; i++)
        {
            if (total_votings > 0)
            {
                labels.push(chartData[i]['option_name'] + 
                    ' ('+chartData[i]['option_result']+' - '+
                    (chartData[i]['option_result']/total_votings*100).toFixed(2)+'%)');
            }
            else{
                labels.push(chartData[i]['option_name'] + 
                ' ('+chartData[i]['option_result']+' - 0%)');
            }
            data.push(chartData[i]['option_result']);
        }
        chartData = {
            datasets: [{
                data: data,
                backgroundColor: window['chart_colors'],
                hoverBackgroundColor: window['chart_colors']
            }],
        
            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: labels,
        };
        if (canvas_selector == '#progress-chart'){
            chart_type = 'doughnut'
            // chartData.datasets[0].backgroundColor = ['#EF6262', '#7CD122'];
            // chartData.datasets[0].hoverBackgroundColor = ['#EF6262', '#7CD122'];
            // chartData.datasets[0].borderColor = 'D3D3D3';
            // chartData.datasets[0].borderWidth = '.5px';
            // chartData.datasets[0].weight = 1;
        }else{
            chart_type = 'pie'
        }
        var ctx = $(canvas_selector)[0].getContext('2d');
        var myPieChart = new Chart(ctx, {
            type: chart_type,
            backgroundColor: 'rgb(255, 99, 132)',
            data: chartData,
            options: {
                aspectRatio: 1,
                legend: {
                    display: false
                },
                responsive: true,
            }
        });
    }
    window['drawChart'] = drawChart;
})()