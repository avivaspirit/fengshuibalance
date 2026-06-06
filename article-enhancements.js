(function () {
  var content = document.querySelector(".article-content");
  if (!content) return;

  var rawText = content.textContent || "";
  var hasAviva = /avivaspirit|aviva\s*spirit/i.test(rawText);
  var hasMiracles = /miracles369/i.test(rawText);

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
    html = html.replace(
      /(?<![/\w])Miracles369\b/g,
      '<a href="https://www.miracles369-store.com/" target="_blank" rel="noopener noreferrer" class="article-brand-link">Miracles369</a>'
    );
    html = html.replace(
      /(?<![/\w])Aviva Spirit\b/g,
      '<a href="https://www.avivaspirit.com/" target="_blank" rel="noopener noreferrer" class="article-brand-link">Aviva Spirit</a>'
    );
    return html;
  }

  if (!content.dataset.brandLinked && (hasAviva || hasMiracles)) {
    content.innerHTML = linkifyPlainText(rawText);
    content.dataset.brandLinked = "true";
  }

  if (document.querySelector(".article-related-brand")) return;

  var footer = document.querySelector(".article-footer-cta");
  if (!footer) return;

  var sectionMeta = document.querySelector('meta[property="article:section"]');
  var isSpiritArticle =
    sectionMeta && sectionMeta.content === "ศาลและตี่จู้";

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
    var blocks = [];
    blocks.push(
      '<p class="article-related-brand__eyebrow">แบรนด์ในเครือ · อาจารย์สุภชัย</p>'
    );

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
