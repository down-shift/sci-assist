from langchain_community.embeddings.gigachat import GigaChatEmbeddings
import numpy as np
from langchain.evaluation import load_evaluator
import warnings

warnings.filterwarnings('ignore')
TOKEN = "NTlkY2MyZmItM2Q4ZC00ZWMzLWE2NjAtNTI3MzZhOTk2ZjQzOjVhZGJiZDQxLTc0YjAtNDQxNi04YjAzLTUxZDVmYTY4NTkwNw=="


embedding_model = GigaChatEmbeddings(
    credentials=TOKEN, verify_ssl_certs=False, scope="GIGACHAT_API_CORP"
)
evaluator = load_evaluator("embedding_distance", embeddings=embedding_model)

def getsim(text1, text2):
    return evaluator.evaluate_strings(prediction=text1, reference=text2)['score']

def getsims(text, references):
    sims = []
    
    for ref in references:
        sims.append(getsim(text, ref))
    
    return sims