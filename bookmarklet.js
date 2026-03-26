// Citation to BibTeX bookmarklet (readable source)
// Minify and wrap in javascript:void(...) for use as a bookmark URL.
(function () {
  var GROBID = "https://lfoppiano-grobid-dev-full.hf.space";
  var text = window.getSelection().toString().trim();
  if (!text) {
    toast("Select a citation first", true);
    return;
  }

  toast("Converting...");

  fetch(GROBID + "/api/processCitation", {
    method: "POST",
    headers: { Accept: "application/x-bibtex" },
    body: new URLSearchParams({ citations: text, consolidateCitations: "1" }),
  })
    .then(function (r) {
      if (!r.ok) throw new Error("GROBID " + r.status);
      return r.text();
    })
    .then(function (bib) {
      bib = bib.trim();
      if (!bib) throw new Error("Could not parse citation");
      return navigator.clipboard.writeText(bib).then(function () {
        toast("BibTeX copied!");
      });
    })
    .catch(function (e) {
      toast(e.message, true);
    });

  function toast(msg, isError) {
    var el = document.getElementById("_bib_toast");
    if (el) el.remove();
    el = document.createElement("div");
    el.id = "_bib_toast";
    el.textContent = msg;
    el.style.cssText =
      "position:fixed;bottom:24px;right:24px;z-index:2147483647;" +
      "padding:12px 20px;border-radius:8px;font:14px/1.4 system-ui,sans-serif;" +
      "color:#fff;background:" +
      (isError ? "#c0392b" : "#2ecc71") +
      ";box-shadow:0 4px 12px rgba(0,0,0,.3);transition:opacity .3s;opacity:1;";
    document.body.appendChild(el);
    setTimeout(function () {
      el.style.opacity = "0";
      setTimeout(function () {
        el.remove();
      }, 300);
    }, 3000);
  }
})();
