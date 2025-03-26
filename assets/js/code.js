var codescroll = function () {
  var elements = document.querySelectorAll(".highlight > div.chroma");
  for (element of elements) {
    // Get the width of the screen
    let screenWidth = window.innerWidth;
    let threshold = screenWidth - 110;
    let firstChild = element.firstElementChild;
    if (firstChild.offsetWidth > threshold) {
      element.classList.add("scroll");
    } else {
      element.classList.remove("scroll");
    }
  }
};

codescroll();
window.onresize = codescroll;
