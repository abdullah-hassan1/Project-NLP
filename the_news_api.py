from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time
import random
from summarization import summarize_tfidf

# Flask app setup
app = Flask(__name__)
CORS(app)

# ---------------------- SCRAPING FUNCTIONS ----------------------

def get_thenews_latest_links():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get('https://www.thenews.com.pk/', headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        latest_links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/latest/' in href and not href.startswith('javascript'):
                if not href.startswith('http'):
                    href = f'https://www.thenews.com.pk{href}'
                latest_links.add(href)
        
        return list(latest_links)
    
    except Exception as e:
        print(f"Error getting The News links: {e}")
        return []

def scrape_thenews_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1', class_='detail-title') or soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'
        
        content = []
        article_container = (soup.find('div', class_='detail-story') or 
                           soup.find('article') or 
                           soup.find('div', class_='story__content') or
                           soup.find('div', class_='story-detail'))

        if article_container:
            for element in article_container(['script', 'style', 'figure', 'div.social-share', 
                                          'div.related-news', 'div.tags', 'div.author',
                                          'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            for p in article_container.find_all('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    if not any(text.startswith(prefix) for prefix in 
                             ['Also Read', 'Also read', 'READ MORE', 'Read more', 'Published', 'Updated']):
                        content.append(text)

        full_text = '\n\n'.join(content)
        summary_sentences = summarize_tfidf(full_text, number_of_sentences=5)  # Use TF-IDF summarization

        return {
            'title': title,
            'url': url,
            'content': full_text,
            'summary': ' '.join(summary_sentences),
            'word_count': len(full_text.split()),
            'published_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            'title': 'Failed to scrape',
            'url': url,
            'content': 'Error occurred while scraping this article',
            'summary': '',
            'word_count': 0,
            'published_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }

# ---------------------- API ENDPOINTS ----------------------

@app.route('/api/thenews/latest', methods=['GET'])
def get_latest_thenews_articles():
    try:
        limit = int(request.args.get('limit', 5))
        links = get_thenews_latest_links()
        random.shuffle(links)
        selected_links = links[:limit]

        articles = []
        for i, url in enumerate(selected_links):
            print(f"Scraping {i+1}/{limit}: {url}")
            article = scrape_thenews_article(url)
            if article:
                articles.append(article)
            time.sleep(1)

        return jsonify({
            'status': 'success',
            'count': len(articles),
            'articles': articles
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/api/thenews/article', methods=['GET'])
# def get_thenews_article_by_url():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'status': 'error', 'message': 'URL parameter is required'}), 400

#     try:
#         article = scrape_thenews_article(url)
#         return jsonify({'status': 'success', 'article': article})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    app.run(debug=True, port=5003)