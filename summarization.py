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

# Cosine Similarity between two sentences
def calculate_sentence_similarity(sent1, sent2):
    words1 = nltk.word_tokenize(sent1)
    words2 = nltk.word_tokenize(sent2)
    all_words = list(set(words1 + words2))
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    for word in words1:
        vector1[all_words.index(word)] += 1
    for word in words2:
        vector2[all_words.index(word)] += 1

    return 1 - cosine_distance(vector1, vector2)

# Calculate the similarity matrix
def calculate_similarity_matrix(sentences):
    matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                matrix[i][j] = calculate_sentence_similarity(sentences[i], sentences[j])
    return matrix

# Summarization using Cosine Similarity (No PageRank)
def summarize_cosine(text, number_of_sentences=5):
    original_sentences = nltk.sent_tokenize(text)
    if len(original_sentences) == 0:
        return []

    # Preprocess sentences and compute similarity matrix
    formatted_sentences = [preprocess(sent) for sent in original_sentences]
    similarity_matrix = calculate_similarity_matrix(formatted_sentences)

    # Calculate a score for each sentence by summing its similarities with all other sentences
    sentence_scores = np.sum(similarity_matrix, axis=1)

    # Rank sentences based on their score (higher is better)
    ranked_sentences = sorted(((score, sentence) for score, sentence in zip(sentence_scores, original_sentences)), reverse=True)

    # Return the top N sentences for the summary
    summary = [ranked_sentences[i][1] for i in range(min(number_of_sentences, len(ranked_sentences)))]
    return summary


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
