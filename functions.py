# Import libraries
import re
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct

# Define a function for text preparation
def text_prepare(text):
    """
        text: a string
        
        return: a clean string
    """
    # Remove special characters
    REPLACE_BY_SPACE_RE = re.compile('[\n\"\'/(){}\[\]\|@,;#]')
    text = re.sub(REPLACE_BY_SPACE_RE, ' ', text)    
    
    # Replace multiple spaces with a single space
    text = re.sub(' +', ' ', text)    
    
    # Convert the text to lowercase
    text = text.lower()  

    # Remove leading and trailing spaces  
    text = text.strip()    
    
    # Return cleaned text
    return text

# Define a function to compute cosine similarity
def awesome_cossim_top(A, B, ntop, lower_bound=0):
    # force A and B as a CSR matrix
    # If they have already been CSR, there is no overhead
    A = A.tocsr()
    B = B.tocsr()

    # Get matrix dimensions
    M, _ = A.shape
    _, N = B.shape

    # Set index data type for result
    idx_dtype = np.int32

    # Calculate max number of non-zero elements
    nnz_max = M * ntop

    # Initialize arrays for CSR matrix data structure
    indptr = np.zeros(M + 1, dtype=idx_dtype)
    indices = np.zeros(nnz_max, dtype=idx_dtype)
    data = np.zeros(nnz_max, dtype=A.dtype)

    # Perform matrix multiplication with top n cosine similarities
    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype=idx_dtype),
        np.asarray(A.indices, dtype=idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype=idx_dtype),
        np.asarray(B.indices, dtype=idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, indices, data
    )

    # Return CSR matrix with result data
    return csr_matrix((data, indices, indptr), shape=(M, N))

# Define a function to create a match table to show the similarity scores
def get_matches_df(sparse_matrix, name_vector, top=100):
    # Get non-zero elements' indices
    non_zeros = sparse_matrix.nonzero()
    sparserows, sparsecols = non_zeros

    # Set number of matches to retrieve
    nr_matches = top if top else sparsecols.size

    # Initialize arrays for storing match data
    left_side = np.empty([nr_matches], dtype=object)
    right_side = np.empty([nr_matches], dtype=object)
    score = np.zeros(nr_matches)

    # Populate arrays with match data
    for index in range(nr_matches):
        left_side[index] = name_vector[sparserows[index]]
        right_side[index] = name_vector[sparsecols[index]]
        score[index] = sparse_matrix.data[index]

    # Return DataFrame with match data
    return pd.DataFrame({'left_dataset': left_side,
                         'right_dataset': right_side,
                         'confidence_score': score})