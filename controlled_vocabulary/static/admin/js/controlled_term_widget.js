// Adapted from django/contrib/admin/static/admin/js/autocomplete.js
;(function ($) {
  'use strict'

  function format_term(term) {
    var ret = term.text
    if (term.description) {
      ret += ' (' + term.description + ')'
    }
    return ret
  }

  var init = function ($element, options) {
    var settings = $.extend(
      {
        ajax: {
          data: function (params) {
            return {
              term: params.term,
              page: params.page,
              prefix: $element.data('voc-prefix')
            }
          },
          // Used to avoid excessive amount of requests
          delay: 300
        },
        templateResult: format_term
      },
      options
    )
    $element.select2(settings)
  }

  $.fn.controlledTermSelect2 = function (options) {
    var settings = $.extend({}, options)
    $.each(this, function (i, element) {
      var $element = $(element)
      init($element, settings)
    })
    return this
  }

  $(function () {
    // Initialize all autocomplete widgets except the one in the template
    // form used when a new formset is added.
    var $selects = $('select[data-voc-prefix]').not('[name*=__prefix__]')
    $selects.controlledTermSelect2()
    // if we leave this class on, django will call select2
    // a second time on this select element.
    $selects.removeClass('admin-autocomplete')

    $('select.controlled-vocabulary').on('change', function (e) {
      $(this).siblings('select[data-voc-prefix]').data('voc-prefix', this.value)
    })
  })

  $(document).on('formset:added', function (event, $row, formsetName) {
    const $select = $row.find('select[data-voc-prefix]')
    $select.controlledTermSelect2()
    $select.removeClass('admin-autocomplete')
  })
})(django.jQuery)
