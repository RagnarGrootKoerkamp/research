 A = 4
 t = 4
 tp1 = t+1
 D = 96
 L = 6
 assert D%L == 0
 DL = D//L
 threads = t*DL
 
 @cuda.jit(fastmath=True)
+def gpu_sketch_15(A, t, D, L, global_hashes, global_signs, seq, starts, T):
     seqid = cuda.blockIdx.x
     start = starts[seqid]
     end = starts[seqid+1]
 
     l = cuda.threadIdx.x
     k = cuda.threadIdx.y
     assert k < t
     assert l < D
 
+    plane = tp1*D
+    threads = t*D//L
 
+    # NOTE: Tin has an offset of k*D to save a bit on further computations.
+    Tin = cuda.shared.array(shape=0, dtype=nb.float32)[k*D:2*plane]
+    local_seq = cuda.shared.array(shape=0, dtype=nb.int32)[2*plane:2*plane+threads]
 
+    signs = cuda.shared.array(shape=0, dtype=nb.float32)[2*plane+threads:2*plane+threads+A*t]
+    hashes = cuda.shared.array(shape=0, dtype=nb.int32)[2*plane+threads+A*t:2*plane+threads+2*A*t]
+
+    # Copy the global hashes/signs to shared memory.
+    if l < A:
+        hashes[l*t+k] = global_hashes[l][k]
+        signs[l*t+k] = global_signs[l][k]
 
+    for ll in range(l, D, D//L):
+        Tin[0*plane + 0*D + ll] = 0
+        Tin[0*plane + (0+1)*D + ll] = 0
+        Tin[1*plane + 0*D + ll] = 0
+        Tin[1*plane + (0+1)*D + ll] = 0
 
     cuda.syncthreads()
 
+    if k==0:
+        Tin[0] = 1
+        Tin[plane] = 1
 
     cuda.syncthreads()
 
     j = 0
 
     # Loop over characters in the sequence.
+    tid = l + k * D//L
     for i in range((end-start)//threads):
         idx = start + i*threads + tid
         local_seq[tid] = seq[idx]
         cuda.syncthreads()
 
         for c in local_seq:
+            h = hashes[c*t+k]
+            s = signs[c*t+k]
             # Compute the shifted target index, avoiding a modulo operation.
+            j2 = plane-j
             for ll in range(L*l, L*(l+1)):
                 r = ll + h
                 r -= D if r >= D else 0
                 # Write to output tensor.
+                Tin[j2 + D + ll] = Tin[j + D + ll] + s * Tin[j + r]
 
+            j = j2
+            cuda.syncthreads()
 
     # Copy to result.
+    for ll in range(l, D, D//L):
+        T[seqid][k][ll] = Tin[j +  ll]
+        T[seqid][k+1][ll] = Tin[j + D + ll]
 
+class GTS_15:
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
 
+        ts = TS_1()
+        self.hashes = np.array(ts.hashes, dtype=np.int32)
+        self.signs = np.array(ts.signs, dtype=np.float32)
+
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
+        gpu_sketch_15[(blocks,1), (DL, t), stream, 4*(threads+2*tp1*D+2*A*t)](np.int32(A), np.int32(t), np.int32(D), np.int32(L), self.d_hashes, self.d_signs, d_seq, d_starts, d_T)
 
         return d_T
