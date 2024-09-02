import unittest
from unittest.mock import patch, MagicMock
import cv2
import numpy as np
from ocr_processing import OCRProcessingApp

class TestOCRProcessingApp(unittest.TestCase):

    @patch('ocr_processing.cv2.imread')
    def test_load_image(self, mock_imread):
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        app = OCRProcessingApp(MagicMock())
        app.load_image()
        self.assertIsNotNone(app.image)
        self.assertEqual(app.image.shape, (100, 100, 3))

    @patch('ocr_processing.pytesseract.image_to_string')
    @patch('ocr_processing.cv2.dnn.readNet')
    def test_process_ocr(self, mock_readNet, mock_image_to_string):
        # Mock the OCR processing
        mock_readNet.return_value = MagicMock()
        mock_image_to_string.return_value = 'Test text'

        app = OCRProcessingApp(MagicMock())
        app.image = np.zeros((100, 100, 3), dtype=np.uint8)
        app.detected_text_boxes = [(0, 0, 50, 50)]
        app.process_ocr()
        
        self.assertEqual(app.text_result, 'Test text')

    def test_decode_predictions(self):
        # Simulate the output of EAST model for unit testing
        scores = np.random.rand(1, 1, 10, 10).astype(np.float32)
        geometry = np.random.rand(1, 5, 10, 10).astype(np.float32)

        app = OCRProcessingApp(MagicMock())
        rects, confidences = app.decode_predictions(scores, geometry)
        self.assertIsInstance(rects, list)
        self.assertIsInstance(confidences, list)

if __name__ == '__main__':
    unittest.main()
