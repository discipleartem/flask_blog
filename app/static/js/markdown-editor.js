/**
 * EasyMDE on .js-markdown-editor textareas.
 * Preview / side-by-side disabled — display uses server-side render.
 */
(function () {
  "use strict";

  if (typeof EasyMDE === "undefined") {
    return;
  }

  var PRESET_LANGS = [
    { id: "python", label: "Python" },
    { id: "html", label: "HTML" },
    { id: "javascript", label: "JS" },
    { id: "css", label: "CSS" },
  ];

  var LANG_RE = /^[a-zA-Z0-9_+#.-]{1,32}$/;

  function normalizeLang(raw) {
    var lang = (raw || "").trim().toLowerCase();
    if (lang === "js") {
      lang = "javascript";
    }
    if (!lang || !LANG_RE.test(lang)) {
      return "python";
    }
    return lang;
  }

  function ensureCodeLangModal() {
    var existing = document.getElementById("md-code-lang-modal");
    if (existing) {
      return existing;
    }

    var wrap = document.createElement("div");
    wrap.id = "md-code-lang-modal";
    wrap.className = "md-code-lang-modal";
    wrap.hidden = true;
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-modal", "true");
    wrap.setAttribute("aria-labelledby", "md-code-lang-title");

    var presets = PRESET_LANGS.map(function (item) {
      return (
        '<button type="button" class="btn btn-outline-secondary btn-sm md-code-lang-preset" data-lang="' +
        item.id +
        '">' +
        item.label +
        "</button>"
      );
    }).join("");

    wrap.innerHTML =
      '<div class="md-code-lang-dialog card border shadow">' +
      '<div class="card-body p-3">' +
      '<h2 id="md-code-lang-title" class="h6 mb-3">Язык блока кода</h2>' +
      '<div class="d-flex flex-wrap gap-2 mb-3">' +
      presets +
      "</div>" +
      '<label class="form-label small" for="md-code-lang-custom">Или укажите язык</label>' +
      '<input type="text" class="form-control form-control-sm mb-3" id="md-code-lang-custom" ' +
      'placeholder="например: sql, bash, rust" value="python" autocomplete="off">' +
      '<div class="d-flex justify-content-end gap-2">' +
      '<button type="button" class="btn btn-outline-secondary btn-sm" data-action="cancel">Отмена</button>' +
      '<button type="button" class="btn btn-dark btn-sm" data-action="insert">Вставить</button>' +
      "</div></div></div>";

    document.body.appendChild(wrap);
    return wrap;
  }

  function openCodeLangModal(onPick) {
    var modal = ensureCodeLangModal();
    var input = modal.querySelector("#md-code-lang-custom");
    var finished = false;

    function close() {
      modal.hidden = true;
      modal.classList.remove("is-open");
      document.removeEventListener("keydown", onKey);
    }

    function finish(lang) {
      if (finished) {
        return;
      }
      finished = true;
      close();
      onPick(normalizeLang(lang));
    }

    function onKey(ev) {
      if (ev.key === "Escape") {
        finished = true;
        close();
      } else if (ev.key === "Enter" && ev.target === input) {
        ev.preventDefault();
        finish(input.value);
      }
    }

    modal.onclick = function (ev) {
      var t = ev.target;
      if (t === modal) {
        finished = true;
        close();
        return;
      }
      if (t.matches("[data-action=cancel]")) {
        finished = true;
        close();
        return;
      }
      if (t.matches("[data-action=insert]")) {
        finish(input.value);
        return;
      }
      if (t.matches(".md-code-lang-preset")) {
        input.value = t.getAttribute("data-lang") || "python";
        finish(input.value);
      }
    };

    input.value = "python";
    modal.hidden = false;
    modal.classList.add("is-open");
    document.addEventListener("keydown", onKey);
    input.focus();
    input.select();
  }

  function insertFencedCode(editor, lang) {
    var cm = editor.codemirror;
    var selected = cm.getSelection();
    var body = selected || "";
    var block = "```" + lang + "\n" + body + "\n```";
    cm.replaceSelection(block);
    if (!selected) {
      var cur = cm.getCursor();
      cm.setCursor({ line: cur.line - 1, ch: 0 });
    }
    cm.focus();
  }

  var codeBlockButton = {
    name: "code-block",
    action: function (editor) {
      openCodeLangModal(function (lang) {
        insertFencedCode(editor, lang);
      });
    },
    className: "fa fa-code",
    title: "Блок кода",
  };

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
    codeBlockButton,
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
