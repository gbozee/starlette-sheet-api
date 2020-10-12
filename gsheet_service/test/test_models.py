from re import sub
import sys
sys.path.append('path')
# import unittest
import pytest
import gsheet_service.models as models

test_response = [3,5,6,74,3,5,7,3,2,2,5,79,6,5,4,4,3,2,5,7,8,9,7,6,5]
page_size = 3
combined_array = ["hello", "hi", "grace", "brave", "boss", "brace",'tree', "yret", "bosas", "bracde",'trdee', "yrest", "bosass", "brdddsace",'trffdfee', "yrfeddfet", "erte", 'end', 'sars', 'nigeria', 'sars', 'must', 'ends']


def test_get_page():
    result1 = models.get_page(combined_array, page_size=7, page=2)
    assert result1 == {
        'first_row': 4,
        'last_row':6,
        'total_row_count': len(combined_array),
        'page': 2,
        'page_size': 7,
        'questions':['brave','boss','brace'],
    }

    result2 = models.get_page(combined_array, page_size=4, page=1)
    assert result2 ==  {
        'first_row': 1,
        'last_row':5,
        'total_row_count': len(combined_array),
        'page': 1,
        'page_size': 4,
        'questions':["hello", "hi", "grace", "brave", "boss"],
    }
   

    result3 = models.get_page(combined_array, page_size=4, page=3)
    assert result3 ==  {
        'first_row': 12,
        'last_row':17,
        'total_row_count': len(combined_array),
        'page': 3,
        'page_size': 4,
        'questions':['yrest', 'bosass', 'brdddsace', 'trffdfee', 'yrfeddfet', 'erte'],
    }

    result4 = models.get_page(combined_array, page_size=4, page=4)
    assert result4 == {
        'first_row': 18,
        'last_row':23,
        'total_row_count': len(combined_array),
        'page': 4,
        'page_size': 4,
        'questions':['end', 'sars', 'nigeria', 'sars', 'must', 'ends'],
    }
  

def test_paginate_response():
    result = models.paginate_response(combined_array, page_size=4)
    assert result == [['hello', 'hi', 'grace', 'brave', 'boss'], ['brace', 'tree', 'yret', 'bosas', 'bracde', 'trdee'], ['yrest', 'bosass', 'brdddsace', 'trffdfee', 'yrfeddfet', 'erte'], ['end', 'sars', 'nigeria', 'sars', 'must', 'ends']]

    result_length = len(result)
    assert result_length == 4

    result2 = models.paginate_response(combined_array, page_size=9)
    result2_length = len(result2)
    assert result2_length == 9

