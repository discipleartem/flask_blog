/**
 * EasyMDE on .js-markdown-editor textareas.
 * Preview / side-by-side disabled — display uses server-side render.
 */
(function () {
  "use strict";

  if (typeof EasyMDE === "undefined") {
    return;
  }

  var toolbar = [
    "bold",
    "italic",
    "heading",
    "|",
    "quote",
    "unordered-list",
    "ordered-list",
    "|",
    "link",
    "|",
    "guide",
  ];

  document.querySelectorAll("textarea.js-markdown-editor").forEach(function (el) {
    new EasyMDE({
      element: el,
      spellChecker: false,
      status: false,
      autofocus: false,
      forceSync: true,
      toolbar: toolbar,
      minHeight: el.rows && el.rows <= 4 ? "100px" : "200px",
    });
  });
})();
