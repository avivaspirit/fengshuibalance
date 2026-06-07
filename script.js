const root = document.documentElement;
const langToggle = document.querySelector("[data-lang-toggle]");
const langLabel = document.querySelector("[data-lang-label]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");
const navBackdrop = document.querySelector("[data-nav-backdrop]");
const recommendedGrid = document.querySelector("[data-recommended-grid]");
const articleGrid = document.querySelector("[data-article-grid]");
const articleSearch = document.querySelector("[data-article-search]");
const articleFilters = document.querySelector("[data-article-filters]");
const articleCount = document.querySelector("[data-article-count]");
const loadMore = document.querySelector("[data-load-more]");
const articleDialog = document.querySelector("[data-article-dialog]");
const adminDialog = document.querySelector("[data-admin-dialog]");
const adminForm = document.querySelector("[data-admin-form]");
const counters = document.querySelectorAll("[data-counter]");

let activeLang = localStorage.getItem("fengshui-balance-lang") || "en";
let activeFilter = "all";
let visibleLimit = 6;
let activeArticleId = null;
let bookmarkedIds = JSON.parse(localStorage.getItem("fengshui-read-later") || "[]");
let editorMode = new URLSearchParams(location.search).has("edit") || location.hash === "#edit";
const articleVersion = "titles-readable-2026-06-06";
const savedVersion = localStorage.getItem("fengshui-balance-articles-version");
const savedArticles = JSON.parse(localStorage.getItem("fengshui-balance-articles") || "null");
const sourceArticles = window.FENGSHUI_ARTICLES_FULL || window.FENGSHUI_ARTICLES || [];
let articles =
  savedVersion === articleVersion && Array.isArray(savedArticles) && savedArticles.length >= sourceArticles.length
    ? savedArticles
    : sourceArticles;

function applyLanguage(lang) {
  activeLang = lang;
  root.lang = lang;
  document.querySelectorAll("[data-en][data-th]").forEach((node) => {
    node.textContent = node.dataset[lang];
  });
  updateCounterSuffixes();
  langLabel && (langLabel.textContent = lang === "en" ? "TH" : "EN");
  document.title =
    lang === "en"
      ? "Fengshui Balance | Ajarn Suppachai Vivattanaprasert"
      : "Fengshui Balance | อาจารย์ สุภชัย วิวัฒนะประเสริฐ";
  localStorage.setItem("fengshui-balance-lang", lang);
}

function closeMenu() {
  menu?.classList.remove("is-open");
  menuToggle?.classList.remove("is-open");
  menuToggle?.setAttribute("aria-expanded", "false");
  document.body.classList.remove("nav-open");
  if (navBackdrop) navBackdrop.hidden = true;
}

function openMenu() {
  menu?.classList.add("is-open");
  menuToggle?.classList.add("is-open");
  menuToggle?.setAttribute("aria-expanded", "true");
  document.body.classList.add("nav-open");
  if (navBackdrop) navBackdrop.hidden = false;
}

function updateCounterSuffixes() {
  counters.forEach((counter) => {
    const suffix = counter.querySelector(".counter-suffix");
    suffix.textContent = counter.dataset[activeLang === "en" ? "suffixEn" : "suffixTh"] || "";
  });
}

function animateCounter(counter) {
  if (counter.dataset.done === "true") return;
  counter.dataset.done = "true";
  const value = counter.querySelector(".counter-value");
  const target = Number(counter.dataset.target || 0);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) {
    value.textContent = target.toLocaleString();
    return;
  }
  const duration = 1200;
  const start = performance.now();
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  function tick(now) {
    const progress = Math.min((now - start) / duration, 1);
    value.textContent = Math.round(target * easeOut(progress)).toLocaleString();
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

function setupCounters() {
  if (!("IntersectionObserver" in window)) {
    counters.forEach(animateCounter);
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.45 }
  );
  counters.forEach((counter) => observer.observe(counter));
}

function cleanExcerptText(text) {
  if (!text) return "";
  let clean = text;
  clean = clean.replace(/https?:\/\/\S+/gi, "");
  clean = clean.replace(/\*+/g, "");
  clean = clean.replace(/[()\[\]{}]/g, "");
  clean = clean.replace(/[-=_.~·•]{2,}/g, " ");
  clean = clean.replace(/\p{Emoji_Presentation}/gu, "");
  clean = clean.replace(/\p{Extended_Pictographic}/gu, "");
  clean = clean.replace(/\s+/g, " ").trim();
  return clean;
}

function excerpt(text, length = 120) {
  const clean = cleanExcerptText(text);
  return clean.length > length ? `${clean.slice(0, length).trim()}...` : clean;
}

const CATEGORY_META = {
  all: { en: "All", th: "ทั้งหมด" },
  saved: { en: "Saved", th: "ที่บันทึกไว้" },
  timing: { en: "Auspicious Timing", th: "ฤกษ์ยาม" },
  spirit: { en: "Spirit House", th: "ศาลและตี่จู้" },
  shop: { en: "Shop", th: "ร้านค้า" },
  office: { en: "Office", th: "ออฟฟิศ" },
  home: { en: "Home", th: "บ้าน" },
  factory: { en: "Factory", th: "โรงงาน" },
  astrology: { en: "Destiny", th: "ดวงจีน" },
  lineage: { en: "Lineage", th: "สายวิชา" },
  general: { en: "Fengshui Notes", th: "บันทึกฮวงจุ้ย" },
  business: { en: "Business", th: "ธุรกิจ" },
  yearly: { en: "Yearly", th: "รายปี" },
  energy: { en: "Energy", th: "พลังงาน" },
  interactive: { en: "Community", th: "ชุมชน" },
};

const CHIP_ICONS = {
  timing: "M2 4.5h12v9H2zM5 2.5V4M11 2.5V4",
  spirit: "M3 13V6l5-3.5L13 6v7",
  shop: "M3 6h10l1.2 7H1.8z",
  office: "M3 13V5h10v8M6 5V3h4v2",
  home: "M2.5 12.5V7L8 3l5.5 4v5.5",
  factory: "M2 13V8l4-2v7M8 13V6l4-1.5V13",
  astrology: "M8 3l1.4 4.3H14l-3.7 2.7 1.4 4.3L8 11.6 4.3 14.3l1.4-4.3L2 7.3h4.6z",
  lineage: "M4 4h8v9H4z",
  general: "M4 4h8v9H4z",
  business: "M3 6h10v7H3z",
  yearly: "M2 4.5h12v9H2z",
  energy: "M8 2v6l4 2",
  interactive: "M3 8c0-2.8 2.2-5 5-5s5 2.2 5 5",
  saved: "M4 3.5h8v9l-4-2.5-4 2.5z",
  all: "M8 3v10",
};

function chipIconHtml(category) {
  const path = CHIP_ICONS[category] || CHIP_ICONS.general;
  return `<span class="chip-icon" aria-hidden="true"><svg viewBox="0 0 16 16" width="13" height="13" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="${path}" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/></svg></span>`;
}

function categoryLabel(category) {
  const meta = CATEGORY_META[category];
  if (!meta) return category;
  return activeLang === "en" ? meta.en : meta.th;
}

function categoryChipHtml(category) {
  const meta = CATEGORY_META[category];
  if (!meta) return `<span class="article-chip">${category}</span>`;
  const label = activeLang === "en" ? meta.en : meta.th;
  return `<span class="article-chip">${chipIconHtml(category)}<span class="chip-label">${label}</span></span>`;
}

function articleTags(article) {
  if (Array.isArray(article.tags) && article.tags.length) return article.tags.slice(0, 2);
  return article.category ? [article.category] : ["general"];
}

function renderArticleChips(article) {
  return `<div class="article-chip-row">${articleTags(article)
    .map((tag) => categoryChipHtml(tag))
    .join("")}</div>`;
}

function popularityLabel(article) {
  if (!article.metrics?.wei) return "";
  const score = Math.round(article.metrics.wei).toLocaleString();
  return activeLang === "en" ? ` · Popularity ${score}` : ` · ความนิยม ${score}`;
}

function saveArticles() {
  localStorage.setItem("fengshui-balance-articles", JSON.stringify(articles));
  localStorage.setItem("fengshui-balance-articles-version", articleVersion);
}

function toggleBookmark(id) {
  const index = bookmarkedIds.indexOf(id);
  if (index === -1) {
    bookmarkedIds.push(id);
  } else {
    bookmarkedIds.splice(index, 1);
  }
  localStorage.setItem("fengshui-read-later", JSON.stringify(bookmarkedIds));
  renderArticles();
}

const hasArticleArchive = Boolean(articleGrid && articleSearch && articleFilters && articleCount && loadMore);
const homepagePreviewCount = 6;

function filteredArticles() {
  const q = (articleSearch?.value || "").trim().toLowerCase();
  let list = articles;
  if (activeFilter === "saved") {
    list = articles.filter((article) => bookmarkedIds.includes(article.id));
  } else {
    list = articles.filter(
      (article) =>
        !article.recommended &&
        (activeFilter === "all" || articleTags(article).includes(activeFilter))
    );
  }
  return list
    .filter((article) => {
      const haystack = `${article.title} ${article.body} ${articleTags(article).join(" ")}`.toLowerCase();
      return !q || haystack.includes(q);
    })
    .sort((a, b) => (b.metrics?.wei || 0) - (a.metrics?.wei || 0));
}

function recommendedArticles() {
  return articles
    .filter((article) => article.recommended)
    .sort((a, b) => (a.recommendedRank || 999) - (b.recommendedRank || 999));
}

function renderFilters() {
  if (!articleFilters) return;
  const categories = [
    "all",
    "saved",
    ...new Set(articles.flatMap((article) => articleTags(article))),
  ];
  articleFilters.innerHTML = categories
    .map(
      (category) =>
        `<button type="button" class="${category === activeFilter ? "is-active" : ""}" data-filter="${category}">${categoryLabel(category)}</button>`
    )
    .join("");
}

function homepageFeaturedArticles() {
  const picks = recommendedArticles();
  const featured = [];
  const seen = new Set();

  picks.forEach((article) => {
    if (featured.length >= homepagePreviewCount || seen.has(article.id)) return;
    seen.add(article.id);
    featured.push(article);
  });

  if (featured.length < homepagePreviewCount) {
    [...articles]
      .sort((a, b) => (b.metrics?.wei || 0) - (a.metrics?.wei || 0))
      .forEach((article) => {
        if (featured.length >= homepagePreviewCount || seen.has(article.id)) return;
        seen.add(article.id);
        featured.push(article);
      });
  }

  return featured.slice(0, homepagePreviewCount);
}

function renderRecommendedCard(article, rank) {
  const isBookmarked = bookmarkedIds.includes(article.id);
  const displayRank = rank ?? article.recommendedRank ?? article.displayRank;
  return `
        <article class="recommended-card">
          <a href="articles/${article.id}.html" class="card-link" data-open-article="${article.id}">
            ${displayRank ? `<span class="recommend-rank">No. ${displayRank}</span>` : ""}
            <div class="card-image-wrapper">
              <img src="${article.image}" alt="${article.alt}" loading="lazy" width="960" height="540">
            </div>
            <div class="card-content">
              ${renderArticleChips(article)}
              <strong>${article.title}</strong>
              ${article.seoKeyword ? `<em class="keyword-tag">${article.seoKeyword}</em>` : ""}
              <small>${article.date || "Fengshui Balance"}${popularityLabel(article)}</small>
              <p>${excerpt(article.body, 120)}</p>
            </div>
          </a>
          <div class="card-footer">
            <a href="articles/${article.id}.html" class="read-more-link" data-open-article="${article.id}">
              <span>${activeLang === "en" ? "Read Article" : "อ่านบทความ"} &rarr;</span>
            </a>
            <button class="bookmark-btn ${isBookmarked ? "is-saved" : ""}" data-bookmark="${article.id}" aria-label="${isBookmarked ? "Remove Bookmark" : "Save for Later"}">
              <span class="bookmark-icon">${isBookmarked ? "🔖" : "🏷️"}</span>
              <span class="bookmark-text">${isBookmarked ? (activeLang === "en" ? "Saved" : "ที่บันทึกไว้") : (activeLang === "en" ? "Read Later" : "บันทึกไว้อ่าน")}</span>
            </button>
          </div>
        </article>`;
}

function renderRecommendedGrid() {
  if (!recommendedGrid) return;
  const featured = homepageFeaturedArticles();
  recommendedGrid.innerHTML = featured
    .map((article, index) => renderRecommendedCard(article, index + 1))
    .join("");
}

function renderArticles() {
  renderFilters();
  renderRecommendedGrid();
  if (!hasArticleArchive) return;

  const list = filteredArticles();
  
  if (list.length === 0) {
    if (activeFilter === "saved") {
      articleCount.textContent = activeLang === "en" ? "0 saved articles" : "0 บทความที่บันทึกไว้";
      articleGrid.innerHTML = `
        <div class="empty-state">
          <span class="empty-icon">🔖</span>
          <p class="empty-title">${activeLang === "en" ? "No saved articles yet" : "ยังไม่มีบทความที่บันทึกไว้"}</p>
          <p class="empty-desc">${activeLang === "en" ? "Articles you bookmark will appear here." : "บทความที่คุณบันทึกไว้จะแสดงที่นี่"}</p>
        </div>`;
    } else {
      articleCount.textContent = activeLang === "en" ? "0 published articles" : "0 บทความที่เผยแพร่";
      articleGrid.innerHTML = `
        <div class="empty-state">
          <p class="empty-title">${activeLang === "en" ? "No articles found" : "ไม่พบบทความ"}</p>
        </div>`;
    }
    loadMore.hidden = true;
    return;
  }

  const visible = list.slice(0, visibleLimit);
  articleCount.textContent =
    activeLang === "en" ? `${list.length} published articles` : `${list.length} บทความที่เผยแพร่`;
  articleGrid.innerHTML = visible
    .map(
      (article) => {
        const isBookmarked = bookmarkedIds.includes(article.id);
        return `
        <article class="article-card ${article.image ? "" : "is-text-only"}">
          <a href="articles/${article.id}.html" class="card-link" data-open-article="${article.id}">
            ${article.image ? `
            <div class="card-image-wrapper">
              <img src="${article.image}" alt="${article.alt}" loading="lazy" width="640" height="480">
            </div>` : ""}
            <div class="card-content">
              ${renderArticleChips(article)}
              <strong>${article.title}</strong>
              ${article.seoKeyword ? `<em class="keyword-tag">${article.seoKeyword}</em>` : ""}
              <small>${article.date || "Fengshui Balance"}${popularityLabel(article)}</small>
              <p>${excerpt(article.body, 120)}</p>
            </div>
          </a>
          <div class="card-footer">
            <a href="articles/${article.id}.html" class="read-more-link" data-open-article="${article.id}">
              <span>${activeLang === "en" ? "Read Article" : "อ่านบทความ"} &rarr;</span>
            </a>
            <button class="bookmark-btn ${isBookmarked ? "is-saved" : ""}" data-bookmark="${article.id}" aria-label="${isBookmarked ? "Remove Bookmark" : "Save for Later"}">
              <span class="bookmark-icon">${isBookmarked ? "🔖" : "🏷️"}</span>
              <span class="bookmark-text">${isBookmarked ? (activeLang === "en" ? "Saved" : "ที่บันทึกไว้") : (activeLang === "en" ? "Read Later" : "บันทึกไว้อ่าน")}</span>
            </button>
          </div>
        </article>`;
      }
    )
    .join("");
  loadMore.hidden = list.length <= visibleLimit;
}

function openArticle(id) {
  const article = articles.find((item) => item.id === id);
  if (!article) return;
  activeArticleId = id;
  const dialogImage = articleDialog.querySelector("[data-dialog-image]");
  dialogImage.hidden = !article.image;
  if (article.image) {
    dialogImage.src = article.image;
    dialogImage.alt = article.alt;
  } else {
    dialogImage.removeAttribute("src");
    dialogImage.alt = "";
  }
  articleDialog.querySelector("[data-dialog-category]").textContent = articleTags(article)
    .map((tag) => categoryLabel(tag))
    .join(" · ");
  articleDialog.querySelector("[data-dialog-title]").textContent = article.title;
  articleDialog.querySelector("[data-dialog-content]").textContent = article.body;
  const source = articleDialog.querySelector("[data-dialog-source]");
  source.href = article.url || "#";
  source.hidden = !article.url;
  articleDialog.querySelector("[data-edit-actions]").hidden = !editorMode;
  articleDialog.showModal();
}

function openAdminFor(id) {
  const article = articles.find((item) => item.id === id);
  if (!article) return;
  adminForm.elements.id.value = article.id;
  adminForm.elements.title.value = article.title;
  adminForm.elements.category.value = article.category;
  adminForm.elements.url.value = article.url || "";
  adminForm.elements.body.value = article.body;
  adminDialog.showModal();
}

function enableEditorMode() {
  editorMode = true;
  document.body.classList.add("editor-mode");
  articleDialog?.querySelector("[data-edit-actions]")?.removeAttribute("hidden");
}

langToggle?.addEventListener("click", () => {
  applyLanguage(activeLang === "en" ? "th" : "en");
  renderArticles();
});

menuToggle?.addEventListener("click", () => {
  if (menu?.classList.contains("is-open")) {
    closeMenu();
  } else {
    openMenu();
  }
});

navBackdrop?.addEventListener("click", closeMenu);

menu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", closeMenu);
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeMenu();
  }
  if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === "e") {
    enableEditorMode();
    adminDialog.showModal();
  }
});

if (articleSearch) {
  articleSearch.addEventListener("input", () => {
    ensureFullArticles().then(() => {
      visibleLimit = 6;
      renderArticles();
    });
  });
  articleSearch.addEventListener("focus", ensureFullArticles);
  articleSearch.addEventListener("mouseenter", ensureFullArticles);
}

if (articleFilters) {
  articleFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-filter]");
    if (!button) return;
    activeFilter = button.dataset.filter;
    visibleLimit = 6;
    ensureFullArticles().then(() => {
      renderArticles();
    });
  });
}

if (articleGrid) {
  articleGrid.addEventListener("click", (event) => {
    const bookmarkBtn = event.target.closest("[data-bookmark]");
    if (bookmarkBtn) {
      event.preventDefault();
      toggleBookmark(bookmarkBtn.dataset.bookmark);
      return;
    }
    const link = event.target.closest("[data-open-article]");
    if (!link) return;
    if (articleDialog) {
      event.preventDefault();
      openArticle(link.dataset.openArticle);
    }
  });
}

if (recommendedGrid) {
  recommendedGrid.addEventListener("click", (event) => {
    const bookmarkBtn = event.target.closest("[data-bookmark]");
    if (bookmarkBtn) {
      event.preventDefault();
      toggleBookmark(bookmarkBtn.dataset.bookmark);
      return;
    }
    const link = event.target.closest("[data-open-article]");
    if (!link) return;
    if (articleDialog) {
      event.preventDefault();
      openArticle(link.dataset.openArticle);
    }
  });
}

if (loadMore) {
  loadMore.addEventListener("click", () => {
    ensureFullArticles().then(() => {
      visibleLimit += 6;
      renderArticles();
    });
  });
}

document.querySelector("[data-dialog-close]")?.addEventListener("click", () => articleDialog?.close());
document.querySelector("[data-admin-close]")?.addEventListener("click", () => adminDialog?.close());
document.querySelector("[data-admin-open]")?.addEventListener("click", () => {
  enableEditorMode();
  adminDialog?.showModal();
});

document.querySelector("[data-edit-article]")?.addEventListener("click", () => openAdminFor(activeArticleId));
document.querySelector("[data-delete-article]")?.addEventListener("click", () => {
  if (!activeArticleId) return;
  articles = articles.filter((article) => article.id !== activeArticleId);
  saveArticles();
  articleDialog?.close();
  renderArticles();
});

adminForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  const id = adminForm.elements.id.value || `custom-${Date.now()}`;
  const existing = articles.find((article) => article.id === id);
  const updated = {
    id,
    title: adminForm.elements.title.value,
    category: adminForm.elements.category.value,
    image: existing?.image || "assets/images/fengshui-home-layout-consultation.jpg",
    alt: existing?.alt || "Fengshui Balance article image",
    date: existing?.date || new Date().toISOString().slice(0, 10),
    url: adminForm.elements.url.value,
    body: adminForm.elements.body.value,
  };
  articles = existing ? articles.map((article) => (article.id === id ? { ...article, ...updated } : article)) : [updated, ...articles];
  saveArticles();
  adminDialog.close();
  renderArticles();
});

document.querySelector("[data-export-articles]")?.addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(articles, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fengshui-balance-articles.json";
  link.click();
  URL.revokeObjectURL(url);
});

let fullArticlesLoaded = false;
let loadingFullArticlesPromise = null;

function ensureFullArticles() {
  if (fullArticlesLoaded || articles.length >= 500) {
    fullArticlesLoaded = true;
    return Promise.resolve();
  }
  if (loadingFullArticlesPromise) {
    return loadingFullArticlesPromise;
  }

  loadingFullArticlesPromise = new Promise((resolve) => {
    const script = document.createElement("script");
    script.src = "articles-full.js";
    script.defer = true;
    script.onload = () => {
      if (Array.isArray(window.FENGSHUI_ARTICLES_FULL)) {
        articles = window.FENGSHUI_ARTICLES_FULL;
        fullArticlesLoaded = true;
        saveArticles();
        renderArticles();
        resolve();
      } else {
        resolve();
      }
    };
    script.onerror = () => resolve();
    document.body.appendChild(script);
  });

  return loadingFullArticlesPromise;
}

applyLanguage(activeLang);
renderArticles();
setupCounters();

if (document.body.classList.contains("articles-archive-page")) {
  visibleLimit = 12;
  document.title =
    activeLang === "en"
      ? "Knowledge Library | Fengshui Balance"
      : "คลังความรู้ | Fengshui Balance";
  if (Array.isArray(window.FENGSHUI_ARTICLES_FULL) && window.FENGSHUI_ARTICLES_FULL.length) {
    articles = window.FENGSHUI_ARTICLES_FULL;
    fullArticlesLoaded = true;
    renderArticles();
  } else {
    ensureFullArticles();
  }
}
