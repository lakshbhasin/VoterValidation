/**
 * Functions for adding pagination to any HTML table. Code adapted from
 * http://stackoverflow.com/a/28206715.
 */

/**
 * Adds pagination to the given selector
 * @param tableSelector: selector that wraps around a table, e.g. "#my-table"
 * @param rowsPerPage: number of rows per page.
 * @param paginationId: ID of pagination nav, e.g. pagination-team. Should
 * be a unique ID for a given page.
 */
function addPagination(tableSelector, rowsPerPage, paginationId) {
  // Add nav options
  var table = $(tableSelector);
  var tableRows = table.find("tbody tr");
  var rowsTotal = tableRows.length;
  var numPages = Math.ceil(rowsTotal/rowsPerPage);

  // Avoid adding pagination if <= 1 page
  if (numPages <= 1) {
    return;
  }

  table.after("<div id='" + paginationId + "' " +
      "class='pagination-nav'>Page: </div>");
  var paginationNav = $("#" + paginationId);

  for(var i = 0; i < numPages; i++) {
      var pageNum = i + 1;
      paginationNav.append("<a href='javascript:void(0)' rel='" + i + "'>"
          + pageNum + "</a> ");
  }

  // Show first page and mark first page as selected.
  tableRows.hide();
  tableRows.slice(0, rowsPerPage).show();
  paginationNav.find('a:first').addClass('active');

  // Handle pagination link clicks
  paginationNav.find('a').bind('click', function(){
    paginationNav.find('a').removeClass('active');
    $(this).addClass('active');

    var currPage = $(this).attr('rel');
    var startItem = currPage * rowsPerPage;
    var endItem = startItem + rowsPerPage;

    // Hide old page and show new.
    tableRows.css('opacity', '0.0').hide().slice(startItem, endItem).show()
        .animate({opacity: 1.0}, 300);
  });
}