
function follow() {
  var url = window.location.pathname;

  var param;

  var request = new XMLHttpRequest();
  request.onload = function() {
    console.log("Successfully followed question");
  };
  request.onerror = function() {
    console.log("Failed to followed question");
  };

  request.open("POST", "/ajax", true);
  request.send(param);
}
