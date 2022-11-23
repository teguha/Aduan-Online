import { ECharts } from 'echarts';
var grafik = echarts.init(
    document.getElementById('grafiks')
)


var option = {
    xAxis: {
      data: ['A', 'B', 'C', 'D', 'E']
    },
    yAxis: {},
    series: [
      {
        data: [10, 22, 28, 43, 49],
        type: 'bar',
        stack: 'x'
      },
      {
        data: [5, 4, 3, 5, 10],
        type: 'bar',
        stack: 'x'
      }
    ]
  };
grafik.setOption(option)

// import * as echarts from 'echarts';

// var chartDom = document.getElementById('grafiks');
// var myChart = echarts.init(chartDom);
// var option;

// option = {
//   xAxis: {
//     type: 'category',
//     data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
//   },
//   yAxis: {
//     type: 'value'
//   },
//   series: [
//     {
//       data: [120, 200, 150, 80, 70, 110, 130],
//       type: 'bar'
//     }
//   ]
// };

//alert("meoww")