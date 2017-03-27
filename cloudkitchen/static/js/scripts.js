$(function() {

  /**  Resalta el nombre de los enlaces del navbar de acuerdo a la ubicacion en donde se encuentre */
  let path = $(location).attr('pathname');
  if (path == '/sales/') {
    $('#link-sales').addClass('active');
  }
  else if (path == '/sales/new/breakfast/') {
    $('#link-new-breakfast').addClass('active');
  }
  else if (path == '/sales/new/food/') {
    $('#link-new-food').addClass('active');
  }
  else if (path == '/supplies/' || path == '/supplies/new/') {
    $('#link-warehouse').addClass('active');
  }
  else if (path == '/cartridges/' || path == '/cartridges/new/') {
    $('#link-warehouse').addClass('active');
  }
  else if (path == '/customers/register/list/') {
    $('#link-customers').addClass('active');
  }
  else if (path == '/kitchen/' || path == '/kitchen/assembly/' ) {
    $('#link-kitchen').addClass('active');
  }
  else if (path == '/diners/' || path == '/diners/logs/') {
    $('#link-diners').addClass('active');
  }
});
