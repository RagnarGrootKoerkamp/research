 A = 4
 t = 4
 tp1 = t+1
 D = 96
+L = 6
+assert D%L == 0
+DL = D//L
+threads = t*DL
 
 @cuda.jit(fastmath=True)
 def gpu_sketch(hashes, signs, seq, starts, T):
     seqid = cuda.blockIdx.x
     start = starts[seqid]
     end = starts[seqid+1]
 
     l = cuda.threadIdx.x
     k = cuda.threadIdx.y
     assert k < t
     assert l < D
 
     # Shared memory for temporary DP tables.
     Tin = cuda.shared.array(shape=(2, tp1, D), dtype=nb.float32)
 
     Tin[0][k][l] = 0
     Tin[0][k+1][l] = 0
     Tin[1][k][l] = 0
     Tin[1][k+1][l] = 0
 
     cuda.syncthreads()
 
     Tin[0][0][0] = 1
     Tin[1][0][0] = 1
 
     cuda.syncthreads()
 
     j = 0
 
     # Loop over characters in the sequence.
     for i in range(start, end):
         c = seq[i]
         h = hashes[c][k]
         s = signs[c][k]
         # Compute the shifted target index, avoiding a modulo operation.
+        for ll in range(L*l, L*(l+1)):
+            r = ll + h
+            r -= D if r >= D else 0
+            # Write to output tensor.
+            Tin[1-j][k+1][ll] = Tin[j][k+1][ll] + s * Tin[j][k][r]
         j = 1-j
         cuda.syncthreads()
 
     # Copy to result.
+    for ll in range(L*l, L*(l+1)):
+        T[seqid][k+1][ll] = Tin[j][k+1][ll]
 
 
 class GTS:
     def __init__(self):
         random.seed(31415)
         # An A*t array of random integers in [0, D)
         self.hashes = np.empty((A, t), dtype=np.int32)
         # An A*t array of random +-1
         self.signs  = np.empty((A, t), dtype=np.float32)
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
 
         # One thread per (l, k) <= (D, t)
+        gpu_sketch[(blocks,1), (DL, t), stream](self.d_hashes, self.d_signs, d_seq, d_starts, d_T)
 
         return d_T
