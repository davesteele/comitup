

function setled(path) {

  var image = document.getElementById("ledimg");

  image.src = path;
}

function blink() {
  setled("img/ledoff.gif");

  request = new XMLHttpRequest();
  request.open("GET", "/blink", true);
  request.send()


  setTimeout(setled, 250, "img/ledon.gif");
  setTimeout(setled, 750, "img/ledoff.gif");
  setTimeout(setled, 1000, "img/ledoff.gif");
}
