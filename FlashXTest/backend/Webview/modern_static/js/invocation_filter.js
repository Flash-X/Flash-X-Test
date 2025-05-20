/**
 * invocation_filter.js
 * Client-side filtering for per-site build tables.
 */
(function() {
  function initInvocationFilter() {
    // For each site section, bind filters to its table
    var sections = document.querySelectorAll('.site-section');
    sections.forEach(function(section) {
      var statusFilter = section.querySelector('.status-filter');
      var typeFilter = section.querySelector('.type-filter');
      var table = section.querySelector('table.inv-table');
      if (!statusFilter || !typeFilter || !table) return;
      function applyFilter() {
        var status = statusFilter.value;
        var type = typeFilter.value;
        var rows = table.querySelectorAll('tr[data-status]');
        rows.forEach(function(row) {
          var rowStatus = row.getAttribute('data-status');
          var rowTypes = row.getAttribute('data-errortypes') || '';
          var types = rowTypes.split(' ').filter(function(t) { return t; });
          var statusMatch = (status === 'all' || rowStatus === status);
          var typeMatch = (type === 'all' || types.indexOf(type) !== -1);
          row.style.display = (statusMatch && typeMatch) ? '' : 'none';
        });
      }
      // Bind change events
      statusFilter.addEventListener('change', applyFilter);
      typeFilter.addEventListener('change', applyFilter);
      // Initial filtering
      applyFilter();
    });
  }
  // Expose init function
  window.initInvocationFilter = initInvocationFilter;
})();
