 A = 4
 t = 4
 tp1 = t+1
 D = 96
 L = 6
 assert D%L == 0
 DL = D//L
 threads = t*DL
 
 @cuda.jit(fastmath=True)
+def gpu_sketch(global_hashes, global_signs, seqs, T):
 
+    seq = seqs[cuda.blockIdx.x]
+    end = len(seq)
 
     l = cuda.threadIdx.x
     k = cuda.threadIdx.y
     assert k < t
     assert l < D
 
     # Copy the global hashes/signs to shared memory.
     hashes = cuda.shared.array(shape=(t, A), dtype=nb.int32)
     signs = cuda.shared.array(shape=(t, A), dtype=nb.float32)
     if l < A:
         hashes[k][l] = global_hashes[k][l]
         hashes[k][l] = global_hashes[k][l]
 
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
 
     local_seq = cuda.shared.array(shape=threads, dtype=nb.int32)
     # Loop over characters in the sequence.
     tid = l + k * DL
+    for i in range(end//threads):
+        idx = i*threads + tid
         local_seq[tid] = seq[idx]
         cuda.syncthreads()
 
         for c in local_seq:
             h = hashes[c][k]
             s = signs[c][k]
             # Compute the shifted target index, avoiding a modulo operation.
             for ll in range(L*l, L*(l+1)):
                 r = ll + h
                 r -= D if r >= D else 0
                 # Write to output tensor.
                 Tin[1-j][k+1][ll] = Tin[j][k+1][ll] + s * Tin[j][k][r]
             j = 1-j
             cuda.syncthreads()
 
     # TODO: Handle leftover part of sequence
 
     # Copy to result.
     #for ll in range(L*l, L*(l+1)):
     for ll in range(l, D, DL):
+        T[cuda.blockIdx.x][k+1][ll] = Tin[j][k+1][ll]
 
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
 
+        d_seqs = tuple(cuda.to_device(seq, stream=stream) for seq in seqs)
         d_T = cuda.device_array((blocks, t+1, D), dtype=np.float32, stream=stream)
 
         # One thread per (l, k) <= (D, t)
+        gpu_sketch[(blocks,1), (DL, t), stream](self.d_hashes, self.d_signs, d_seqs, d_T)
 
         return d_T
