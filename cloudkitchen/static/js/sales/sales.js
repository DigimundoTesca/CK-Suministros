$(function() {
  

  function get_sales_day(day) {
    $.ajax({
      url: '/sales/sales-day/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: '{{ csrf_token }}',
        'day': day,
      },
      traditional: true,
      datatype: 'jsonp',
      success: function(result) {
        console.log(result);
      },
      error: function(result, jqXHR, textStatus, errorThrown) {
        console.log(result);
      },
    });
  }
  var earnings_for_the_week = new Chart(ctx_week, {
    type: 'bar',
    data: {
      labels: ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sábado", "Domingo"],
      datasets: [{
        label: 'Ventas del día',
        data: earnings,
        backgroundColor: [
          'rgba(241,196,15,0.7)',
          'rgba(230,126,34,0.7)',
          'rgba(231,76,60,0.7)',
          'rgba(26,188,156,0.7)',
          'rgba(46,204,113,0.7)',
          'rgba(52,152,219,0.7)',
          'rgba(52,73,94,0.7)',
        ],
        borderColor: [
          'rgba(241,196,15,0.9)',
          'rgba(230,126,34,0.9)',
          'rgba(231,76,60,0.9)',
          'rgba(26,188,156,0.9)',
          'rgba(46,204,113,0.9)',
          'rgba(52,152,219,0.9)',
          'rgba(52,73,94,0.9)',
        ],
      }]
    },
    options: {
      responsive: true,
      onClick: function(event, legendItem) {
        try {
          get_sales_day(legendItem[0]._index);
        } catch (error) {
          console.log(error.message);
        }
      },
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  });
  var earnings_for_the_day = new Chart(ctx_day, {
    type: 'horizontalBar',
    data: {
      labels: [
        "12:00 - 13:00", "12:00 - 12:30", "11:30 - 12:00", "11:00 - 11:30", "10:30 - 11:00", "10:00 - 10:30", "09:30 - 10:00", "09:00 - 09:30",
        "08:30 - 09:00", "08:00 - 08:30", "07:30 - 08:00", "07:00 - 07:30", "06:30 - 07:00", "06:00 - 06:30", "05:30 - 06:00", "05:00 - 05:30",
      ],
      datasets: [{
        label: 'Ventas en este horario',
        data: [90, 0, 0, 0, 0, 0, 0, 0, 300, 0, 40, 0, 0, 0, 0, 100],
        backgroundColor: [
          'rgba(242,38,19,0.7)',
          'rgba(246,36,89,0.7)',
          'rgba(103,65,114,0.7)',
          'rgba(65,131,215,0.7)',
          'rgba(54,215,183,0.7)',
          'rgba(46,204,113,0.7)',
          'rgba(247,202,24,0.7)',
          'rgba(249,105,14,0.7)',
          'rgba(242,38,19,0.7)',
          'rgba(246,36,89,0.7)',
          'rgba(103,65,114,0.7)',
          'rgba(65,131,215,0.7)',
          'rgba(54,215,183,0.7)',
          'rgba(46,204,113,0.7)',
          'rgba(247,202,24,0.7)',
          'rgba(249,105,14,0.7)',
        ],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      onClick: function(event, legendItem) {
        console.log(legendItem[0]._index);
      },
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  });
  /** Funciona para darle formato de moneda a un numero */
  function set_number_format(amount, decimals) {
    amount += '';
    amount = parseFloat(amount.replace(/[^0-9\.]/g, ''));
    decimals = decimals || 0;
    if (isNaN(amount) || amount === 0)
      return parseFloat(0).toFixed(decimals);
    amount = '' + amount.toFixed(decimals);
    var amount_parts = amount.split('.'),
      regexp = /(\d+)(\d{3})/;
    while (regexp.test(amount_parts[0]))
      amount_parts[0] = amount_parts[0].replace(regexp, '$1' + ' ' + '$2');
    return amount_parts.join('.');
  }
  /** Calcula el total de ganancias de la semana y lo imprime */
  function set_total_earnings() {
    var total_earnings = 0;
    for (var i = 0; i < earnings.length; i++) {
      total_earnings += earnings[i];
    }
    total_earnings = set_number_format(total_earnings, 2);
    $('#total-earnings-text').append(total_earnings);
  }
  set_total_earnings();
});