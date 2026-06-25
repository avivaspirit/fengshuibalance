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
      paragraph.push(line);
    });

    flushList();
    flushParagraph();
    return html.join("");
  }

  if (!content.dataset.formatted && !content.querySelector("p")) {
    content.innerHTML = formatArticleBody(content.textContent || "");
    content.dataset.formatted = "true";
    content.dataset.brandLinked = "true";
  } else {
    document.body.classList.add("article-page");
  }

  var hasAviva = /avivaspirit|aviva\s*spirit/i.test(content.textContent || "");
  var hasMiracles = /miracles369/i.test(content.textContent || "");

  if (document.querySelector(".article-related-brand")) return;

  var footer = document.querySelector(".article-footer-cta");
  if (!footer) return;

  var sectionMeta = document.querySelector('meta[property="article:section"]');
  var isSpiritArticle = sectionMeta && sectionMeta.content === "ศาลและตี่จู้";

  // Skip brand aside if no relevance (but DON'T return — enhancements below should still run)
  if (isSpiritArticle || hasAviva || hasMiracles) {

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
  } // end brand aside conditional

  // --- Related articles navigation ---
  var main = document.querySelector(".article-page-main");
  if (main && !main.querySelector(".article-more-links")) {
    var moreLinks = document.createElement("nav");
    moreLinks.className = "article-more-links";
    moreLinks.innerHTML =
      '<a href="../articles.html" class="button secondary">← กลับสู่คลังความรู้ทั้งหมด</a>' +
      '<a href="../index.html#services" class="button secondary">ปรึกษาฮวงจุ้ย →</a>';
    main.appendChild(moreLinks);
  }

  // --- Inject BreadcrumbList schema ---
  (function() {
    var existingSchemas = document.querySelectorAll('script[type="application/ld+json"]');
    var articleSchema = null;
    existingSchemas.forEach(function(s) {
      try {
        var d = JSON.parse(s.textContent);
        if (d["@type"] === "Article") articleSchema = d;
      } catch(e) {}
    });
    if (articleSchema) {
      var breadcrumbLd = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "Fengshui Balance", "item": "https://fengshuibalance.vercel.app/"},
          {"@type": "ListItem", "position": 2, "name": "คลังความรู้", "item": "https://fengshuibalance.vercel.app/articles.html"},
          {"@type": "ListItem", "position": 3, "name": articleSchema.headline || "บทความ"}
        ]
      };
      var scriptEl = document.createElement("script");
      scriptEl.type = "application/ld+json";
      scriptEl.textContent = JSON.stringify(breadcrumbLd);
      document.head.appendChild(scriptEl);
    }
  })();

  // === READING EXPERIENCE ENHANCEMENTS ===

  // 1. Reading time estimate
  (function() {
    var meta = document.querySelector(".article-meta");
    if (!meta) return;
    var text = (content.textContent || "").trim();
    var charCount = text.length;
    // Thai reading speed: ~400 chars/min (slower than English due to script complexity)
    var minutes = Math.max(1, Math.round(charCount / 400));
    var timeSpan = document.createElement("span");
    timeSpan.textContent = "⏱ " + minutes + " นาทีอ่าน";
    meta.appendChild(timeSpan);
  })();

  // 2. Reading progress bar
  (function() {
    var bar = document.createElement("div");
    bar.className = "reading-progress";
    bar.innerHTML = '<div class="reading-progress-fill"></div>';
    document.body.appendChild(bar);
    var fill = bar.querySelector(".reading-progress-fill");
    function updateProgress() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      fill.style.width = Math.min(100, pct) + "%";
    }
    window.addEventListener("scroll", updateProgress, { passive: true });
    updateProgress();
  })();

  // 3. Back to top button
  (function() {
    var btn = document.createElement("button");
    btn.className = "back-to-top";
    btn.setAttribute("aria-label", "กลับขึ้นบน");
    btn.innerHTML = "↑";
    btn.style.display = "none";
    document.body.appendChild(btn);
    window.addEventListener("scroll", function() {
      btn.style.display = window.scrollY > 600 ? "flex" : "none";
    }, { passive: true });
    btn.addEventListener("click", function() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  })();

  // 4. Share button (Facebook)
  (function() {
    var article = document.querySelector(".article-card-detail");
    if (!article) return;
    var url = window.location.href;
    var shareWrap = document.createElement("div");
    shareWrap.className = "article-share";
    shareWrap.innerHTML =
      '<span class="article-share-label">แชร์บทความ</span>' +
      '<a class="article-share-btn article-share-fb" href="https://www.facebook.com/sharer/sharer.php?u=' +
      encodeURIComponent(url) +
      '" target="_blank" rel="noopener noreferrer" aria-label="แชร์ไป Facebook">Facebook</a>' +
      '<a class="article-share-btn article-share-line" href="https://social-plugins.line.me/lineit/share?url=' +
      encodeURIComponent(url) +
      '" target="_blank" rel="noopener noreferrer" aria-label="แชร์ไป LINE">LINE</a>' +
      '<button class="article-share-btn article-share-copy" aria-label="คัดลอกลิงก์">คัดลอกลิงก์</button>';
    var header = document.querySelector(".article-header");
    if (header) {
      header.appendChild(shareWrap);
    }
    var copyBtn = shareWrap.querySelector(".article-share-copy");
    copyBtn.addEventListener("click", function() {
      navigator.clipboard.writeText(url).then(function() {
        copyBtn.textContent = "✓ คัดลอกแล้ว";
        setTimeout(function() { copyBtn.textContent = "คัดลอกลิงก์"; }, 2000);
      });
    });
  })();

  // 5. Related articles by category
  (function() {
    var main = document.querySelector(".article-page-main");
    if (!main) return;
    if (main.querySelector(".article-related")) return;

    // Extract current article category from the eyebrow
    var eyebrow = document.querySelector(".article-header .eyebrow");
    if (!eyebrow) return;
    var currentCategory = eyebrow.textContent.trim();

    // Extract current article ID from URL
    var match = window.location.pathname.match(/wei-(\d+)\.html/);
    if (!match) return;
    var currentId = "wei-" + match[1];

    // Load articles-full.js data to find related
    var script = document.createElement("script");
    script.src = "../articles-full.js";
    script.onload = function() {
      if (!window.FENGSHUI_ARTICLES_FULL) return;
      var all = window.FENGSHUI_ARTICLES_FULL;

      // Find current article to get its category/tags
      var current = all.find(function(a) { return a.id === currentId; });
      if (!current) return;

      var cat = current.category || "";
      var tags = current.tags || [];

      // Score related articles: same category = +2, shared tag = +1 each, high WEI = +1
      var scored = all
        .filter(function(a) { return a.id !== currentId && len(a.body) >= 600; })
        .map(function(a) {
          var score = 0;
          if (a.category === cat) score += 2;
          if (a.tags) {
            a.tags.forEach(function(t) {
              if (tags.indexOf(t) !== -1) score += 1;
            });
          }
          var wei = (a.metrics && a.metrics.wei) || 0;
          if (wei > 1000) score += 1;
          if (wei > 5000) score += 1;
          return { a: a, score: score };
        })
        .filter(function(x) { return x.score > 0; })
        .sort(function(x, y) { return y.score - x.score; })
        .slice(0, 3);

      if (!scored.length) return;

      function len(body) {
        return (body || "").trim().length;
      }

      var html = '<div class="article-related">';
      html += '<p class="article-related__label">บทความที่เกี่ยวข้อง</p>';
      html += '<div class="article-related__grid">';
      scored.forEach(function(item) {
        var a = item.a;
        var title = (a.title || "").replace(/\s+/g, " ").trim();
        if (title.length > 70) title = title.substring(0, 68) + "…";
        var wei = (a.metrics && a.metrics.wei) || 0;
        var weiLabel = wei >= 1000 ? (wei / 1000).toFixed(1) + "k" : wei;
        html +=
          '<a class="article-related__card" href="' + a.id + ".html" + '">' +
          "<strong>" + escapeHtml(title) + "</strong>" +
          '<small>📈 ' + weiLabel + " · " + (a.date || "").substring(0, 7) + "</small>" +
          "</a>";
      });
      html += "</div></div>";

      var div = document.createElement("div");
      div.innerHTML = html;
      var related = div.firstChild;

      // Insert before the footer CTA
      var footer = main.querySelector(".article-footer-cta");
      if (footer) {
        main.insertBefore(related, footer);
      } else {
        main.appendChild(related);
      }
    };
    document.head.appendChild(script);
  })();

})();
