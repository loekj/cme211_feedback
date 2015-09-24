# Example matrix from the book by Davis
file_name = "example_A.mtx"

# Read the matrix data
import scipy.io as io
A = io.mmread(file_name)
A = A + A.transpose()
n = A.shape[0] # Size of matrix

# Convert the matrix to CSC format
#--4_7
#--This is just very bad code dude!
#--You know why? Check this out:
#--START
import scipy.sparse as sp
A = sp.csc_matrix(A)
#--END

# CSC data
#--syntax_2
#--very bad code because of
#--the folowing
#--here it is:
#--START
Ax = A.data    # Matrix entries
Ap = A.indptr  # Size of Ap = size of matrix
#--END
Ai = A.indices # Row indices for entries in Ax

# We plot the graph of A use a DOT file
file = open('graph_A.dot','w') # Open file
file.write("graph G {\n")
for k in range(n):
    for p in range(Ap[k],Ap[k+1]):
        if Ai[p] < k:
            str = "{} -- {};\n".format(k+1,Ai[p]+1)
            file.write(str)
file.write("labelloc=\"t\";")
file.write("label=\"Graph of A\";")
file.write("}")
file.close() # Close file
