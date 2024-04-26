from gigabot import GigaBot

from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import load_prompt
from langchain.chains.summarize import load_summarize_chain
import warnings

warnings.filterwarnings('ignore')

class Summirizer(GigaBot):
    """ summirizer for docs. #deprecated
    """
    def txt2documents(self, path_to_txt, chunk_size: int = 5000, chunk_overlap: int = 0):
        loader = TextLoader(path_to_txt)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap  = chunk_overlap,
            length_function = len,
            is_separator_regex = False,
        )
        documents = text_splitter.split_documents(documents)
        return documents
    
    def summarize_txt(self, path_to_txt, map_prompt_path, combine_prompt_path):
        documents = self.txt2documents(path_to_txt)
        map_prompt = load_prompt(map_prompt_path)
        combine_prompt = load_prompt(combine_prompt_path)
        chain = load_summarize_chain(self.model, chain_type="map_reduce",
                                    map_prompt=map_prompt,
                                    combine_prompt=combine_prompt,
                                    verbose=False)
        res = chain.invoke({"input_documents": documents})
        return res["output_text"].replace(". ", ".\n")
    
    def pdf2documents(self, path_to_pdf):
        loader = PyPDFLoader(path_to_pdf)
        pages = loader.load_and_split()
        return pages
    
    def summarize_pdf(self, path_to_pdf, map_prompt_path, combine_prompt_path):
        pages = self.pdf2documents(path_to_pdf)
        map_prompt = load_prompt(map_prompt_path)
        combine_prompt = load_prompt(combine_prompt_path)
        chain = load_summarize_chain(self.model, chain_type="map_reduce",
                                    map_prompt=map_prompt,
                                    combine_prompt=combine_prompt,
                                    verbose=False)
        res = chain.invoke({"input_documents": pages})
        return res["output_text"].replace(". ", ".\n")
    
    def chatting(self, path, filetype):
        if filetype == 'TXT':
            result = self.summarize_txt(path)
        elif filetype == 'PDF':
            result = self.summarize_pdf(path)
        return result