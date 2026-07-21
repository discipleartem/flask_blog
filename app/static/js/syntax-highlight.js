/**
 * Кастомная подсветка синтаксиса для блоков <pre><code class="language-…">.
 * Языки: python, html, javascript/js, css; остальное — универсальный режим.
 */
(function (global) {
  "use strict";

  var ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };

  function escapeHtml(text) {
    return String(text).replace(/[&<>"]/g, function (ch) {
      return ESC[ch];
    });
  }

  function span(type, text) {
    return '<span class="syn syn-' + type + '">' + escapeHtml(text) + "</span>";
  }

  /**
   * Подсветка по упорядоченному списку правил { type, re }.
   * re должен иметь флаг g; совпадение с начала остатка — через lastIndex.
   */
  function highlightByRules(source, rules) {
    var out = "";
    var i = 0;
    var len = source.length;

    while (i < len) {
      var matched = false;
      var rest = source.slice(i);

      for (var r = 0; r < rules.length; r++) {
        var rule = rules[r];
        rule.re.lastIndex = 0;
        var m = rule.re.exec(rest);
        if (!m || m.index !== 0) {
          continue;
        }
        out += span(rule.type, m[0]);
        i += m[0].length;
        matched = true;
        break;
      }

      if (!matched) {
        out += escapeHtml(source.charAt(i));
        i += 1;
      }
    }
    return out;
  }

  var PYTHON_KEYWORDS =
    "False|None|True|and|as|assert|async|await|break|class|continue|def|del|" +
    "elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|" +
    "not|or|pass|raise|return|try|while|with|yield";

  var JS_KEYWORDS =
    "async|await|break|case|catch|class|const|continue|debugger|default|delete|" +
    "do|else|export|extends|finally|for|function|if|import|in|instanceof|let|" +
    "new|of|return|static|super|switch|this|throw|try|typeof|var|void|while|" +
    "with|yield|true|false|null|undefined";

  var rulesPython = [
    { type: "comment", re: /#.*/g },
    { type: "string", re: /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')/g },
    { type: "number", re: /\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b/g },
    { type: "decorator", re: /@[A-Za-z_]\w*/g },
    { type: "keyword", re: new RegExp("\\b(?:" + PYTHON_KEYWORDS + ")\\b", "g") },
    { type: "builtin", re: /\b(?:print|len|range|str|int|float|list|dict|set|tuple|bool|type|isinstance|open|super|self|cls)\b/g },
    { type: "function", re: /\b[A-Za-z_]\w*(?=\s*\()/g },
  ];

  var rulesJs = [
    { type: "comment", re: /\/\/.*|\/\*[\s\S]*?\*\//g },
    { type: "string", re: /`(?:\\.|[^`\\])*`|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g },
    { type: "number", re: /\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b/g },
    { type: "keyword", re: new RegExp("\\b(?:" + JS_KEYWORDS + ")\\b", "g") },
    { type: "function", re: /\b[A-Za-z_$]\w*(?=\s*\()/g },
  ];

  var rulesCss = [
    { type: "comment", re: /\/\*[\s\S]*?\*\//g },
    { type: "string", re: /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g },
    { type: "number", re: /#(?:[0-9a-fA-F]{3,8})\b|-?\d*\.?\d+(?:%|px|em|rem|vh|vw|s|ms|deg)?/g },
    { type: "keyword", re: /@(?:media|import|keyframes|font-face|supports|charset|layer)\b/g },
    { type: "property", re: /[a-z-]+(?=\s*:)/g },
    { type: "selector", re: /[.#]?[A-Za-z_][\w-]*/g },
  ];

  /** HTML: теги / атрибуты / строки / комментарии / сущности */
  function highlightHtml(source) {
    var out = "";
    var i = 0;
    var len = source.length;

    while (i < len) {
      if (source.startsWith("<!--", i)) {
        var endC = source.indexOf("-->", i + 4);
        if (endC === -1) {
          out += span("comment", source.slice(i));
          break;
        }
        out += span("comment", source.slice(i, endC + 3));
        i = endC + 3;
        continue;
      }

      if (source.charAt(i) === "<") {
        var endT = source.indexOf(">", i + 1);
        if (endT === -1) {
          out += escapeHtml(source.slice(i));
          break;
        }
        out += highlightHtmlTag(source.slice(i, endT + 1));
        i = endT + 1;
        continue;
      }

      if (source.charAt(i) === "&") {
        var endE = source.indexOf(";", i + 1);
        if (endE !== -1 && endE - i < 12) {
          out += span("entity", source.slice(i, endE + 1));
          i = endE + 1;
          continue;
        }
      }

      var next = source.indexOf("<", i);
      var amp = source.indexOf("&", i);
      var cut = len;
      if (next !== -1) {
        cut = Math.min(cut, next);
      }
      if (amp !== -1) {
        cut = Math.min(cut, amp);
      }
      out += escapeHtml(source.slice(i, cut));
      i = cut;
    }
    return out;
  }

  function highlightHtmlTag(tagText) {
    var out = "";
    var re =
      /^(<\/?)([A-Za-z][\w:-]*)([\s\S]*?)(\/?>)$/;
    var m = re.exec(tagText);
    if (!m) {
      return escapeHtml(tagText);
    }
    out += span("punctuation", m[1]);
    out += span("tag", m[2]);

    var attrs = m[3];
    var attrRe =
      /(\s+)([A-Za-z_:][\w:.-]*)(?:(\s*=\s*)("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s"'=<>`]+))?/g;
    var last = 0;
    var am;
    while ((am = attrRe.exec(attrs))) {
      if (am.index > last) {
        out += escapeHtml(attrs.slice(last, am.index));
      }
      out += escapeHtml(am[1]) + span("attr", am[2]);
      if (am[3]) {
        out += escapeHtml(am[3]) + span("string", am[4]);
      }
      last = am.index + am[0].length;
    }
    if (last < attrs.length) {
      out += escapeHtml(attrs.slice(last));
    }
    out += span("punctuation", m[4]);
    return out;
  }

  var rulesGeneric = [
    { type: "comment", re: /\/\/.*|#.*|\/\*[\s\S]*?\*\//g },
    { type: "string", re: /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`/g },
    { type: "number", re: /\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b/g },
    {
      type: "keyword",
      re: /\b(?:if|else|for|while|return|function|class|def|import|from|const|let|var|true|false|null|None|True|False|and|or|not|in|try|catch|except|finally|async|await|yield|break|continue|switch|case|default|public|private|protected|static|void|int|string|bool|new|this)\b/g,
    },
    { type: "function", re: /\b[A-Za-z_]\w*(?=\s*\()/g },
  ];

  var INDENT_SPACES = {
    python: 4,
    javascript: 2,
    html: 2,
    css: 2,
    generic: 4,
  };

  function normalizeLang(raw) {
    var lang = (raw || "").toLowerCase().replace(/^language-/, "");
    if (lang === "js" || lang === "jsx" || lang === "ts" || lang === "tsx") {
      return "javascript";
    }
    if (lang === "htm" || lang === "xml") {
      return "html";
    }
    if (lang === "py") {
      return "python";
    }
    return lang || "generic";
  }

  function indentWidthFor(lang) {
    var kind = normalizeLang(lang);
    return INDENT_SPACES[kind] || INDENT_SPACES.generic;
  }

  /**
   * Табы → пробелы по ширине отступа языка (PEP 8 / распространённый стиль web).
   * Уже стоящие пробелы не трогаем.
   */
  function expandTabsToSpaces(source, tabWidth) {
    var width = tabWidth > 0 ? tabWidth : 4;
    var lines = String(source).split("\n");
    var out = [];

    for (var li = 0; li < lines.length; li++) {
      var line = lines[li];
      var rebuilt = "";
      var col = 0;
      for (var i = 0; i < line.length; i++) {
        var ch = line.charAt(i);
        if (ch === "\t") {
          var n = width - (col % width);
          rebuilt += new Array(n + 1).join(" ");
          col += n;
        } else {
          rebuilt += ch;
          col += 1;
        }
      }
      out.push(rebuilt);
    }
    return out.join("\n");
  }

  function highlightSource(source, lang) {
    var kind = normalizeLang(lang);
    var width = indentWidthFor(kind);
    var text = expandTabsToSpaces(source, width);

    if (kind === "html") {
      return highlightHtml(text);
    }
    if (kind === "python") {
      return highlightByRules(text, rulesPython);
    }
    if (kind === "javascript") {
      return highlightByRules(text, rulesJs);
    }
    if (kind === "css") {
      return highlightByRules(text, rulesCss);
    }
    return highlightByRules(text, rulesGeneric);
  }

  function languageFromClass(className) {
    var parts = String(className || "").split(/\s+/);
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].indexOf("language-") === 0) {
        return parts[i].slice("language-".length);
      }
    }
    return "generic";
  }

  function highlightCodeElement(codeEl) {
    if (!codeEl || codeEl.nodeType !== 1) {
      return;
    }
    if (codeEl.getAttribute("data-syn") === "1") {
      return;
    }
    var lang = languageFromClass(codeEl.className);
    var width = indentWidthFor(lang);
    var source = codeEl.textContent || "";
    codeEl.innerHTML = highlightSource(source, lang);
    codeEl.setAttribute("data-syn", "1");
    codeEl.setAttribute("data-indent", String(width));
    codeEl.style.tabSize = String(width);
    codeEl.style.MozTabSize = String(width);
    codeEl.classList.add("syn-ready");
  }

  function highlightRoot(root) {
    var scope = root && root.querySelectorAll ? root : document;
    var nodes = scope.querySelectorAll("pre code[class*='language-'], pre code:not([class])");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      // Без class — тоже подсветим универсально
      if (!el.className) {
        el.className = "language-generic";
      }
      highlightCodeElement(el);
    }
  }

  global.FlaskBlogSyntax = {
    highlight: highlightRoot,
    highlightElement: highlightCodeElement,
    highlightSource: highlightSource,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      highlightRoot(document);
    });
  } else {
    highlightRoot(document);
  }
})(window);
