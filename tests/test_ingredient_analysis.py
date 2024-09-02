import unittest
from unittest.mock import patch, MagicMock
from ingredient_analysis import get_ingredient_info, analyze_ingredient_list

class TestIngredientAnalysis(unittest.TestCase):

    @patch('ingredient_analysis.get_ingredient_info')
    def test_get_ingredient_info(self, mock_get_ingredient_info):
        mock_get_ingredient_info.return_value = 'Some info'
        info = get_ingredient_info('IngredientName')
        self.assertEqual(info, 'Some info')

    @patch('ingredient_analysis.get_ingredient_info')
    def test_analyze_ingredient_list(self, mock_get_ingredient_info):
        mock_get_ingredient_info.side_effect = lambda x: f'Info for {x}'
        result = analyze_ingredient_list(['Ingredient1', 'Ingredient2'])
        expected_result = ['Info for Ingredient1', 'Info for Ingredient2']
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
