# @Created Date: 2021-01-09 01:07:41 pm
# @Filename: align.py
# @Email:  1730416009@stu.suda.edu.cn
# @Author: ZeFeng Zhu
# @Last self.Modified: 2021-01-09 01:07:51 pm
# @Copyright (c) 2021 self.MinghuiGroup, Soochow University
from pdb_profiling.data import blosum62

class GlobalAlign(object):

    def __init__(self, q: str, s: str, M=blosum62, open_gap_score: int = -11, extend_gap_score: int = -1, inf=float('inf')):
        self.q, self.len_q = q, len(q)
        self.s, self.len_s = s, len(s)
        self.M = M
        self.open_gap_score = open_gap_score
        self.extend_gap_score = extend_gap_score
        self.inf = inf
        self.alignments = set()

    def constant_gap_penalty(self, i: int, j: int):
        choices = (
            self.memoize_score[i-1, j-1] + self.M[self.q[i-1], self.s[j-1]],
            self.memoize_score[i-1, j] + self.open_gap_score,
            self.memoize_score[i, j-1] + self.open_gap_score
        )
        max_val = max(choices)
        self.memoize_score[i, j] = max_val
        pointer = ((i-1, j-1), (i-1, j), (i, j-1))
        self.memoize_pointer[i, j] = frozenset(pointer[index] for index in range(3) if choices[index] == max_val)
        return max_val

    def needleman_wunsch(self):
        self.memoize_pointer = dict()
        self.memoize_score = {(0, 0): 0}
        for i in range(1, self.len_q+1):
            self.memoize_pointer[i, 0] = frozenset(((i-1, 0),))
            self.memoize_score[i, 0] = self.open_gap_score*i
        for j in range(1, self.len_s+1):
            self.memoize_pointer[0, j] = frozenset(((0, j-1),))
            self.memoize_score[0, j] = self.open_gap_score*j
        
        for i in range(1, self.len_q+1):
            for j in range(1, self.len_s+1):
                self.constant_gap_penalty(i, j)
        return self.memoize_score[self.len_q, self.len_s]

    def affine_gap_penalty(self, i: int, j: int):
        choices_x = (
            self.memoize_score_m[i, j-1] + self.open_gap_score + self.extend_gap_score,
            self.memoize_score_x[i, j-1] + self.extend_gap_score
        )
        choices_y = (
            self.memoize_score_m[i-1, j] + self.open_gap_score + self.extend_gap_score,
            self.memoize_score_y[i-1, j] + self.extend_gap_score
        )
        max_val_x = max(choices_x)
        max_val_y = max(choices_y)
        self.memoize_score_x[i, j] = max_val_x
        self.memoize_score_y[i, j] = max_val_y

        cur = self.M[self.q[i-1], self.s[j-1]]

        choices_m = (
            self.memoize_score_m[i-1, j-1] + cur,
            self.memoize_score_y[i-1, j-1] + cur,
            self.memoize_score_x[i-1, j-1] + cur
        )
        max_val_m = max(choices_m)
        self.memoize_score_m[i, j] = max_val_m

        pointer_m = (('memoize_pointer_m', (i-1, j-1)), ('memoize_pointer_y', (i-1, j-1)), ('memoize_pointer_x', (i-1, j-1)))
        pointer_x = (('memoize_pointer_m', (i, j-1)), ('memoize_pointer_x', (i, j-1)))
        pointer_y = (('memoize_pointer_m', (i-1, j)), ('memoize_pointer_y', (i-1, j)))
        self.memoize_pointer_m[i, j] = frozenset(pointer_m[index] for index in range(3) if choices_m[index] == max_val_m)
        self.memoize_pointer_x[i, j] = frozenset(pointer_x[index] for index in range(2) if choices_x[index] == max_val_x)
        self.memoize_pointer_y[i, j] = frozenset(pointer_y[index] for index in range(2) if choices_y[index] == max_val_y)
        return max_val_m

    def gotoh_affine(self):
        val_inf = -self.inf
        self.memoize_pointer_m, self.memoize_pointer_x, self.memoize_pointer_y = dict(), dict(), dict()
        self.memoize_score_m, self.memoize_score_x, self.memoize_score_y = dict(), dict(), dict()
        # self.memoize_score = dict()
        
        self.memoize_score_m[0, 0] = 0
        self.memoize_score_x[0, 0] = self.open_gap_score
        self.memoize_score_y[0, 0] = self.open_gap_score

        for i in range(1, self.len_q+1):
            # self.memoize_pointer_m[i, 0] = frozenset(((i-1, 0),))
            # self.memoize_pointer_y[i, 0] = frozenset(((i-1, 0),))
            self.memoize_score_m[i, 0] = val_inf
            self.memoize_score_x[i, 0] = val_inf
            self.memoize_score_y[i, 0] = self.open_gap_score + self.extend_gap_score * i
        for j in range(1, self.len_s+1):
            # self.memoize_pointer_m[0, j] = frozenset(((0, j-1),))
            # self.memoize_pointer_x[0, j] = frozenset(((0, j-1),))
            self.memoize_score_m[0, j] = val_inf
            self.memoize_score_y[0, j] = val_inf
            self.memoize_score_x[0, j] = self.open_gap_score + self.extend_gap_score * j
        
        for i in range(1, self.len_q+1):
            for j in range(1, self.len_s+1):
                self.affine_gap_penalty(i,j)
        te = (self.len_q, self.len_s)
        return max(self.memoize_score_m[te], self.memoize_score_x[te], self.memoize_score_y[te])

    def traceback_needleman_wunsch(self, key, parent=tuple()):
        '''
        deepth first traversal/search traceback (via function stack)  
        '''
        try:
            for child in self.memoize_pointer[key]:
                self.traceback_needleman_wunsch(child, parent=parent+(key,))
        except KeyError:
            self.alignments.add(parent+(key,))
            return

    def traceback_gotoh_affine(self, source, key, parent=tuple()):
        '''
        deepth first traversal/search traceback (via function stack)  
        '''
        try:
            for child_source, child_key in getattr(self, source)[key]:
                self.traceback_gotoh_affine(child_source, child_key, parent=parent+(key,))
        except KeyError:
            self.alignments.add(parent+(key,))
            return
    
    def range_alignment(self, q_base: int = 0, s_base: int = 0):
        def unit(a):
            for x, y in reversed(tuple(zip(a[:-1], a[1:]))):
                if x[0]-y[0]:
                    cur_x = next(seq_q)
                if x[1]-y[1]:
                    cur_y = next(seq_s)
                if x[0]-y[0] and x[1]-y[1]:
                    yield cur_x, cur_y

        for a in self.alignments:
            seq_q = iter(range(1, self.len_q+1))
            seq_s = iter(range(1, self.len_s+1))
            x, y = zip(*unit(a))
            start_x, start_y = x[0], y[0]
            index_x, index_y = x[0]-1, y[0]-1
            interval_x, interval_y = [], []
            for i, j in zip(x, y):
                pre_x = index_x + 1
                pre_y = index_y + 1
                if pre_x == i and pre_y == j:
                    index_x, index_y = i, j
                else:
                    interval_x.append((start_x+q_base, index_x+q_base))
                    interval_y.append((start_y+s_base, index_y+s_base))
                    start_x, start_y = i, j
                    index_x, index_y = i, j
            interval_x.append((start_x+q_base, index_x+q_base))
            interval_y.append((start_y+s_base, index_y+s_base))
            yield interval_x, interval_y

    def show_alignment(self):
        for a in self.alignments:
            seq_q = iter(self.q)
            seq_s = iter(self.s)
            str_x, str_y = '', ''
            # a = np.asarray(a)  (a[:-1] - a[1:])[::-1]
            for x, y in reversed(tuple(zip(a[:-1], a[1:]))):
                str_x += next(seq_q) if x[0]-y[0] else '-'
                str_y += next(seq_s) if x[1]-y[1] else '-'
            yield str_x, str_y
