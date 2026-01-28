'''
This module Loads, cleans and transforms the sequential data 
into a usable format for the PrefixSpan algorithm.
'''


from typing import List, Dict, Set, Tuple
from collections import defaultdict


Item = str
Itemset = Set[Item]  
Sequence = List[Itemset]
Database = List[Sequence]
Position = Tuple[int, int]


def normalise_itemset(itemset: Itemset) -> Itemset:
    """
    Removes duplicates
    """
    return set(sorted(itemset)) 

def normalise_sequence(sequence: Sequence) -> Sequence:
    """
    Normalises each itemset
    """
    normalised = []
    for itemset in sequence:
        if itemset:  #skips empty itemsets
            norm_itemset = normalise_itemset(itemset)
            if norm_itemset:  #only keeps non-empty sequences
                    normalised.append(norm_itemset)
    return normalised

def normalise_database(database: Database) -> Database:
    normalised = []
    for sequence in database:
        norm_seq = normalise_sequence(sequence)
        if norm_seq:  
            normalised.append(norm_seq)
    return normalised


def print_database(database: Database):
    """
    Prints databases
    """
    for i, sequence in enumerate(database):
        itemset_strs = []
        for itemset in sequence:
            sorted_items = sorted(itemset)
            if len(sorted_items) == 1:
                itemset_strs.append(sorted_items[0])
            else:
                itemset_strs.append(f"({','.join(sorted_items)})")
        print(f"Seq{i}: {' -> '.join(itemset_strs)}")



def print_database_raw(database: Database):

    for i, sequence in enumerate(database):
        print(f"Seq{i}: {[set(sorted(itemset)) for itemset in sequence]}")


def load_spmf_database(file_path: str) -> Database:
  '''
  Loads SPMF data and converts to 2D list of sets format 
  '''
  database = []
  with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            sequence = []
            itemset = set() 
            
            for item in line.split():
                if item == '-1':
                    if itemset: 
                        sequence.append(set(sorted(itemset))) 
                        itemset = set()
                elif item == '-2':
                    if itemset:  
                        sequence.append(set(sorted(itemset)))
                    break
                else:
                    itemset.add(item)  
            
            if sequence:  
                database.append(sequence)
    
  return database

def convert_database_to_sets(database: Database) -> Database:
    set_database = []
    for sequence in database:
        set_sequence = []
        for itemset in sequence:
            set_sequence.append(set(itemset))
        set_database.append(set_sequence)
    return set_database

def convert_database_to_lists(database: Database) -> List[List[List[str]]]:
    list_database = []
    for sequence in database:
        list_sequence = []
        for itemset in sequence:
            list_sequence.append(sorted(itemset)) 
        list_database.append(list_sequence)
    return list_database

