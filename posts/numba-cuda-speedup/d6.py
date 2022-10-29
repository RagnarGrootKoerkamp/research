 A = 4
 t = 4
 tp1 = t+1
 D = 96
 
+@cuda.jit(fastmath=True)
 def gpu_sketch(hashes, signs, seq, starts, T):
     seqid = cuda.blockIdx.x
     start = starts[seqid]
     end = starts[seqid+1]
 
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
     for i in range(start, end):
         c = seq[i]
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
     T[seqid][k+1][l] = Tout[k+1][l]
 
 
 class GTS:
     def __init__(self):
         random.seed(31415)
         # An A*t array of random integers in [0, D)
+        self.hashes = np.empty((A, t), dtype=np.int32)
         # An A*t array of random +-1
+        self.signs  = np.empty((A, t), dtype=np.float32)
         for c in range(A):
             for k in range(t):
                 self.hashes[c][k] = random.randrange(0, D)
                 self.signs[c][k] = random.randrange(-1, 2, 2)
 
         self.d_hashes = cuda.to_device(self.hashes)
         self.d_signs = cuda.to_device(self.signs)
 
     def sketch(self, seqs):
         # Allocate memory for the response.
         stream = cuda.stream()
 
         blocks = len(seqs)
 
         seq = np.concatenate(seqs)
         starts = np.array(np.cumsum(np.array([0] + [len(seq) for seq in seqs]), dtype=np.int32), dtype=np.int32)
 
         d_seq = cuda.to_device(seq, stream=stream)
         d_starts = cuda.to_device(starts, stream=stream)
         d_T = cuda.device_array((blocks, t+1, D), dtype=np.float32, stream=stream)
 
         # One thread per (k, l) <= (t, D)
         gpu_sketch[(blocks,1), (t, D), stream](self.d_hashes, self.d_signs, d_seq, d_starts, d_T)
 
         return d_T
