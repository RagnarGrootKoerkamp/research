var fnTooltip = function () {
  let refs = document.querySelectorAll(".footnote-ref");
  for (ref of refs) {
    var parent = ref.parentElement;
    var id = ref.getAttribute("href").substr(1);
    var footnote = document.getElementById(id).childNodes[0].cloneNode(true);
    for (backref of footnote.querySelectorAll(".footnote-backref")) {
      backref.remove();
    }
    outer = document.createElement("span");
    outer.className = "fn-tooltip";
    number = document.createElement("span");
    number.className = "fn-number";
    number.append(ref.innerHTML);
    outer.append(number);
    inner = document.createElement("span");
    inner.className = "fn-text";
    inner.append(footnote.cloneNode(true));
    outer.append(inner);
    parent.append(outer);
  }
};

fnTooltip();
