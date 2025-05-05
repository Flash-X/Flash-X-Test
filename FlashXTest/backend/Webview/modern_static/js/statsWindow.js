var MSModel = 0;
var mouseX;  // x position of mouse pointer
var mouseY;  // y position of mouse pointer
var statsWindow;
var statsHeader;
var statsBody;
document.onmousemove = captureMouse;

function statsWindowInit() {
  if (document.all) {
    MSModel = 1;
  }
  statsWindow = document.getElementById("statsWindow");
  statsHeader = document.getElementById("statsHeader");
  statsBody   = document.getElementById("statsBody");
}

/* called when pointer hovers over a date */
function appear(header, body) {
  // delete all text already in the window
  while (statsHeader.hasChildNodes()) {
    statsHeader.removeChild(statsHeader.lastChild);
  }
  while (statsBody.hasChildNodes()) {
    statsBody.removeChild(statsBody.lastChild);
  }
  // put the new text in
  if (MSModel) {
    statsHeader.innerHTML = header;
    statsBody.innerHTML = body;
  } else {
    var range;
    var domfrag;

    range = document.createRange();
    range.setStartBefore(statsHeader);
    domfrag = range.createContextualFragment(header);
    statsHeader.appendChild(domfrag);
    range = document.createRange();
    range.setStartBefore(statsBody);
    domfrag = range.createContextualFragment(body);
    statsBody.appendChild(domfrag);
  }
  // width and height of new text will affect location
  setLocation();
  statsWindow.style.visibility = "visible";
}

/* called when pointer stops hovering over a date */
function disappear() {
  statsWindow.style.visibility = "hidden";
}

/* capture position of mouse pointer */
function captureMouse(e) {
  if (MSModel) {
    mouseX = event.clientX + document.body.scrollLeft;
    mouseY = event.clientY + document.body.scrollTop;
  } else {
    mouseX = e.pageX;
    mouseY = e.pageY;
  }
  setLocation();
}

/* set location of the floating DIV element */
function setLocation() {
  var leftEdge;     // x-coord of left edge of statsWindow
  var topEdge;      // y-coord of top edge of statsWindow
  var xOffset = 10; // horizontal offset from pointer
  var yOffset = 10; // vertical offset from pointer

  var winXOffset = (MSModel) ? document.body.scrollLeft : window.pageXOffset;
  var winWidth   = (MSModel) ? document.body.clientWidth : window.outerWidth;
  var winYOffset = (MSModel) ? document.body.scrollTop : window.pageYOffset;
  var winHeight  = (MSModel) ? document.body.clientHeight : window.outerHeight;

  if ((mouseX - winXOffset) > (winWidth / 2)) {
    leftEdge = mouseX - xOffset - statsWindow.offsetWidth;
    if (leftEdge < winXOffset) leftEdge = winXOffset;
  } else {
    leftEdge = mouseX + xOffset;
  }
  if ((mouseY - winYOffset) > (winHeight / 2)) {
    topEdge = mouseY - yOffset - statsWindow.offsetHeight;
    if (topEdge < winYOffset) topEdge = winYOffset;
  } else {
    topEdge = mouseY + yOffset;
  }

  statsWindow.style.left = leftEdge + "px";
  statsWindow.style.top = topEdge + "px";
}