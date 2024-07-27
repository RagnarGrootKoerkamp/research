var codescroll = function () {
  console.log("codescroll");
  var elements = document.querySelectorAll(".highlight > div.chroma");
  for (element of elements) {
    // Get the width of the screen
    let screenWidth = window.innerWidth;
    let threshold = screenWidth - 110;
    let firstChild = element.firstElementChild;
    console.log(
      screenWidth,
      threshold,
      firstChild.offsetWidth,
      element,
      firstChild,
    );
    if (firstChild.offsetWidth > threshold) {
      element.classList.add("scroll");
    } else {
      element.classList.remove("scroll");
    }
  }
};

codescroll();
window.onresize = codescroll;
