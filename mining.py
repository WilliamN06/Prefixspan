from collections import defaultdict
from typing import List, Tuple, Dict, Set

Item = str
Itemset = Set[Item]  
Sequence = List[Item]
Database = List[Sequence]
Position = Tuple[int, int]
Matches = List[Tuple[int, int]]


'''
PrefixSpan class where logic is contained 
'''


class PrefixSpan:
    def __init__(self, minsup: int, type: str = "count"):
        self.type = type.lower()
        self.minsup = minsup


    def run(self, db: Database) -> List[Tuple[List[Itemset], int]]:
        self.db = db
        self.patterns = []
        self.minsup = self.minsup
        if self.type == "percent":
            if self.minsup > 100 or self.minsup < 0:
                raise ValueError(f"Percent support must be a number between 0 and 100, value passed {self.minsup}")
            else:
                self.minsup = (self.minsup/100)*len(self.db)
        initial_matches = [(i, -1) for i in range(len(self.db))]
        self._prefixspan(prefix=[], matches=initial_matches)
        return self.patterns
    
    def check_support(self, pattern: List[Itemset], matches: Matches):
        if len(matches) >= self.minsup:
            self.patterns.append((pattern, len(matches)))

    def build_i_projection(self, prefix: List[Itemset], matches: Matches):
        projected_seqs = []
        for seq_id, lastpos in matches:
            projected_seqs.append([])

            if not prefix:
                projected_seqs[-1].append(self.db[seq_id][0])
                projected_seqs[-1].extend(self.db[seq_id][1:])
            else:
                remaining = self.db[seq_id][lastpos] - prefix[-1]
                projected_seqs[-1].append(remaining)
                if lastpos + 1 < len(self.db[seq_id]):
                    projected_seqs[-1].extend(self.db[seq_id][lastpos + 1:])

        return projected_seqs
    
    def build_s_projection(self, matches: Matches):
        projected_seqs = []
        for seq_id, lastpos in matches:
            projected_seqs.append(self.db[seq_id][lastpos + 1:])
        return projected_seqs
    
    def s_items_index(self, seqs: List[List[Itemset]], matches: Matches):
        index = defaultdict(list)
        for seq_id, seq in enumerate(seqs):
            j, lastIndex = matches[seq_id] if matches else (seq_id, -1)
            for k, itemset in enumerate(seq, start=lastIndex + 1):
               for item in itemset:
                   l = index[item]
                   if l and l[-1][0] == j:
                       continue
                   l.append((j, k))
        return index
    
    def i_items_index(self, seqs: List[List[Itemset]], prefix: List[Itemset], matches: Matches):
        index = defaultdict(list)
        for seq_id, seq in enumerate(seqs):
            j, lastIndex = matches[seq_id] if matches else (seq_id, -1)
            if not seq[0]:
                continue
            for item in seq[0]:
                l = index[item]
                l.append((j, lastIndex if lastIndex >= 0 else 0))
        return index

    def _prefixspan(self, prefix: List[Itemset], matches: Matches):
        if len(matches) < self.minsup:
            return

        if prefix:
            self.check_support(prefix, matches)

        s_projected = self.build_s_projection(matches)
        i_projected = self.build_i_projection(prefix, matches)

        if not s_projected and not i_projected: 
            return
        s_candidates = self.s_items_index(s_projected, matches)
        i_candidates = self.i_items_index(i_projected, prefix, matches)
        
        #pruning
        valid_s_candidates = {item: m for item, m in s_candidates.items() 
                             if len(m) >= self.minsup}
        valid_i_candidates = {item: m for item, m in i_candidates.items() 
                             if len(m) >= self.minsup}

        if not valid_s_candidates and not valid_i_candidates: # condition for end of recursion 
            return
        #s- extesnions 
        for newitem, newmatches in valid_s_candidates.items():
            if len(newmatches) < self.minsup:
                continue
            if len(prefix) > 0:
                newpatt = prefix.copy()
                newpatt.append({newitem})
            else:
                newpatt = [{newitem}]

            self._prefixspan(newpatt, newmatches)
         
         #I -extenstions 
        for newitem, newmatches in valid_i_candidates.items():
            if len(newmatches) < self.minsup: # preventin duplicate patterns through only allowing values > to extend
                continue
            if not prefix:
                continue
            newpatt = [itemset.copy() for itemset in prefix]
            if max(newpatt[len(newpatt)-1]) < newitem:
                newpatt[len(newpatt)-1].add(newitem)
                self._prefixspan(newpatt, newmatches)

if __name__ == "__main__":
    db = [
    [{"A"}, {"B"}, {"C"}],
    [{"A"}, {"B"}, {"C"}],
    [{"A"}, {"B"}]
]    
    from preprocessing import load_spmf_database
    db = load_spmf_database('sign.txt')
    print("done loading")
    minsup = 3
    ps = PrefixSpan(minsup)
    patterns = ps.run(db)

    print("Frequent sequential patterns (with itemsets):")
    for pattern, sup in patterns:
        print(f"{pattern}: {sup}")