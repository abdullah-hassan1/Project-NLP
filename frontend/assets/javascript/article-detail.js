document.addEventListener("DOMContentLoaded", function () {
  const articleDetail = document.getElementById("articleDetail");

  // Get the article data from localStorage
  const articleData = JSON.parse(localStorage.getItem("currentArticle"));

  if (!articleData) {
    articleDetail.innerHTML = `
                    <div class="error-message">
                        <h2>Article Not Found</h2>
                        <p>We couldn't find the article you're looking for.</p>
                        <a href="index.html" class="original-link-top">
                            <i class="fas fa-arrow-left"></i>
                            Back to News
                        </a>
                    </div>
                `;
    return;
  }

  // Determine source class
  let sourceClass = "";
  let sourceName = "";

  if (articleData.source === "dawn") {
    sourceClass = "source-dawn";
    sourceName = "Dawn News";
  } else if (articleData.source === "thenews") {
    sourceClass = "source-thenews";
    sourceName = "The News";
  } else if (articleData.source === "tribune") {
    sourceClass = "source-tribune";
    sourceName = "Tribune News";
  }

  // Format date
  let date = "";
  if (articleData.published_date) {
    date = new Date(articleData.published_date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } else {
    date = "Date not available";
  }

  // Create the article detail HTML with summary section
  articleDetail.innerHTML = `
                <div class="article-header">
                    <span class="source-label ${sourceClass}">${sourceName}</span>
                    <h1 class="article-title">${
                      articleData.title || "No title available"
                    }</h1>
                    <div class="article-meta">
                        <span>${date}</span>
                        <span>${
                          articleData.word_count
                            ? articleData.word_count + " words"
                            : ""
                        }</span>
                    </div>
                </div>
                
                ${
                  articleData.url
                    ? `
                <a href="${articleData.url}" target="_blank" rel="noopener noreferrer" class="original-link-top">
                    <i class="fas fa-external-link-alt"></i>
                    Read Original Article
                </a>
                `
                    : ""
                }
                
                ${
                  articleData.image_url
                    ? `<img src="${articleData.image_url}" alt="${articleData.title}" class="article-image">`
                    : ""
                }
                
                <div class="summary-section">
                    <h3 class="summary-title">
                        <i class="fas fa-file-contract"></i>
                        Summary
                    </h3>
                    <div class="summary-content">
                        ${
                          articleData.summary ||
                          "No summary available for this article."
                        }
                    </div>
                </div>
                
                <div class="article-content">
                    <h3>Full Article</h3>
                    ${
                      articleData.content
                        ? `<p>${articleData.content.replace(
                            /\n/g,
                            "</p><p>"
                          )}</p>`
                        : articleData.description
                        ? `<p>${articleData.description}</p>`
                        : "<p>No content available for this article.</p>"
                    }
                </div>
                
                ${
                  articleData.url
                    ? `
                <a href="${articleData.url}" target="_blank" rel="noopener noreferrer" class="original-link-bottom">
                    <i class="fas fa-external-link-alt"></i>
                    Continue Reading on ${sourceName}
                </a>
                `
                    : ""
                }
            `;
});
