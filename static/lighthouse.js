// (c) Crown Owned Copyright, 2016. Dstl.

$(document).ready(function() {
  try {
    $('#categories-filter input[type=checkbox]').on('change', function () {
      $form = $(this).closest('form');
      $form.submit();
    });
    $('#categories-filter input[type=submit]').parent().hide();
  } catch (e) {}

  // Turn off jQuery animation
  jQuery.fx.off = true;

  // Use GOV.UK selection-buttons.js to set selected
  // and focused states for block labels
  var $blockLabels = $(".block-label input[type='radio'], .block-label input[type='checkbox']");
  new GOVUK.SelectionButtons($blockLabels);
});
