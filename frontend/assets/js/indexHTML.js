// API endpoints
const API_ENDPOINTS = {
  dawn: "http://localhost:5002/api/dawn/latest?limit=10",
  thenews: "http://localhost:5003/api/thenews/latest?limit=10",
  tribune: "http://localhost:5001/api/tribune/latest?limit=10",
};

// DOM elements
const newsContainer = document.getElementById("newsContainer");
const refreshBtn = document.getElementById("refreshBtn");
const exploreBtn = document.getElementById("exploreBtn");
const loadingSpinner = document.getElementById("loadingSpinner");
const sectionTitle = document.getElementById("sectionTitle");



// Current state
let currentFilter = "all";
let allArticles = [];

// Function to handle article clicks
function handleArticleClick(article) {
  localStorage.setItem("currentArticle", JSON.stringify(article));
  window.open("article-detail.html", "_blank");
}

// Fetch news from all sources
async function fetchAllNews() {
  try {
    loadingSpinner.style.display = "block";
    newsContainer.innerHTML = "";

    if (allArticles.length === 0 || currentFilter === "refresh") {
      const [dawnResponse, thenewsResponse, tribuneResponse] =
        await Promise.all([
          fetch(API_ENDPOINTS.dawn).then((res) => res.json()),
          fetch(API_ENDPOINTS.thenews).then((res) => res.json()),
          fetch(API_ENDPOINTS.tribune).then((res) => res.json()),
        ]);

      // Reset all articles
      allArticles = [];

      // Process Dawn articles
      if (dawnResponse.status === "success") {
        dawnResponse.articles.forEach((article) => {
          article.source = "dawn";
          allArticles.push(article);
        });
      }

      // Process The News articles
      if (thenewsResponse.status === "success") {
        thenewsResponse.articles.forEach((article) => {
          article.source = "thenews";
          allArticles.push(article);
        });
      }

      // Process Tribune articles
      if (tribuneResponse.status === "success") {
        tribuneResponse.articles.forEach((article) => {
          article.source = "tribune";
          allArticles.push(article);
        });
      }

    }

    filterAndDisplayArticles();
  } catch (error) {
    console.error("Error fetching news:", error);
    showError("Failed to load news. Please try again later.");
  } finally {
    loadingSpinner.style.display = "none";
    if (currentFilter === "refresh") {
      currentFilter = "all";
    }
  }
}

// Filter articles based on current filter and display them
function filterAndDisplayArticles() {
  try {
    updateSectionTitle();

    let filteredArticles = allArticles;
    if (currentFilter === "dawn") {
      filteredArticles = allArticles.filter(
        (article) => article.source === "dawn"
      );
    } else if (currentFilter === "thenews") {
      filteredArticles = allArticles.filter(
        (article) => article.source === "thenews"
      );
    } else if (currentFilter === "tribune") {
      filteredArticles = allArticles.filter(
        (article) => article.source === "tribune"
      );
    }

    newsContainer.innerHTML = "";

    if (filteredArticles.length > 0) {
      filteredArticles.forEach((article) => {
        try {
          if (article.source === "dawn") {
            addNewsArticle(article, "Dawn", "source-dawn");
          } else if (article.source === "thenews") {
            addNewsArticle(article, "The News", "source-thenews");
          } else if (article.source === "tribune") {
            addNewsArticle(article, "Tribune", "source-tribune");
          }
        } catch (error) {
          console.error("Error rendering article:", error);
        }
      });
    } else {
      showError("No news articles found for this source.");
    }
  } catch (error) {
    console.error("Error filtering articles:", error);
    showError("Error displaying news. Please try again.");
  }
}

// Update section title based on current filter
function updateSectionTitle() {
  if (currentFilter === "all") {
    sectionTitle.textContent = "Top Stories";
  } else if (currentFilter === "dawn") {
    sectionTitle.textContent = "Dawn News";
  } else if (currentFilter === "thenews") {
    sectionTitle.textContent = "The News International";
  } else if (currentFilter === "tribune") {
    sectionTitle.textContent = "Tribune News";
  }
}

// Show error message
function showError(message) {
  newsContainer.innerHTML = `
                <div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 20px;">
                    <p>${message}</p>
                </div>
            `;
}

// Add a news article to the DOM
function addNewsArticle(article, source, sourceClass) {
  if (!article || !article.title) {
    console.warn("Skipping invalid article:", article);
    return;
  }

  const articleElement = document.createElement("article");
  articleElement.className = "news-article";


    let date = article.published_date || "Date not available";
    let description =
      article.summary || article.content || "No description available";
    if (description.length > 150) {
      description = description.substring(0, 150) + "...";
    }

    articleElement.innerHTML = `
                    <div class="article-content">
                        <span class="source-label ${sourceClass}">${source}</span>
                        <h3 class="news-heading">${article.title}</h3>
                        <p class="news-summary">${description}</p>
                        <div class="article-footer">
                            <span class="publish-date">${date}</span>
                            <a href="#" class="read-more">Read More <i class="fas fa-arrow-right"></i></a>
                        </div>
                    </div>
                `;

    articleElement.addEventListener("click", () => handleArticleClick(article));

    const readMoreLink = articleElement.querySelector(".read-more");
    readMoreLink.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      handleArticleClick(article);
    });

    newsContainer.appendChild(articleElement);
  }


// Event Listeners
refreshBtn.addEventListener("click", () => {
  currentFilter = "refresh";
  fetchAllNews();
});

exploreBtn.addEventListener("click", () => {
  currentFilter = "all";
  fetchAllNews();
});

homeLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "all";
  fetchAllNews();
});

dawnLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "dawn";
  fetchAllNews();
});

thenewsLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "thenews";
  fetchAllNews();
});

tribuneLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "tribune";
  fetchAllNews();
});

// Footer link events
footerHomeLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "all";
  fetchAllNews();
});

footerDawnLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "dawn";
  fetchAllNews();
});

footerThenewsLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "thenews";
  fetchAllNews();
});

footerTribuneLink.addEventListener("click", (e) => {
  e.preventDefault();
  currentFilter = "tribune";
  fetchAllNews();
});

// Load news when page loads
document.addEventListener("DOMContentLoaded", fetchAllNews);
