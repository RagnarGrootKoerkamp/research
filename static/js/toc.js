let observer = new IntersectionObserver(handler, {
  threshold: [0],
});
let paragraphs = [...document.querySelectorAll("article > div > *")];
let submenu = [...document.querySelectorAll(".toc a")];
function previousHeaderId(p) {
  while (p && !p.matches("h1, h2, h3, h4")) {
    p = p.previousElementSibling;
  }
  return p?.id;
}
let paragraphMenuMap = paragraphs.reduce((acc, p) => {
  let h = previousHeaderId(p);
  p.previousHeader = h;
  if (h) {
    let entry = submenu.find((a) => decodeURIComponent(a.hash) === "#" + h);
    acc[h] = entry;
  }
  return acc;
}, {});

paragraphs.forEach((elem) => observer.observe(elem));

let selection;
function handler(updates) {
  selection = (selection || updates).map(
    (s) => updates.find((e) => e.target === s.target) || s,
  );
  // Clear all.
  for (s of selection) {
    if (!s.isIntersecting) {
      paragraphMenuMap[s.target.previousHeader]?.parentElement.classList.remove(
        "selected",
        "parent",
      );
    }
  }
  // Set all.
  for (s of selection) {
    if (s.isIntersecting) {
      let parentElem = paragraphMenuMap[s.target.previousHeader]?.closest("li");
      // ensure that parent menu entries are selected too
      parentElem?.classList.add("selected");
      while (parentElem) {
        parentElem?.classList.add("parent");
        parentElem = parentElem.parentElement.closest("li");
      }
    }
  }
}
