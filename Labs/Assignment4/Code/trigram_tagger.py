
from collections import defaultdict
from count_freqs import *
from utils import *
import math
import sys
import os


if __name__ == "__main__":
  counts_file = open(os.path.join(os.path.dirname(__file__), "ner.counts"))
  sentences_file = open(os.path.join(os.path.dirname(__file__), "ner_dev.dat"))
  
  hmm = Hmm()
  hmm.read_counts(counts_file)
  
  word_counts = defaultdict(int)
  
  for word, tag in hmm.emission_counts:
    word_counts[word] += hmm.emission_counts[(word, tag)]
  
  for word in word_counts:
    count = word_counts[word]
    if count < 5:
      for tag in hmm.all_states:
        if (word, tag) in hmm.emission_counts:
          hmm.emission_counts[("_RARE_", tag)] += count
  
  
  
  initial_probability = defaultdict(float)
  initial_tag = None
  
  for tag in hmm.all_states:
    initial_probability[tag] = trigram_probability("*", "*", tag, hmm)
  
  initial_tag = arg_max(hmm.all_states, lambda tag: trigram_probability("*", "*", tag, hmm))[0]
  
  
  
  sentences = sentence_iterator(simple_conll_corpus_iterator(sentences_file))
  
  for sentence in sentences:
    original_words = []
    words = []
    for _, word in sentence:
      if not(word in word_counts) or (word_counts[word] < 5):
        words.append("_RARE_")
      else:
        words.append(word)
      original_words.append(word)
    
    t1 = defaultdict(float)
    t2 = defaultdict(str)
    
    x_probs = defaultdict(float)
    x = defaultdict(str)
    
    for tag in hmm.all_states:
      t1[(tag, 0)] = initial_probability[tag] * emission_probability(words[0], tag, hmm)
      t2[(tag, 0)] = initial_tag
    
    i = 1
    for j in hmm.all_states:
      t2[(j, i)], t1[(j, i)] = arg_max(hmm.all_states, lambda k: t1[(k, i - 1)] * bigram_probability(k , j, hmm) * emission_probability(words[i], j, hmm))
    
    
    for i in range(2, len(words)):
      for j in hmm.all_states:
        max_probability = -1
        max_tag = None
        for k in hmm.all_states:
          for l in hmm.all_states:
            probability = t1[(l, i - 2)] * t1[(k, i - 1)] * trigram_probability(l, k, j, hmm) * emission_probability(words[i], j, hmm)
            if probability > max_probability:
              max_probability = probability
              max_tag = k
        
        t1[(j, i)] = max_probability
        t2[(j, i)] = max_tag
    
    x[len(words) - 1], x_probs[len(words) - 1] = arg_max(hmm.all_states, lambda k: t1[(k, len(words) - 1)])
    
    max_probability = -1
    max_tag = None
    for j in hmm.all_states:
      for k in hmm.all_states:
        prob = t1[(k, len(words) - 1)] * t1[(j, len(words) - 2)]
        if prob > max_probability:
          max_probability = prob
          max_tag = j
          
    x[len(words) - 2] = max_tag
    x_probs[len(words) - 2] = max_probability
    
    for i in reversed(range(2, len(words))):
      max_probability = -1
      max_tag = None
      for j in hmm.all_states:
        for k in hmm.all_states:
          prob = t1[(k, i - 1)] * t1[(j, i - 2)]
          if prob > max_probability:
            max_probability = prob
            max_tag = j
      
      x[i - 2] = max_tag
      x_probs[i - 2] = max_probability
    
    for i in range(0, len(words)):
      print original_words[i] + " " + x[i] + " " #+ str(math.log(x_probs[i])/math.log(2))
    print ""
    
    sys.exit()
  
  
