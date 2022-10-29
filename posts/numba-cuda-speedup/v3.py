A = 4
t = 4
tp1 = t+1
D = 96

@cuda.jit
def gpu_sketch(hashes, signs, seq, T):
    k = cuda.threadIdx.x
    l = cuda.threadIdx.y
    assert k < t
    assert l < D

    # Shared memory for temporary DP tables.
    Tin = cuda.shared.array(shape=(tp1, D), dtype=nb.float32)
    Tout = cuda.shared.array(shape=(tp1, D), dtype=nb.float32)

    Tin[k][l] = 0
    Tin[k+1][l] = 0
    Tout[k][l] = 0
    Tout[k+1][l] = 0

    cuda.syncthreads()

    Tin[0][0] = 1
    Tout[0][0] = 1

    cuda.syncthreads()

    # Loop over characters in the sequence.
    for c in seq:
        h = hashes[c][k]
        s = signs[c][k]
        # Compute the shifted target index, avoiding a modulo operation.
        r = l + h
        r -= D if r >= D else 0
        # Write to output tensor.
        Tout[k+1][l] = Tin[k+1][l] + s * Tin[k][r]
        cuda.syncthreads()
        # Copy output back to input.
        Tin[k+1][l] = Tout[k+1][l]
        cuda.syncthreads()

    # Copy to result.
    T[k+1][l] = Tout[k+1][l]


class GTS:
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
        # Allocate memory for the response.
        T = np.zeros((t+1, D), dtype=np.float32)
        # One thread per (k, l) <= (t, D)
        gpu_sketch[(1,1), (t, D)](self.hashes, self.signs, seq, T)
        return T
