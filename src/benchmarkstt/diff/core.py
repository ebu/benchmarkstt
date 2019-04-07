from difflib import SequenceMatcher


class HuntMcIlroy:
    """Implements the Hunt–McIlroy algorithm.

    More information available at https://en.wikipedia.org/wiki/Hunt%E2%80%93McIlroy_algorithm

    Mimics structure of difflib.SequenceMatcher
    Code based on https://gist.github.com/jorendorff/5040491
    """
    # TODO: make a proper diff implementing Hunt–McIlroy algorithm
    #      (see https://github.com/ebu/ai-benchmarking-stt/issues/30 )
    def __init__(self, a='', b=''):
        self.a = a
        self.b = b
        self.opcodes = None
        self.matching_blocks = None

    def set_seqs(self, a, b):
        self.a = a
        self.b = b

    def set_seq1(self, a):
        self.a = a

    def set_seq2(self, b):
        self.b = b

    def find_longest_match(self, alo, ahi, blo, bhi):
        raise NotImplementedError()
        a, b = self.a, self.b
        sa, sb, n = alo, blo, 0

        runs = {}
        for i in range(alo, ahi):
            new_runs = {}
            for j in range(blo, bhi):
                if a[i] == b[j]:
                    k = new_runs[j] = runs.get(j - 1, 0) + 1
                    if k > n:
                        sa = i - k + 1
                        sb = j - k + 1
                        n = k
            runs = new_runs

        assert a[sa:sa + n] == b[sb:sb + n]
        return sa, sb, n

    # re-use get_matching_blocks and get_opcodes from difflib
    get_matching_blocks = SequenceMatcher.get_matching_blocks
    get_opcodes = SequenceMatcher.get_opcodes


class RatcliffObershelp(SequenceMatcher):
    def __init__(self, a, b, *args, **kwargs):
        if 'autojunk' not in kwargs:
            kwargs['autojunk'] = False
        super().__init__(a=a, b=b, *args, **kwargs)
