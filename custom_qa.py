from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

import os 
os.environ["OPENAI_API_KEY"] = "INSERT YOUR API KEY!"

from langchain_community.document_loaders import PyPDFLoader

# PDF 파일 경로 목록
pdf_files = [
    "1.pdf",
    "2.pdf",
]

# 로더, 텍스트 분할기 및 임베딩 초기화
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
embeddings = OpenAIEmbeddings()

texts = []

# 각 PDF 파일에 대해 작업 수행
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    documents = loader.load()
    texts.extend(text_splitter.split_documents(documents))

docsearch = Chroma.from_documents(texts, embeddings)

from langchain.prompts import PromptTemplate
prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Answer in Korean:"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}
qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0), 
                                 chain_type="stuff", 
                                 retriever=docsearch.as_retriever(), 
                                 return_source_documents=True, 
                                 chain_type_kwargs=chain_type_kwargs)


# 사용자로부터 질문을 입력받고 답변 생성
while True:
    query = input("Enter your question (or type 'exit' to quit): ")
    if query.lower() == "exit":
        break
    result = qa.invoke({"query": query})
    answer = result['result']
    print("Answer:", answer)