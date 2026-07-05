function normalizeSearchText(value) {
  return String(value || "").trim().toLowerCase();
}

function collectPaperCards(root) {
  return Array.from(root.querySelectorAll("[data-paper-card]"));
}

function getSelectedTag(root) {
  var active = root.querySelector("[data-tag-filter].is-active");
  return active ? active.getAttribute("data-tag-filter") || "" : "";
}

function paperMatchesQuery(card, query) {
  if (!query) {
    return true;
  }

  var title = normalizeSearchText(card.getAttribute("data-search-title"));
  var summary = normalizeSearchText(card.getAttribute("data-search-summary"));
  return title.indexOf(query) !== -1 || summary.indexOf(query) !== -1;
}

function paperMatchesTag(card, tag) {
  if (!tag) {
    return true;
  }

  var tags = [];
  try {
    tags = JSON.parse(card.getAttribute("data-tags") || "[]");
  } catch (_error) {
    tags = [];
  }

  return tags.indexOf(tag) !== -1;
}

function applyPaperFilters(root) {
  var queryInput = root.querySelector("#paper-search");
  var query = normalizeSearchText(queryInput ? queryInput.value : "");
  var tag = getSelectedTag(root);
  var cards = collectPaperCards(root);
  var visibleCount = 0;

  cards.forEach(function(card) {
    var visible = paperMatchesQuery(card, query) && paperMatchesTag(card, tag);
    card.hidden = !visible;
    card.classList.toggle("is-hidden", !visible);
    if (visible) {
      visibleCount += 1;
    }
  });

  var empty = root.querySelector("[data-filter-empty]");
  if (empty) {
    var hasVisibleCards = visibleCount !== 0;
    empty.hidden = hasVisibleCards;
    empty.classList.toggle("is-hidden", hasVisibleCards);
  }
}

function initializePaperFilters(root) {
  var queryInput = root.querySelector("#paper-search");
  var tagButtons = Array.from(root.querySelectorAll("[data-tag-filter]"));

  if (queryInput) {
    queryInput.addEventListener("input", function() {
      applyPaperFilters(root);
    });
  }

  tagButtons.forEach(function(button) {
    button.addEventListener("click", function() {
      tagButtons.forEach(function(candidate) {
        candidate.classList.remove("is-active");
      });
      button.classList.add("is-active");
      applyPaperFilters(root);
    });
  });

  applyPaperFilters(root);
}

document.addEventListener("DOMContentLoaded", function() {
  initializePaperFilters(document);
});
