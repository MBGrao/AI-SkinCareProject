import unittest
from unittest.mock import patch, MagicMock
from safety_ratings import get_safety_rating

class TestSafetyRatings(unittest.TestCase):

    @patch('safety_ratings.get_safety_and_toxicity_info')
    def test_get_safety_rating(self, mock_get_safety_and_toxicity_info):
        mock_get_safety_and_toxicity_info.return_value = {'safety': 'Safe'}
        rating = get_safety_rating('IngredientName')
        self.assertEqual(rating, 'Safe')

if __name__ == '__main__':
    unittest.main()
