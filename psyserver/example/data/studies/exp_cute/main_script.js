"use strict";

// settings
const DEFAULT_RATING = 8;
const LABEL_DURATION = 1000; // milliseconds
const PROLIFIC_URL = "https://UPDATE_THIS";
// const cat = 1

// object to contain experiment data
const DATA = {
  trials: [
    {
      animal: "sheep",
      imageID: "sheep_1",
    },
    {
      animal: "sheep",
      imageID: "sheep_2",
    },
    {
      animal: "sheep",
      imageID: "sheep_3",
    },
    {
      animal: "goat",
      imageID: "goat_1",
    },
    {
      animal: "goat",
      imageID: "goat_2",
    },
    {
      animal: "goat",
      imageID: "goat_3",
    },
  ],
  trialIndex: -1,
  startTime: Date.now(), // milliseconds since UNIX epoch
};

// set up the starting page
function setUp() {
  // get study information from the Prolific query string
  let urlParams = new URLSearchParams(window.location.search);
  DATA.prolificPID = urlParams.get("PROLIFIC_PID");
  if (DATA.prolificPID === null) {
    DATA.prolificPID = "DEBUG_PROLIFIC_ID";
  }
  DATA.studyID = urlParams.get("STUDY_ID");
  DATA.sessionID = urlParams.get("SESSION_ID");
  // shuffle trials
  shuffleArray(DATA.trials);
  // bind keyup to space to submit the trial, if the slider is visible
  $(document).keyup((event) => {
    if (event.key === " " && $("#slider").is(":visible")) {
      submitTrial();
    }
  });
  // bind click to start button to begin the trials
  $("#start_button").click(() => {
    $("#instructions").text(
      "Instructions:\r\n " +
        "Press space to submit your rating and show the next animal."
    );
    $("#start_button").hide();
    beginTrial();
  });
  // hide the slider and slider label
  $("#slider").hide();
  $("#slider_label").hide();
  // show instructions
  $("#instructions").text(
    "Instructions:\r\n " +
      "In this task, you will be rating the cuteness of livestock on a " +
      "scale from 1 to 10. Click the start button to begin."
  );
}

// show the next trial
function beginTrial() {
  // if there are trials remaining
  if (DATA.trialIndex < DATA.trials.length - 1) {
    // increment trial index
    DATA.trialIndex++;
    // hide all images
    $("img").hide();
    // hide slider and slider label
    $("#slider").hide();
    $("#slider_label").hide();
    // update animal label
    $("#animal_label").text(DATA.trials[DATA.trialIndex].animal);
    // show animal label
    $("#animal_label").show();
    // set timeout for showing the image
    window.setTimeout(showImage, LABEL_DURATION);
  } else {
    // hide all images
    $("img").hide();
    // hide slider and slider label
    $("#slider").hide();
    $("#slider_label").hide();

    // get final data
    DATA.endTime = Date.now();
    DATA.duration = performance.now();
    DATA.id = DATA.prolificPID;
    console.debug("saving data");
    // post data to server
    $.ajax({
      url: "save",
      type: "POST",
      data: JSON.stringify(DATA),
      contentType: "application/json",
      success: () => {
        showEndPage();
      },
    }).fail(() => {
      console.log("there was an error with the $.post()");
      showEndPage();
    });
  }
}

// show the image to be rated
function showImage() {
  // hide animal label
  $("#animal_label").hide();
  // set slider and slider label value
  $("#slider").val(DEFAULT_RATING);
  updateSliderLabel();
  // show slider and slider label
  $("#slider").show();
  $("#slider_label").show();
  // show the image for the current trial
  let imageID = DATA.trials[DATA.trialIndex].imageID;
  $("#" + imageID).show();
}

// update the label showing the slider's value
function updateSliderLabel() {
  $("#slider_label").text($("#slider").val());
}

// submit a trial
function submitTrial() {
  // store response
  DATA.trials[DATA.trialIndex].rating = $("#slider").val();
  // begin next trial
  beginTrial();
}

// show end page, start Prolific redirect countdown
function showEndPage() {
  // change instruction text
  $("#instructions").text(
    "All done - thank you for participating!\r\n" +
      "You should be redirected to Prolific in a " +
      "few seconds.\r\nIf you aren't automatically " +
      "redirected, please click the link below."
  );
  // update link
  $("#prolific_link").attr("href", PROLIFIC_URL);
  $("#prolific_link").text("Click here to return to Prolific");
  // begin countdown
  let redirectTime = 5; // seconds
  let redirectTick = 1000; // milliseconds
  let countdownInterval = setInterval(() => {
    redirectTime--;
    $("#instructions").text(
      "All done - thank you for participating!\r\n" +
        "You should be redirected to Prolific in " +
        redirectTime +
        " seconds." +
        "\r\nIf you aren't automatically redirected, " +
        "please click the link below."
    );
    if (redirectTime <= 0) {
      clearInterval(countdownInterval);
      // window.location = PROLIFIC_URL;
    }
  }, redirectTick);
}

// run the setUp function when the page loads
$(window).on("load", () => {
  setUp();
});

// in-place Fisher-Yates (or Durstenfeld) shuffle
function shuffleArray(array) {
  let swapTo = array.length; // index of position to swap to
  let swapFrom = null; // index of element randomly selected to swap
  let temp = null; // holds a value for changing assignment
  // work back to front, swapping with random unswapped (earlier) elements
  while (swapTo > 0) {
    // pick an (unswapped) element from the back
    swapFrom = Math.floor(Math.random() * swapTo--);
    // swap it with the current element
    temp = array[swapTo];
    array[swapTo] = array[swapFrom];
    array[swapFrom] = temp;
  }
}
