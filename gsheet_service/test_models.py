import sys
sys.path.append('path')
import unittest
import models

test_response = [3,5,6,74,3,5,7,3,2,2,5,79,6,5,4,4,3,2,5,7,8,9,7,6,5]
page_size = 3

class TestModel(unittest.TestCase):

    def test_paginate_response_pagenum(self):
        result = models.paginate_response(test_response, page_size)
        self.assertEqual(len(result), page_size )

    def test_paginate_response_array(self):
        result = models.paginate_response(test_response, page_size)
        self.assertTrue(set(test_response).issuperset(set(result[0])))

if __name__ == '__main__':
    unittest.main()