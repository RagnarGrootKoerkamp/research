 A = 4
 t = 4
 D = 96
 
+@jitclass([('hashes', nb.int64[:,:]), ('signs', nb.int64[:,:])])
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
+                for l in range(D):
+                    r = l+h if l+h < D else l+h-D
+                    T[k+1][l] += s * T[k][r]
 
         return T[t]
