# Hi Amit! If you could dump a mongodb dump class in here, 
# that would be great! Thanks :-)

import os
from pymongo import MongoClient


class MongoDB(object):
  
  def __init__(self):
    
    # Connect to the Mongo
    self.client = MongoClient('localhost', 27017)
    self.db = self.client['ouroboros_staging']
    
    self.subjects = self.db['spacewarp_subjects']
    self.classifications = self.db['spacewarp_classifications']
    
    # for subject in self.subjects.find():
    #   print subject
    
    # for classification in self.classifications.find():
    #   print classification['annotations']

if __name__ == '__main__':
  m = MongoDB()
  # print m.subjects
  # print m.classifications
