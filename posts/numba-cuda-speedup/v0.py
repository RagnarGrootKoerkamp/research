A = 4
t = 4
D = 96

class TS:
    def __init__(self):
        random.seed(31415)
        # An A*t array of random integers in [0, D)
        self.hashes = np.empty((A, t), dtype=np.int64)
        # An A*t array of random +-1
        self.signs  = np.empty((A, t), dtype=np.int64)
        for c in range(A):
            for k in range(t):
                self.hashes[c][k] = random.randrange(0, D)
                self.signs[c][k] = random.randrange(-1, 2, 2)

    def sketch(self, seq):
        T = np.zeros((t+1, D), dtype=np.int64)
        T[0][0] = 1

        for c in seq:
            for k in range(t-1, -1, -1):
                h = self.hashes[c][k]
                s = self.signs[c][k]
                T[k+1] += s * np.roll(T[k], h)

        return T[t]

