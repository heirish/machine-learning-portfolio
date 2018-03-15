
# coding: utf-8

# In[ ]:
import random

class RandomChoose(object):
 
    def __init__(self, ratio=0.200, seed=123):
        self.ratio = ratio * 1000 #precision 3 after point
        self.seed = seed
        random.seed(seed)
        
 
    def choose(self):
       if random.randint(1,1000) < self.ratio:
           return True
       else:
           return False