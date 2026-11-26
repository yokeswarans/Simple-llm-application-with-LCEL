"""
Langserve.py - Serve a LangChain translation chain as a REST API
==================================================================

What is LangServe?
------------------
LangServe is a library from LangChain that turns any LangChain "runnable"
(a chain, prompt, model, parser, etc.) into a ready-to-use REST API.

Normally a chain only works inside your Python script or notebook. With
LangServe, you hand it the chain and it automatically:
  * creates web endpoints (URLs) that other programs can call over HTTP,
  * checks that incoming requests have the right input format,
  * generates interactive API docs and a browser "playground" for testing.

LangServe is built on top of FastAPI (a popular Python web framework), so
the server we create here is a normal FastAPI app.

What this file does
-------------------
1. Loads API keys from the .env file.
2. Builds a simple LCEL chain:  prompt -> model -> parser
   that translates text into a chosen language.
3. Exposes that chain as an API at the path "/chain" using LangServe.
4. Starts a web server on http://localhost:5000

How to run it
-------------
    pip install fastapi uvicorn langserve[all] langchain-groq python-dotenv
    python Langserve.py

Then open in your browser:
    http://localhost:5000/docs              -> auto-generated API docs
    http://localhost:5000/chain/playground/ -> interactive page to try the chain

Example request (from another program or terminal):
    POST http://localhost:5000/chain/invoke
    Body (JSON):
        {"input": {"language": "French", "text": "Hello, how are you?"}}
"""

import os

# python-dotenv reads the key=value pairs in the .env file and adds them
# to the environment, so os.getenv("GROQ_API_KEY") can find them.
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI                                  # Web framework that LangServe runs on
from langchain_core.prompts import ChatPromptTemplate        # Builds prompts with {placeholders}
from langchain_core.output_parsers import StrOutputParser    # Turns the model's reply into a plain string
from langchain_groq import ChatGroq                          # Chat model hosted on Groq
from langserve import add_routes                             # Attaches a chain to the FastAPI app as API endpoints

# Make sure the Groq API key is available to the LangChain libraries.
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")


# ---------------------------------------------------------------------------
# Step 1: Create the LLM (Large Language Model)
# ---------------------------------------------------------------------------
# ChatGroq connects to a model running on Groq's servers.
# "openai/gpt-oss-20b" is the name of the open-weights model we want to use.
model = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------------------------------------------------
# Step 2: Create the prompt template
# ---------------------------------------------------------------------------
# A prompt template is a reusable message layout with placeholders.
#   {language} -> the language to translate into (e.g. "French")
#   {text}     -> the text the user wants translated
# The "system" message tells the model what job to do;
# the "user" message holds the actual input.
system_template = "Translate the following into {language}"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])


# ---------------------------------------------------------------------------
# Step 3: Create the output parser
# ---------------------------------------------------------------------------
# The model returns a message object (AIMessage). StrOutputParser pulls out
# just the text, so the API returns a clean string like "Bonjour".
parser = StrOutputParser()


# ---------------------------------------------------------------------------
# Step 4: Build the chain using LCEL (LangChain Expression Language)
# ---------------------------------------------------------------------------
# The "|" (pipe) operator connects the pieces: the output of each step
# becomes the input of the next.
#
#   {"language": ..., "text": ...}  ->  prompt  ->  model  ->  parser  ->  "translated text"
chain = prompt_template | model | parser


# ---------------------------------------------------------------------------
# Step 5: Create the web application
# ---------------------------------------------------------------------------
# FastAPI creates the web server. The title, version and description
# are shown on the auto-generated docs page (http://localhost:5000/docs).
app = FastAPI(
    title="Langchain Server",
    version='1.0',
    description=" A simple API server using langchain runnable interfaces"
)


# ---------------------------------------------------------------------------
# Step 6: Expose the chain as an API with LangServe
# ---------------------------------------------------------------------------
# add_routes() is the core of LangServe. It takes our chain and creates
# several endpoints under the given path ("/chain"), including:
#   POST /chain/invoke       -> run the chain once and get the full result
#   POST /chain/batch        -> run the chain on a list of inputs at once
#   POST /chain/stream       -> get the result piece by piece as it's generated
#   GET  /chain/playground/  -> a web page to try the chain in your browser
add_routes(
    app,
    chain,
    path="/chain"
)


# ---------------------------------------------------------------------------
# Step 7: Start the server
# ---------------------------------------------------------------------------
# This block only runs when you execute the file directly
# (python Langserve.py), not when it is imported by another file.
# uvicorn is the server program that actually listens for HTTP requests.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="localhost",   # Only accessible from this computer
        port=5000           # Server address: http://localhost:5000
    )
