
def arg_max(iterator, callback):
  max_value = -1
  max_index = None
  for i in iterator:
    value = callback(i)
    if value > max_value:
      max_value = value
      max_index = i
  return (max_index, max_value)

def emission_probability(word, tag, counts):
  return counts.emission_counts[(word, tag)] / counts.ngram_counts[0][(tag,)]

def bigram_probability(tag1, tag2, counts):
  if tag1 == "*":
    denominator = counts.ngram_counts[1][(tag1, tag1)]
  else:
    denominator = counts.ngram_counts[0][(tag1,)]
  
  return counts.ngram_counts[1][(tag1, tag2)] / denominator

def trgram_probability(tag1, tag2, tag3, counts):
  return counts.ngram_counts[2][(tag1, tag2, tag3)] / bigram_probability(tag1, tag2, counts)
  