/**
 * Code for displaying generic search results with datatables.
 */

var USER_RESULTS_PER_PAGE = 3;
var TEAM_RESULTS_PER_PAGE = 3;

// Defer until JQuery, pagination, required data are present.
function deferSearchResults(method) {
  if (window.jQuery && window.addPagination
      && window.userResults !== undefined && window.teamResults !== undefined) {
    method();
  } else {
    setTimeout(function() { deferSearchResults(method); }, 50);
  }
}
deferSearchResults(onLoadHandlerSearchResults);

function onLoadHandlerSearchResults() {
  if (userResults && userResults.length != 0) {
    generateResultsTable(userResults, "#user-search-table");
    addPagination("#user-search-table", USER_RESULTS_PER_PAGE,
        "pagination-user");
  }
  if (teamResults && teamResults.length != 0) {
    generateResultsTable(teamResults, "#team-search-table");
    addPagination("#team-search-table", TEAM_RESULTS_PER_PAGE),
        "pagination-team";
  }
}

/**
 * Add search result table rows to the given table.
 *
 * @param resultList: list of pre-ranked objects (search results)
 * @param tableSelector: specifies the table, e.g. #team-search-table
 */
function generateResultsTable(resultList, tableSelector) {
  var html = "<tbody>";
  for (var i = 0; i < resultList.length; i++) {
    var result = resultList[i];
    html += "<tr class='flex'>";
    html += "<td class='search-avatar'>" +
        "<img src='" + result.avatar_url + "'></td>";
    html += "<td class='search-result-text'>";

    if (result['type'] === 'Team') {
      html += "<div class='search-name'><a href='/t/" + result.id + "/'>"
          + result.name + "</a></div>";
      var memberStr = result.member_count > 1 ? " members" : " member";
      html += "<div class='result-stats'>" + result.total_calls_made +
          " calls · " + result.member_count + memberStr + "</div>";
    } else {
      html += "<div class='search-name'><a href='/u/" + result.name + "/'>"
          + result.name + "</a></div>";
      html += "<div class='result-stats'>" + result.calls_made +
          " calls · " + result.rank + "</div>";
    }
    html += "<div class='search-description'>" + result.description + "</div>";
    html += "</td>";
    html += "</tr>"
  }

  html += "</tbody>";
  $(tableSelector).html(html);
}
