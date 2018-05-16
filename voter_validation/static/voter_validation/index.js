/**
 * JavaScript functions for formatting Campaign goals on front page.
 */

// Global values for Campaign ProgressBar.Lines. The keys are the Campaigns'
// primary keys, and the values are the ProgressBar.Lines
var CAMP_PROGRESS_BARS = {};

// Start and end colors for progress bar goals site-wide
var START_COLOR = "#3498DB";
var END_COLOR = "#2BE8CE";

// If goal is not met, use START_COLOR site-wide
var PROG_BAR_PARAMS_GOAL_UNMET = {
  color: START_COLOR,
  trailColor: "#EEE",
  trailWidth: 8,  // note: these are in some weird non-pixel units (rows?)
  strokeWidth: 8
};

// If goal is met, fix color at endColor
var PROG_BAR_PARAMS_GOAL_MET = {
  color: END_COLOR,
  trailColor: "#EEE",
  trailWidth: 8,  // note: these are in some weird non-pixel units (rows?)
  strokeWidth: 8
};


// Defer until JQuery, ProgressBar, Campaigns have loaded
function deferIndex(method) {
    if (window.jQuery && window.ProgressBar && window.campaigns) {
        method();
    } else {
        setTimeout(function () {
            deferIndex(method)
        }, 50);
    }
}
deferIndex(setupCampaignHtml);

// Sets up Campaign progress bars.
function setupCampaignHtml() {
    $("#campaign-progress").html(generateCampaignContainerHtml());

    // Populate ProgressBars and update counts
    for (var i = 0; i < campaigns.length; i++) {
        var campaign = campaigns[i];
        var campaignPk = campaign.id;

        var progBarParams = undefined;
        if (campaign.validation_count >= campaign.validation_goal) {
            progBarParams = PROG_BAR_PARAMS_GOAL_MET;
        } else {
            progBarParams = PROG_BAR_PARAMS_GOAL_UNMET;
        }

        // Create ProgressBar by finding the div with id (e.g.)
        // #camp-1-line-container, where 1 is the PK of the Campaign.
        CAMP_PROGRESS_BARS[campaignPk] = new ProgressBar.Line(
            "#camp-" + campaignPk + "-line-container", progBarParams);

        // Set up overall validation counts for this Campaign
        updateProgressBarAndText(campaignPk, campaign.validation_count,
            campaign.validation_goal);
    }
}

// Generates HTML for Campaign containers, which are populated later.
function generateCampaignContainerHtml() {
    var htmlToReturn = "";
    for (var i = 0; i < campaigns.length; i++) {
        var campaign = campaigns[i];
        var campaignPk = campaign.id;
        htmlToReturn += "<div class='campaign-card' " +
            "id='camp-" + campaignPk + "-panel'>";

        // Campaign general information
        htmlToReturn += "<div class='campaign-info flex column'>";
        htmlToReturn += "<p class='campaign-name'>" + campaign.name + "</p>";
        htmlToReturn += "</div>";

        // Campaign progress bars
        htmlToReturn += "<div class='val-count' style='width: 100%;'>";
        htmlToReturn += "Validations: " +
            "<span id='camp-" + campaignPk + "-val-count'></span>/" +
            "<span id='camp-" + campaignPk + "-val-goal'></span>" +
            "</div>";
        // Total progress bar
        htmlToReturn += "<div id='camp-" + campaignPk + "-line-container' " +
            "class='camp-progress-bar'></div>";

        htmlToReturn += "<div class='flex space-around val-button'>" +
            "<a class='generic-submit-button' " +
            "href='/validate/" + campaignPk + "/' " +
            "title='Click here to validate for " + campaign.name + "!'>" +
            "Validate" + "</a>";

        htmlToReturn += "</div></div>";
    }

    return htmlToReturn;
}

function updateProgressBarAndText(campaignPk, validations, validationGoal) {
    // The text element containing the overall validations for this Campaign
    var textElem = $("#camp-" + campaignPk + "-val-count");
    textElem.text(Number(validations).toLocaleString("en"));

    // Set overall validation goal too for Campaign.
    var goalElem = $("#camp-" + campaignPk + "-val-goal");
    goalElem.text(Number(validationGoal).toLocaleString("en"));

    // Update and animate bar.
    var barElem = CAMP_PROGRESS_BARS[campaignPk];
    barElem.animate(Math.min(validations/validationGoal, 1.0));
}
