function getRangeCounts(data, ranges, rangesform) {
    var rangeCounts = ranges.map(function () {
        return 0;
    });

    data.forEach(function (value) {
        var rangeIndex = ranges.findIndex(function (range) {
            if (rangesform === 'list') {
                return value >= range[0] && value < range[1];
            } else if (rangesform === 'category') {
                return value === range;
            }

        });
        if (rangeIndex !== -1) {
            rangeCounts[rangeIndex]++;
        }
    });
    return rangeCounts;
}

function buildDistributionChart(list_data, ranges) {
    var rangeCounts = getRangeCounts(list_data, ranges, 'list')
    console.log('counts是', rangeCounts)
    console.log(rangeCounts)
    // 转换数据为 echarts 所需格式
    var data = [];
    for (var i = 0; i < ranges.length; i++) {
        data.push({name: ranges[i], value: rangeCounts[i], count: rangeCounts[i]});
    }
    console.log(data)

    // 配置图表

    var options = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: ranges,
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: 'Direct',
                type: 'bar',
                barWidth: '60%',
                data: data,
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}', // 显示数量
                },
                itemStyle: {
                    color: 'skyblue'
                }
            }
        ]
    };

    return options
}

function buildcolordistributionChart(list_data, ranges) {
    var rangeCounts = getRangeCounts(list_data, ranges, 'list')
    console.log('counts是', rangeCounts)
    console.log(rangeCounts)
    // 转换数据为 echarts 所需格式
    var data = [];
    for (var i = 0; i < ranges.length; i++) {
        data.push({name: ranges[i], value: rangeCounts[i], count: rangeCounts[i]});
    }
    console.log(data)

    var endColor = '#982637';
    var startColor = '#2F6296';

    // 计算每个柱子的颜色
    var colors = rangeCounts.map(function (value) {
        var ratio = (value - Math.min(...rangeCounts)) / (Math.max(...rangeCounts) - Math.min(...rangeCounts));
        var color = ratioToColor(ratio, startColor, endColor);
        console.log(ratio, color)
        return color;
    });

    console.log(colors)

    // 配置图表

    var options = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: ranges,
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: 'Direct',
                type: 'bar',
                barWidth: '60%',
                data: data,
                label: {
                    show: true,
                    position: 'top',
                    formatter: '{c}', // 显示数量
                },
                itemStyle: {
                    color: function (params) {
                        return colors[params.dataIndex];
                    }
                }
            }
        ]
    };

    return options
}

function buildPieCharts(list_data, categories) {
    var rangeCounts = getRangeCounts(list_data, categories, 'category');
    console.log(rangeCounts)
    var data = categories.map(function (category, index) {
        return {value: rangeCounts[index], name: category};
    })
    var options = {
        series: [{
            type: 'pie',
            radius: '50%',
            data: data
        }]
    };
    return options
}

function buildCharts(chartstype, list_data, ranges) {
    if (chartstype === 'distributionchart') {
        return buildDistributionChart(list_data, ranges)
    } else if (chartstype === 'piechart') {
        return buildPieCharts(list_data, ranges)
    }
}

function getMinandMax(numbers) {
    var max = numbers[0];
    var min = numbers[0];
    for (var i = 1; i < numbers.length; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }

        if (numbers[i] < min) {
            min = numbers[i];
        }
    }

    return [min, max]
}

// 将比例转换为颜色
function ratioToColor(ratio, startColor, endColor) {
    var startRGB = colorToRGB(startColor);
    var endRGB = colorToRGB(endColor);
    var resultRGB = [];
    for (var i = 0; i < 3; i++) {
        resultRGB[i] = startRGB[i] * (1 - ratio) + endRGB[i] * ratio;
    }
    return RGBToColor(resultRGB);
}

// 将颜色转换为 RGB 值
function colorToRGB(color) {
    var reg = /^#([0-9a-fA-f]{3}|[0-9a-fA-f]{6})$/;
    color = color.toLowerCase();
    if (reg.test(color)) {
        if (color.length === 4) {
            var temp = '#';
            for (var i = 1; i < 4; i++) {
                temp += color.slice(i, i + 1).concat(color.slice(i, i + 1));
            }
            color = temp;
        }
        //处理六位的颜色值
        var colorNew = [];
        for (var i = 1; i < 7; i += 2) {
            colorNew.push(parseInt("0x" + color.slice(i, i + 2)));
        }
        return colorNew;
    } else {
        return color;
    }
}

// 将 RGB 值转换为颜色
function RGBToColor(rgb) {
    var color = '#';
    for (var i = 0; i < 3; i++) {
        color += ('00' + Math.round(rgb[i]).toString(16)).slice(-2);
    }
    return color;
}