import init from "./pkg/suffix_array_construction.js";
// TODO: fix the import using
// https://stackoverflow.com/questions/61986932/how-to-pass-a-string-from-js-to-wasm-generated-through-rust-using-wasm-bindgen-w
init()
  .then((wasm) => {
    console.log(wasm);
    const canvas = document.getElementById("drawing");
    console.log(canvas);
    const context = canvas.getContext("2d");
    console.log(context);

    const string = document.getElementById("string");
    string.addEventListener("change", (event) => {
      wasm.update_string();
      wasm.draw();
    });

    const next = document.getElementById("next");
    next.addEventListener("click", () => {
      wasm.next();
      wasm.draw();
    });

    const prev = document.getElementById("prev");
    prev.addEventListener("click", () => {
      wasm.prev();
      wasm.draw();
    });

    wasm.draw();

    document.onkeydown = function (e) {
      switch (e.keyCode) {
        case 37: // left
          wasm.prev();
          wasm.draw();
          return false;
        case 39: // right
          wasm.next();
          wasm.draw();
          return false;
        case 38: // up
          break;
        case 40: // down
          break;
      }
      return true;
    };
  })
  .catch(console.error);
