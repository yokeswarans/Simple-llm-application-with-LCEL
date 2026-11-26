import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes

os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

model = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

system_template = "Translate the following into {language}"
prompt_template = ChatPromptTemplate.from_messages([
    ('system',system_template),
    ('user','{text}')
])


parser = StrOutputParser()

chain = prompt_template | model | parser


app = FastAPI(
    title="Langchain Server",
    version='1.0',
    description=" A simple API server using langchain runnable interfaces"
)

add_routes(
    app,
    chain,
    path = "/chain"
)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="localhost",
        port=5000
    )
