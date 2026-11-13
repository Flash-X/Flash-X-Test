/**
 * table_sort.js
 * Click-to-sort for th[data-sortable] headers and text search on the index page.
 */
(function () {
  'use strict';

  /* Return the sort key for a cell: data-sort-value attr, then trimmed text. */
  function cellKey(cell) {
    var v = cell.getAttribute('data-sort-value');
    return (v !== null ? v : (cell.textContent || '')).trim().toLowerCase();
  }

  /* Re-apply zebra stripes after sorting; skip hidden rows. */
  function restripe(rows) {
    var vis = 0;
    rows.forEach(function (row) {
      row.classList.remove('row', 'row-alt');
      if (row.style.display !== 'none') {
        row.classList.add(vis % 2 === 0 ? 'row' : 'row-alt');
        vis++;
      }
    });
  }

  function sortTable(th) {
    var table = th.closest('table');
    if (!table) return;

    var headers = Array.from(th.parentElement.children);
    var colIdx  = headers.indexOf(th);
    var prevDir = th.getAttribute('aria-sort');
    var dir     = prevDir === 'ascending' ? 'descending' : 'ascending';

    headers.forEach(function (h) { h.removeAttribute('aria-sort'); });
    th.setAttribute('aria-sort', dir);

    var rows = Array.from(table.querySelectorAll('tr')).filter(function (r) {
      return r.classList.contains('row') || r.classList.contains('row-alt');
    });

    rows.sort(function (a, b) {
      var ak = cellKey(a.children[colIdx] || {});
      var bk = cellKey(b.children[colIdx] || {});
      var cmp = ak < bk ? -1 : ak > bk ? 1 : 0;
      return dir === 'ascending' ? cmp : -cmp;
    });

    var parent = table.querySelector('tbody') || table;
    rows.forEach(function (row) { parent.appendChild(row); });
    restripe(rows);
  }

  /* Wire up all sortable headers in the document. */
  function initTableSort() {
    document.querySelectorAll('th[data-sortable]').forEach(function (th) {
      th.addEventListener('click', function () { sortTable(th); });
    });
  }

  /* Live text search on the index page invocation list. */
  function initInvocationSearch() {
    var input = document.getElementById('invocationSearch');
    if (!input) return;
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var rows = document.querySelectorAll(
        '.index-table tr.row, .index-table tr.row-alt'
      );
      var vis = 0;
      rows.forEach(function (row) {
        var text = (row.textContent || '').toLowerCase();
        var show = !q || text.indexOf(q) !== -1;
        row.style.display = show ? '' : 'none';
        if (show) {
          row.classList.remove('row', 'row-alt');
          row.classList.add(vis % 2 === 0 ? 'row' : 'row-alt');
          vis++;
        }
      });
    });
  }

  window.initTableSort        = initTableSort;
  window.initInvocationSearch = initInvocationSearch;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initTableSort();
      initInvocationSearch();
    });
  } else {
    initTableSort();
    initInvocationSearch();
  }
}());
