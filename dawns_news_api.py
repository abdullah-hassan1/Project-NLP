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

def get_dawn_news_links():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get('https://www.dawn.com', headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/news/' in href and href not in links:
                if not href.startswith('http'):
                    href = f'https://www.dawn.com{href}'
                links.append(href)
        return links
    except Exception as e:
        print(f"Error getting links: {e}")
        return []

def scrape_dawn_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('meta', property='og:title')
        if not title:
            return None

        content = []
        article_body = soup.find('div', class_='story__content')
        if article_body:
            for tag in article_body(['script', 'style', 'figure']):
                tag.decompose()
            for p in article_body.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    content.append(text)

        full_text = '\n\n'.join(content)
        summary_sentences = summarize_tfidf(full_text, number_of_sentences=5)  # Use TF-IDF summarization

        return {
            'title': title['content'],
            'url': url,
            'content': full_text,
            'summary': ' '.join(summary_sentences),
            'word_count': len(full_text.split()),
            'published_date': time.strftime('%Y-%m-%d %H:%M:%S')  # Add current time as published date
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

@app.route('/api/dawn/latest', methods=['GET'])
def get_latest_dawn_articles():
    try:
        limit = int(request.args.get('limit', 5))
        links = get_dawn_news_links()
        random.shuffle(links)
        selected_links = links[:limit]

        articles = []
        for i, url in enumerate(selected_links):
            print(f"Scraping {i+1}/{limit}: {url}")
            article = scrape_dawn_article(url)
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

# @app.route('/api/dawn/article', methods=['GET'])
# def get_dawn_article_by_url():
#     url = request.args.get('url')
#     if not url:
#         return jsonify({'status': 'error', 'message': 'URL parameter is required'}), 400

#     try:
#         article = scrape_dawn_article(url)
#         return jsonify({'status': 'success', 'article': article})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    app.run(debug=True, port=5002)