/* One accessible Chart.js design language for every regression view.
   Registered before chart constructors, after Chart.js CDN itself. */
(function () {
  'use strict';
  const palette = Object.freeze({
    observation: '#218c88',
    observationFill: 'rgba(33,140,136,0.62)',
    prediction: '#dc8b4c',
    series: '#218c88',
    series2: '#bd7040',
    grid: '#e8eef3',
    text: '#53667b',
    tooltip: '#17283e',
    white: '#ffffff'
  });
  const api = {
    palette,
    scatter: {
      pointRadius: 3.5,
      pointHoverRadius: 6,
      pointBorderColor: '#ffffff',
      pointBorderWidth: 0.6,
      backgroundColor: palette.observationFill
    },
    fit: {borderColor: palette.prediction, backgroundColor: palette.prediction,
          borderWidth: 2.5, pointRadius: 0, fill: false, tension: 0},
    trend: {borderColor: palette.series, backgroundColor: palette.series,
            borderWidth: 2.25, pointRadius: 3, pointHoverRadius: 6,
            spanGaps: false, tension: 0.16},
    axis: label => ({title: {display: true, text: label, color: palette.text},
                     grid: {color: palette.grid}, ticks: {color: palette.text}})
  };
  window.ResearchChartTheme = Object.freeze(api);
  if (!window.Chart) return;
  const chart = window.Chart;
  chart.defaults.color = palette.text;
  chart.defaults.font.family = "'DM Sans','Noto Sans KR',sans-serif";
  chart.defaults.font.size = 11;
  chart.defaults.animation = false;
  chart.defaults.borderColor = palette.grid;
  chart.defaults.plugins.legend.labels.usePointStyle = true;
  chart.defaults.plugins.tooltip.backgroundColor = palette.tooltip;
  chart.defaults.plugins.tooltip.titleColor = palette.white;
  chart.defaults.plugins.tooltip.bodyColor = palette.white;
  chart.defaults.plugins.tooltip.displayColors = true;
  chart.defaults.plugins.tooltip.padding = 11;
  chart.defaults.plugins.tooltip.cornerRadius = 8;
  chart.defaults.elements.point.hoverRadius = 6;
  chart.defaults.elements.line.borderWidth = 2.25;
})();
