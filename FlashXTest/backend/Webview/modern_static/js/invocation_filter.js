/**
 * invocation_filter.js
 * Client-side filtering for per-site build tables using the Status and Error
 * Type dropdown selects.  Each .site-section card is handled independently.
 */
(function () {
  'use strict';

  function initInvocationFilter() {
    var sections = document.querySelectorAll('.site-section');

    sections.forEach(function (section) {
      var statusFilter = section.querySelector('.status-filter');
      var typeFilter   = section.querySelector('.type-filter');
      var table        = section.querySelector('table.inv-table');
      var noResultsMsg = section.querySelector('.no-results-msg');

      if (!statusFilter || !typeFilter || !table) return;

      function applyFilter() {
        var status = statusFilter.value;
        var type   = typeFilter.value;
        var rows   = table.querySelectorAll('tr[data-status]');
        var visibleCount = 0;
        var altToggle = 0;

        rows.forEach(function (row) {
          var rowStatus = row.getAttribute('data-status') || '';
          var rowTypes  = (row.getAttribute('data-errortypes') || '').split(' ')
                            .filter(function (t) { return t; });

          var statusOk = (status === 'all' || rowStatus === status);
          var typeOk   = (type   === 'all' || rowTypes.indexOf(type) !== -1);
          var show     = statusOk && typeOk;

          row.style.display = show ? '' : 'none';

          if (show) {
            // Re-apply zebra stripes to visible rows only
            row.classList.remove('row', 'row-alt');
            row.classList.add(altToggle % 2 === 0 ? 'row' : 'row-alt');
            altToggle++;
            visibleCount++;
          }
        });

        // Show "no results" message when every row is filtered out
        if (noResultsMsg) {
          noResultsMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
        }
      }

      statusFilter.addEventListener('change', applyFilter);
      typeFilter.addEventListener('change', applyFilter);

      // Apply on load so the initial selection is respected
      applyFilter();
    });
  }

  window.initInvocationFilter = initInvocationFilter;
}());
