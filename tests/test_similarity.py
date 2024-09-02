import unittest
from unittest.mock import patch, MagicMock
from nlp_similarity import get_similar_products

class TestSimilarityComparison(unittest.TestCase):

    @patch('nlp_similarity.embed_sentences')
    @patch('nlp_similarity.compute_similarity')
    def test_get_similar_products(self, mock_compute_similarity, mock_embed_sentences):
        mock_embed_sentences.return_value = [1.0, 2.0]
        mock_compute_similarity.return_value = 0.8
        result = get_similar_products(['Product1', 'Product2'])
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(item, tuple) and len(item) == 2 for item in result))

if __name__ == '__main__':
    unittest.main()
