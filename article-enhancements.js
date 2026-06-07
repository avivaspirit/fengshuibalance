(function () {
  var content = document.querySelector(".article-content");
  if (!content) return;

  document.body.classList.add("article-page");

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function linkifyPlainText(text) {
    var html = escapeHtml(text);
    html = html.replace(
      /https?:\/\/(?:www\.)?miracles369-store\.com[^\s&lt;]*/gi,
      function (url) {
        return (
          '<a href="' +
          url +
          '" target="_blank" rel="noopener noreferrer" class="article-brand-link">' +
          url +
          "</a>"
        );
      }
    );
    html = html.replace(
      /https?:\/\/(?:www\.)?avivaspirit\.com[^\s&lt;]*/gi,
      function (url) {
        return (
          '<a href="' +
          url +
          '" target="_blank" rel="noopener noreferrer" class="article-brand-link">' +
          url +
          "</a>"
        );
      }
    );
    html = html.replace(/\bMiracles369\b/g, function (match, offset, full) {
      var before = full.charAt(offset - 1) || "";
      if (/[\/\w]/.test(before)) return match;
      return (
        '<a href="https://www.miracles369-store.com/" target="_blank" rel="noopener noreferrer" class="article-brand-link">Miracles369</a>'
      );
    });
    html = html.replace(/\bAviva Spirit\b/g, function (match, offset, full) {
      var before = full.charAt(offset - 1) || "";
      if (/[\/\w]/.test(before)) return match;
      return (
        '<a href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer" class="article-brand-link">Aviva Spirit</a>'
      );
    });
    return html;
  }

  function isDivider(line) {
    return /^(-{3,}|={3,}|\*{3,}|\.{3,})$/.test(line);
  }

  function isCallout(line) {
    return /^(\*{2,3}|#{1,3}\s|>>>)/.test(line);
  }

  function isListItem(line) {
    return /^([-•*]|\d+[\.)])\s+/.test(line);
  }

  function endsSentence(line) {
    return /[.!?…:]$/.test(line) || /ครับ$|ค่ะ$|นะ$|เลย$|ด้วย$/.test(line);
  }

  function shouldContinue(prev, line) {
    if (!prev) return false;
    if (endsSentence(prev)) return false;
    if (/^\d+[\.)]\s/.test(line)) return false;
    if (isCallout(line) || isListItem(line) || isDivider(line)) return false;
    if (prev.length > 120) return false;
    return /[,，(\[]$/.test(prev) || line.length < 48;
  }

  function formatArticleBody(text) {
    var normalized = (text || "").replace(/\r\n/g, "\n").trim();
    if (!normalized) return "";

    var lines = normalized.split("\n");
    var html = [];
    var paragraph = [];
    var listItems = [];

    function flushParagraph() {
      if (!paragraph.length) return;
      var joined = paragraph.join(" ").replace(/\s+/g, " ").trim();
      paragraph = [];
      if (!joined) return;
      html.push("<p>" + linkifyPlainText(joined) + "</p>");
    }

    function flushList() {
      if (!listItems.length) return;
      html.push('<ul class="article-list">');
      listItems.forEach(function (item) {
        html.push("<li>" + linkifyPlainText(item) + "</li>");
      });
      html.push("</ul>");
      listItems = [];
    }

    lines.forEach(function (rawLine) {
      var line = rawLine.trim();
      if (!line) {
        flushList();
        flushParagraph();
        return;
      }

      if (isDivider(line)) {
        flushList();
        flushParagraph();
        html.push('<hr class="article-divider" />');
        return;
      }

      if (isListItem(line)) {
        flushParagraph();
        listItems.push(line.replace(/^([-•*]|\d+[\.)])\s+/, ""));
        return;
      }

      if (isCallout(line)) {
        flushList();
        flushParagraph();
        html.push('<p class="article-callout">' + linkifyPlainText(line) + "</p>");
        return;
      }

      flushList();
      var prev = paragraph[paragraph.length - 1] || "";
      if (paragraph.length && shouldContinue(prev, line)) {
        paragraph.push(line);
      } else {
        flushParagraph();
        paragraph.push(line);
      }
    });

    flushList();
    flushParagraph();
    return html.join("");
  }

  if (!content.dataset.formatted) {
    content.innerHTML = formatArticleBody(content.textContent || "");
    content.dataset.formatted = "true";
    content.dataset.brandLinked = "true";
  }

  var hasAviva = /avivaspirit|aviva\s*spirit/i.test(content.textContent || "");
  var hasMiracles = /miracles369/i.test(content.textContent || "");

  if (document.querySelector(".article-related-brand")) return;

  var footer = document.querySelector(".article-footer-cta");
  if (!footer) return;

  var sectionMeta = document.querySelector('meta[property="article:section"]');
  var isSpiritArticle = sectionMeta && sectionMeta.content === "ศาลและตี่จู้";

  if (!isSpiritArticle && !hasAviva && !hasMiracles) return;

  var aside = document.createElement("aside");
  aside.className = "article-related-brand";

  if (isSpiritArticle) {
    aside.innerHTML =
      '<p class="article-related-brand__eyebrow">แบรนด์ในเครือ · ศาลและตี่จู้</p>' +
      "<h3>Aviva Spirit — ตู้ศาลเจ้าที่และตี่จู้หินอ่อน Modern Luxury</h3>" +
      '<p>อาจารย์สุภชัยเป็นผู้ก่อตั้ง <a href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer">Aviva Spirit</a> ' +
      "แบรนด์ตู้ศาลพระภูมิและตี่จู้เอี๊ยหินอ่อนโมเดิร์นรายแรกในไทยที่จดลิขสิทธิ์และสิทธิบัตร " +
      "ออกแบบตามหลักฮวงจุ้ยโดยได้รับเกียรติจากอาจารย์เกรียงไกร บุญธกานนท์เป็นที่ปรึกษา " +
      'ดูแคตตาล็อกผลงาน บทความศาลเจ้าที่ และตู้ตี่จู้ได้ที่เว็บไซต์ Aviva Spirit — หรืออ่าน <a href="../brand-portfolio.html">แบรนด์ในเครือของอาจารย์สุภชัย</a></p>' +
      '<a class="button secondary article-related-brand__cta" href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer">เยี่ยมชม Aviva Spirit</a>';
  } else {
    var blocks = [
      '<p class="article-related-brand__eyebrow">แบรนด์ในเครือ · อาจารย์สุภชัย</p>',
    ];
    if (hasAviva) {
      blocks.push(
        "<h3>Aviva Spirit — ตู้ศาลเจ้าที่และตี่จู้หินอ่อน Modern Luxury</h3>" +
          '<p><a href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer">Aviva Spirit</a> คือแบรนด์ตู้ศาลพระภูมิและตี่จู้เอี๊ยหินอ่อนโมเดิร์นรายแรกในไทยที่จดลิขสิทธิ์และสิทธิบัตร ออกแบบตามหลักฮวงจุ้ยโดยอาจารย์สุภชัย วิวัฒนะประเสริฐ</p>' +
          '<a class="button secondary article-related-brand__cta" href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer">เยี่ยมชม Aviva Spirit</a>'
      );
    }
    if (hasMiracles) {
      blocks.push(
        "<h3>Miracles369 — แผ่นกั้นดาวและของเสริมฮวงจุ้ย</h3>" +
          '<p><a href="https://www.miracles369-store.com/" target="_blank" rel="noopener noreferrer">Miracles369</a> คือร้านของเสริมฮวงจุ้ยและแผ่นกั้นดาวจากอาจารย์สุภชัย สั่งซื้อออนไลน์ได้ที่เว็บไซต์ Miracles369</p>' +
          '<a class="button secondary article-related-brand__cta" href="https://www.miracles369-store.com/" target="_blank" rel="noopener noreferrer">เยี่ยมชม Miracles369</a>'
      );
    }
    blocks.push(
      '<p class="article-related-brand__more"><a href="../brand-portfolio.html">ดูแบรนด์ในเครือทั้งหมดของอาจารย์สุภชัย</a></p>'
    );
    aside.innerHTML = blocks.join("");
  }

  footer.parentNode.insertBefore(aside, footer);
})();
