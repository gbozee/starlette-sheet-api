from gsheet_service.models import get_cell_data, get_cells
import pytest 
import re
sample_data = [
 '\nRead the following passages carefully and then, choose option to each of the questions that follow.',
 '"D121"',
 '"D121"',
 '"D121"',
 '"D113"'
]

# def get_cells(sample_data):
#     cleaned_data = ",".join(list(set(sample_data)))
#     pattern = re.compile(r'[A-Z]\d+"')
#     return pattern.findall(cleaned_data)

def mock_call():
    return [[['\nRead the following passages carefully and then, choose option to each of the questions that follow.']],
 [['The drums and the dancing began again and reached fever heat. Darkness was around the corner, and the burial was near. Guns fired the last salute and the canons rent the sky. And then from the centre of the fury came a cry of agony and shouts of horror. It was as if a spell has been cast. All was silent.\n In the centre of the crowd, a boy lay in a pool of blood. It was the dead man’s sixteen year old son, who with his brothers and half brothers had been dancing the traditional farewell to his father. Okonkwo’s gun had exploded and a piece of iron had pierced the boy’s groin and the violence and reactions that followed was without parallel in the tradition of Umuofia. Violent deaths were frequent but nothing like this had ever happened.\n  The only course opened to Okonkwo was to flee from the clan. It was a crime against the earth goddess to kill a clansman, and a man who committed it must flee from the land. The crime was of two kinds, male and female. Okonkwo had committed the female because he did not do it intentionally. He could return to the town after seven years.\n  The night he collected his most valuable belongings into head loads. His wives wept bitterly and their children wept with them without knowing why Oberika and half a dozen other friends came to help and console him. They each made nine or ten trips carrying Okonkwo’s yams to store motherland. It was a little village called Mbanta, just beyond the borders of Mbaino.\n  As soon as the day broke, a large crowd of men from Ezeudu’s quarters stormed Okonkwo’s compound, dressed in garbs of war. It was the justice of the earth goddess and they were merely his messengers.']]]

expected_dict = {
            'D113': '\nRead the following passages carefully and then, choose option to each of the questions that follow.',
            "D121": 'The drums and the dancing began again and reached fever heat. Darkness was around the corner, and the burial was near. Guns fired the last salute and the canons rent the sky. And then from the centre of the fury came a cry of agony and shouts of horror. It was as if a spell has been cast. All was silent.\n In the centre of the crowd, a boy lay in a pool of blood. It was the dead man’s sixteen year old son, who with his brothers and half brothers had been dancing the traditional farewell to his father. Okonkwo’s gun had exploded and a piece of iron had pierced the boy’s groin and the violence and reactions that followed was without parallel in the tradition of Umuofia. Violent deaths were frequent but nothing like this had ever happened.\n  The only course opened to Okonkwo was to flee from the clan. It was a crime against the earth goddess to kill a clansman, and a man who committed it must flee from the land. The crime was of two kinds, male and female. Okonkwo had committed the female because he did not do it intentionally. He could return to the town after seven years.\n  The night he collected his most valuable belongings into head loads. His wives wept bitterly and their children wept with them without knowing why Oberika and half a dozen other friends came to help and console him. They each made nine or ten trips carrying Okonkwo’s yams to store motherland. It was a little village called Mbanta, just beyond the borders of Mbaino.\n  As soon as the day broke, a large crowd of men from Ezeudu’s quarters stormed Okonkwo’s compound, dressed in garbs of war. It was the justice of the earth goddess and they were merely his messengers.'
        }

def test_grouping_similar_cells():
    mocked_data = mock_call()
    unique_cells = get_cells(sample_data)
    unique_cells.sort()
    expected = ['D121', 'D113']
    expected.sort()
    assert unique_cells == expected
    assert get_cell_data(unique_cells, mocked_data) == expected_dict

    # API CALL PATTTERN
    # {
    #     "columns": ["Pretext","comprehension"],
    #     "type": "text"
    # }

    #"result_pairs":["Pretext","Comprehension"]