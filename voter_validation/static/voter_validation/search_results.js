/**
 * Code for displaying Voter search results and allowing validation
 */

var VOTER_RESULTS_PER_PAGE = 10;

// Defer until JQuery, pagination, required data are present.
function deferSearchResults(method) {
  if (window.jQuery && window.addPagination
      && window.voterResults !== undefined) {
    method();
  } else {
    setTimeout(function() { deferSearchResults(method); }, 50);
  }
}
deferSearchResults(onLoadHandlerSearchResults);

function onLoadHandlerSearchResults() {
  if (voterResults && voterResults.length !== 0) {
    generateResultsTable(voterResults, "#voter-search-table");
    addPagination("#voter-search-table", VOTER_RESULTS_PER_PAGE,
        "pagination-voter");
  }
}

function submitValidationToApi(voterId, validate, elementToUpdate) {
    $.ajax({
        url: window.location.origin + "/api/private/validate_voter/",
        type: "POST",
        data: {
            voter_id: voterId,
            campaign_id: campaignId,  // global variable for page
            val: validate
        },

        success: function(jsonResponse) {
            // Update the text of the appropriate element.
            if (jsonResponse["result"] === "success") {
                if (validate) {
                    elementToUpdate.text("Validated!");
                } else {
                    elementToUpdate.text("Invalidated!");
                }
            } else {
                // Some kind of error occurred.
                elementToUpdate.text("Error; see logs");
                console.log(jsonResponse["error"]);
            }
        },

        error: function(xhr, error_msg, err) {
            console.log(error_msg);
        }
    });
}

/**
 * Add search result Voters to the given table.
 *
 * @param resultList: list of pre-ranked Voters (search results)
 * @param tableSelector: specifies the table, e.g. #voter-search-table
 */
function generateResultsTable(resultList, tableSelector) {
  // Header for table
  var html = "<thead><tr>";
  html += "<th class='validated-result'>Validated?</th>";
  html += "<th class='voter-text'>Voter</th>";
  html += "<th class='action'>Action</th>";

  html += "</tr></thead><tbody>";
  for (var i = 0; i < resultList.length; i++) {
    var result = resultList[i];
    // Voter ID is row ID
    html += "<tr id='" + result.id + "'>";

    // Validation column
    var isValidated = result.is_validated === "true";
    var validatedText = isValidated ? "Yes" : "No";
    html += "<td class='validated-result'>" + validatedText + "</td>";

    // Voter info column
    html += "<td class='voter-text'>";
    html += "<div class='voter-name'>" + result.name + "</div>";
    html += "<div class='voter-address'>" + result.address + "</div>";
    html += "<div class='voter-misc'>" +
        "Party: " + result.party + "<br>" +
        (result.gender === "" ? "" : "Gender: " + result.gender + "<br>") +
        "Latest registration date: " + result.curr_reg_date +
        "</div>";
    html += "</td>";

    // Validation/Invalidation link column
    if (isValidated) {
      html += "<td class='invalidation-action'><a href='javascript:void(null);'>" +
          "Invalidate</a>";
    } else {
      html += "<td class='validation-action'><a href='javascript:void(null);'>" +
          "Validate</a>";
    }
    html += "</td></tr>";
  }

  html += "</tbody>";
  $(tableSelector).html(html);

  // Invalidation link clicks
  $(".invalidation-action a").click(function (e) {
    var voterId = $($(this).closest("tr")).attr('id');
    var tdToUpdate = $($(this).closest("td"));
    // Confirm first
    tdToUpdate.html("<a href='javascript:void(null);' class='confirm'>Confirm?</a>");
    tdToUpdate.find('.confirm').click(function(e) {
        tdToUpdate.text("Invalidating...");
        submitValidationToApi(voterId, false, tdToUpdate);
    });
  });
  // Validation link clicks
  $(".validation-action a").click(function (e) {
    var voterId = $($(this).closest("tr")).attr('id');
    var tdToUpdate = $($(this).closest("td"));
    // Confirm first
    tdToUpdate.html("<a href='javascript:void(null);' class='confirm'>Confirm?</a>");
    tdToUpdate.find('.confirm').click(function(e) {
        tdToUpdate.text("Validating...");
        submitValidationToApi(voterId, true, tdToUpdate);
    });
  });
}
