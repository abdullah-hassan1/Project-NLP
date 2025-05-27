import nltk
import string
import numpy as np
from nltk.cluster.util import cosine_distance
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')

# Preprocessing function
def preprocess(text):
    formatted_text = text.lower()
    tokens = [word for word in nltk.word_tokenize(formatted_text)]
    tokens = [word for word in tokens if word not in stopwords and word not in string.punctuation]
    return ' '.join(tokens)


# Calculate sentence importance using TF-IDF
def calculate_sentence_tfidf(sentences):
    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # Get the importance score for each sentence (sum of TF-IDF scores for words in each sentence)
    sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    return sentence_scores

# Summarization using TF-IDF (No PageRank)
def summarize_tfidf(text, number_of_sentences=5):
    original_sentences = nltk.sent_tokenize(text)
    if len(original_sentences) == 0:
        return []

    # Calculate TF-IDF scores for each sentence
    sentence_scores = calculate_sentence_tfidf(original_sentences)

    # Rank sentences based on their TF-IDF score (higher is better)
    ranked_sentences = sorted(((score, sentence) for score, sentence in zip(sentence_scores, original_sentences)), reverse=True)

    # Return the top N sentences for the summary
    summary = [ranked_sentences[i][1] for i in range(min(number_of_sentences, len(ranked_sentences)))]
    return summary

