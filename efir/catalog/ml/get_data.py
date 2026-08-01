from catalog.models import Product
from orders.models import Order, OrderItem
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from catalog.stop_words import cz_stop_words
import numpy as np


def get_similarity_matrix():

    products = list(Product.objects.filter(active=True))
    documents = []

    product_ids = [p.id for p in products]

    for p in products:
        p.category.name if p.category.name else ""
        p.name if p.name else ""
        p.long_description if p.long_description else ""
        doc = f"{p.category.name} {p.name} {p.long_description}".strip()
        documents.append(doc)

    vectorizer = TfidfVectorizer(stop_words=cz_stop_words)
    matrix = vectorizer.fit_transform(documents)

    
    similarity_matrix = cosine_similarity(matrix, matrix)
        
    return product_ids, similarity_matrix


def get_recommendations(target_product):
    product_ids, similarity_matrix = get_similarity_matrix()
    recommendations = []

    target_idx = product_ids.index(target_product)
    scores = similarity_matrix[target_idx]

    sorted_score_indices = np.argsort(scores)[::-1]

    recommended_product_ids = []

    for p in sorted_score_indices:
        p_id = product_ids[p]
        
        if p_id != target_product:
            recommended_product_ids.append(p_id)
        if len(recommended_product_ids) == 5:
            break

    print('scores per IDX',scores, sorted_score_indices, recommended_product_ids)

    recommendations = list(Product.objects.filter(id__in=recommended_product_ids))

    print('recommendations', recommendations)
    return recommendations

