const root = document.documentElement;
const langToggle = document.querySelector("[data-lang-toggle]");
const langLabel = document.querySelector("[data-lang-label]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");
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
let visibleLimit = 9;
let activeArticleId = null;
let editorMode = new URLSearchParams(location.search).has("edit") || location.hash === "#edit";
const articleVersion = "top10-recommended-2026-06-05";
const savedVersion = localStorage.getItem("fengshui-balance-articles-version");
const savedArticles = JSON.parse(localStorage.getItem("fengshui-balance-articles") || "null");
const sourceArticles = window.FENGSHUI_ARTICLES || [];
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
  langLabel.textContent = lang === "en" ? "TH" : "EN";
  document.title =
    lang === "en"
      ? "Fengshui Balance | Ajarn Suppachai Vivattanaprasert"
      : "Fengshui Balance | อาจารย์ สุภชัย วิวัฒนะประเสริฐ";
  localStorage.setItem("fengshui-balance-lang", lang);
}

function closeMenu() {
  menu.classList.remove("is-open");
  menuToggle.setAttribute("aria-expanded", "false");
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

function excerpt(text, length = 190) {
  const compact = text.replace(/\s+/g, " ").trim();
  return compact.length > length ? `${compact.slice(0, length).trim()}...` : compact;
}

function categoryLabel(category) {
  const labels = {
    all: activeLang === "en" ? "All" : "ทั้งหมด",
    home: activeLang === "en" ? "Home" : "บ้าน",
    office: activeLang === "en" ? "Office" : "ออฟฟิศ",
    spirit: activeLang === "en" ? "Spirit House" : "ศาลและตี่จู้",
    lineage: activeLang === "en" ? "Lineage" : "สายวิชา",
    yearly: activeLang === "en" ? "Yearly" : "รายปี",
    business: activeLang === "en" ? "Business" : "ธุรกิจ",
    shop: activeLang === "en" ? "Shop" : "ร้านค้า",
    factory: activeLang === "en" ? "Factory" : "โรงงาน",
    timing: activeLang === "en" ? "Auspicious Timing" : "ฤกษ์ยาม",
    astrology: activeLang === "en" ? "Destiny" : "ดวงจีน",
    general: activeLang === "en" ? "Fengshui Notes" : "บันทึกฮวงจุ้ย",
    energy: activeLang === "en" ? "Energy" : "พลังงาน",
    interactive: activeLang === "en" ? "Community" : "ชุมชน",
  };
  return labels[category] || category;
}

function saveArticles() {
  localStorage.setItem("fengshui-balance-articles", JSON.stringify(articles));
  localStorage.setItem("fengshui-balance-articles-version", articleVersion);
}

function filteredArticles() {
  const q = articleSearch.value.trim().toLowerCase();
  return articles.filter((article) => !article.recommended).filter((article) => {
    const matchesFilter = activeFilter === "all" || article.category === activeFilter;
    const haystack = `${article.title} ${article.body} ${article.category}`.toLowerCase();
    return matchesFilter && (!q || haystack.includes(q));
  });
}

function recommendedArticles() {
  return articles
    .filter((article) => article.recommended)
    .sort((a, b) => (a.recommendedRank || 999) - (b.recommendedRank || 999));
}

function renderFilters() {
  const categories = ["all", ...new Set(articles.map((article) => article.category))];
  articleFilters.innerHTML = categories
    .map(
      (category) =>
        `<button type="button" class="${category === activeFilter ? "is-active" : ""}" data-filter="${category}">${categoryLabel(category)}</button>`
    )
    .join("");
}

function renderArticles() {
  renderFilters();
  recommendedGrid.innerHTML = recommendedArticles()
    .map(
      (article) => `
        <article class="recommended-card">
          <a href="articles/${article.id}.html" data-open-article="${article.id}">
            <span class="recommend-rank">No. ${article.recommendedRank}</span>
            <img src="${article.image}" alt="${article.alt}" loading="lazy" width="960" height="540">
            <span class="article-chip">${categoryLabel(article.category)}</span>
            <strong>${article.title}</strong>
            ${article.seoKeyword ? `<em class="keyword-tag">${article.seoKeyword}</em>` : ""}
            <small>${article.date || "Fengshui Balance"}${article.metrics?.wei ? ` · WEI ${Math.round(article.metrics.wei).toLocaleString()}` : ""}</small>
            <p>${excerpt(article.body, 150)}</p>
          </a>
        </article>`
    )
    .join("");

  const list = filteredArticles();
  const visible = list.slice(0, visibleLimit);
  articleCount.textContent =
    activeLang === "en" ? `${list.length} published articles` : `${list.length} บทความที่เผยแพร่`;
  articleGrid.innerHTML = visible
    .map(
      (article) => `
        <article class="article-card ${article.image ? "" : "is-text-only"}">
          <a href="articles/${article.id}.html" data-open-article="${article.id}">
            ${article.image ? `<img src="${article.image}" alt="${article.alt}" loading="lazy" width="640" height="480">` : ""}
            <span class="article-chip">${categoryLabel(article.category)}</span>
            <strong>${article.title}</strong>
            ${article.seoKeyword ? `<em class="keyword-tag">${article.seoKeyword}</em>` : ""}
            <small>${article.date || "Fengshui Balance"}${article.metrics?.wei ? ` · WEI ${Math.round(article.metrics.wei).toLocaleString()}` : ""}</small>
            <p>${excerpt(article.body)}</p>
          </a>
        </article>`
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
  articleDialog.querySelector("[data-dialog-category]").textContent = categoryLabel(article.category);
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

langToggle.addEventListener("click", () => {
  applyLanguage(activeLang === "en" ? "th" : "en");
  renderArticles();
});

menuToggle.addEventListener("click", () => {
  const isOpen = menu.classList.toggle("is-open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});

menu.querySelectorAll("a").forEach((link) => {
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

articleSearch.addEventListener("input", () => {
  visibleLimit = 9;
  renderArticles();
});

articleFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-filter]");
  if (!button) return;
  activeFilter = button.dataset.filter;
  visibleLimit = 9;
  renderArticles();
});

articleGrid.addEventListener("click", (event) => {
  const link = event.target.closest("[data-open-article]");
  if (!link) return;
  event.preventDefault();
  openArticle(link.dataset.openArticle);
});

recommendedGrid.addEventListener("click", (event) => {
  const link = event.target.closest("[data-open-article]");
  if (!link) return;
  event.preventDefault();
  openArticle(link.dataset.openArticle);
});

loadMore.addEventListener("click", () => {
  visibleLimit += 9;
  renderArticles();
});

document.querySelector("[data-dialog-close]").addEventListener("click", () => articleDialog.close());
document.querySelector("[data-admin-close]").addEventListener("click", () => adminDialog.close());
document.querySelector("[data-admin-open]").addEventListener("click", () => {
  enableEditorMode();
  adminDialog.showModal();
});

document.querySelector("[data-edit-article]").addEventListener("click", () => openAdminFor(activeArticleId));
document.querySelector("[data-delete-article]").addEventListener("click", () => {
  if (!activeArticleId) return;
  articles = articles.filter((article) => article.id !== activeArticleId);
  saveArticles();
  articleDialog.close();
  renderArticles();
});

adminForm.addEventListener("submit", (event) => {
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

document.querySelector("[data-export-articles]").addEventListener("click", () => {
  const blob = new Blob([JSON.stringify(articles, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fengshui-balance-articles.json";
  link.click();
  URL.revokeObjectURL(url);
});

applyLanguage(activeLang);
renderArticles();
setupCounters();
