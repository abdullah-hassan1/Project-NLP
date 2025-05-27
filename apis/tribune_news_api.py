from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time
import random
from algorithm.summarization import summarize_tfidf


# Flask app setup
app = Flask(__name__)
CORS(app)

# ---------------------- SCRAPING FUNCTIONS ----------------------

def get_tribune_latest_links():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        response = requests.get('https://tribune.com.pk/', headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        story_links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/story/' in href and not href.startswith('javascript'):
                if not href.startswith('http'):
                    href = f'https://tribune.com.pk{href}'
                story_links.add(href)
        
        return list(story_links)
    
    except Exception as e:
        print(f"Error getting Tribune links: {e}")
        return []

def scrape_tribune_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize with default values
        article_data = {
            'title': 'No title found',
            'url': url,
            'content': 'Content not available',
            'word_count': 0,
            'published_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Try both formats of Tribune articles
        story_box = soup.find('div', class_='story-box-section')
        if story_box:
            # Format 1 processing
            title = story_box.find('h1')
            if title:
                article_data['title'] = title.get_text(strip=True)
            
            story_text = story_box.find('span', class_='story-text')
            if story_text:
                for element in story_text(['script', 'style', 'figure', 'div', 'aside', 'iframe']):
                    element.decompose()
                
                paragraphs = []
                for p in story_text.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        paragraphs.append(text)
                
                if paragraphs:
                    article_data['content'] = '\n\n'.join(paragraphs)
                    article_data['word_count'] = len(' '.join(paragraphs).split())
        else:
            # Format 2 processing
            title = (soup.find('h1', class_='story-title') or 
                    soup.find('h1', class_='title') or 
                    soup.find('h1'))
            if title:
                article_data['title'] = title.get_text(strip=True)
            
            article_body = (soup.find('div', class_='story-content') or 
                          soup.find('article') or 
                          soup.find('div', class_='content-area') or
                          soup.find('span', class_='story-text'))
            
            if article_body:
                for element in article_body(['script', 'style', 'figure', 'div.social-share', 
                                          'div.related-posts', 'div.tags', 'div.author',
                                          'header', 'footer', 'aside', 'iframe']):
                    element.decompose()
                
                paragraphs = []
                for p in article_body.find_all('p'):
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        paragraphs.append(text)
                
                if paragraphs:
                    article_data['content'] = '\n\n'.join(paragraphs)
                    article_data['word_count'] = len(' '.join(paragraphs).split())

        # Generate summary using TF-IDF
        if article_data['content'] != 'Content not available':
            summary_sentences = summarize_tfidf(article_data['content'], number_of_sentences=5)
            article_data['summary'] = ' '.join(summary_sentences)
        else:
            article_data['summary'] = 'No summary available'

        return article_data

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

@app.route('/api/tribune/latest', methods=['GET'])
def get_latest_tribune_articles():
    try:
        limit = int(request.args.get('limit', 5))
        links = get_tribune_latest_links()
        random.shuffle(links)
        selected_links = links[:limit]

        articles = []
        for i, url in enumerate(selected_links):
            print(f"Scraping {i+1}/{limit}: {url}")
            article = scrape_tribune_article(url)
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


# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    app.run(debug=True, port=5001)