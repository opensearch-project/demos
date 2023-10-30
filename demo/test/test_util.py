import sys, pytest, random
from math import ceil
sys.path.append('./demo/')

from docbot.util import opensearch_connection_builder, shorten_json_file_same_index

def test_opensearch_connection():
  connection = opensearch_connection_builder()
  health = connection.cat.health()
  assert isinstance(health, str)

def test_shorten_json_file_same_index():

  calculate_len_result = lambda sentence_len, num_words, overlap: (ceil((sentence_len - num_words)/int(num_words - num_words*overlap)) + 1) if num_words <= sentence_len else 1

  #test right inputs
  for i in range(10000):
    #overlaps by one word
    random_len = random.randint(100, 10000)
    random_num_words = random.randint(99, random_len)
    random_overlap = random.randint(1, 99) / 100
    sentence = 'a ' * random_len

    result = shorten_json_file_same_index({'content': sentence}, random_num_words, random_overlap)

    assert(len(result) == calculate_len_result(random_len, random_num_words, random_overlap))

  #test wrong json type
  with pytest.raises(ValueError):
    shorten_json_file_same_index([])

  #test wrong json file contents
  with pytest.raises(ValueError):
    shorten_json_file_same_index({'a':'b'})

  #test wrong parameters
  with pytest.raises(ValueError):
    shorten_json_file_same_index({'content':' '}, num_words=-100, overlap=-5)

  #test extremely long sentences
  sentence = 'abba ' * 10000
  result = shorten_json_file_same_index({'content': sentence}, num_words=100, overlap=0.1)
  assert(len(result) == calculate_len_result(10000, 100, 0.1))

  #test same num_words
  sentence = 'abba ' * 100
  result = shorten_json_file_same_index({'content': sentence}, num_words=100)
  assert(len(result)==calculate_len_result(100, 100, 0.3))


  #test one long word
  sentence = 'abba' * 100000
  result = shorten_json_file_same_index({'content': sentence})
  assert(len(result)==calculate_len_result(1, 100, 0.3))
