# Simple LLM Application with LCEL

A beginner-friendly project that builds a small **translation app** using **LangChain Expression Language (LCEL)** and a model hosted on **Groq**, then serves it as a REST API with **LangServe**.

## What's in this repo

| File | Description |
|------|-------------|
| `SimplellmLCEL.ipynb` | Step-by-step notebook: calling a chat model, parsing output, prompt templates, and chaining everything with LCEL. Includes a translation example and an article-writing example. |
| `Langserve.py` | Turns the translation chain into a web API using LangServe + FastAPI, with a browser playground for testing. |
| `requirements.txt` | Python packages needed to run the project. |
| `.env` *(not committed)* | Your API keys (see setup below). |

## Key concepts

- **Chat model (`ChatGroq`)** – sends messages to the `openai/gpt-oss-20b` model running on Groq.
- **Prompt template (`ChatPromptTemplate`)** – a reusable message layout with placeholders like `{language}` and `{text}`.
- **Output parser (`StrOutputParser`)** – turns the model's reply into a plain string.
- **LCEL** – connects components with the `|` operator:
  ```
  {"language", "text"}  ->  prompt  ->  model  ->  parser  ->  translated text
  ```
- **LangServe** – exposes any LangChain chain as a REST API with auto-generated docs and a playground.
- **LangSmith tracing** – (notebook) logs each chain run to the LangSmith dashboard for debugging.

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/yokeswarans/Simple-llm-application-with-LCEL.git
   cd Simple-llm-application-with-LCEL
   ```

2. **Create an environment and install dependencies**
   ```bash
   conda create -n langchain python=3.11
   conda activate langchain
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project folder:
   ```env
   GROQ_API_KEY=your_groq_api_key
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=your_project_name
   OPENAI_API_KEY=your_openai_api_key
   ```
   - `GROQ_API_KEY` is required (get one at [console.groq.com](https://console.groq.com)).
   - The `LANGCHAIN_*` keys are only needed for LangSmith tracing in the notebook.

## Usage

### Run the notebook
Open `SimplellmLCEL.ipynb` in Jupyter or VS Code, select your environment's kernel, and run the cells from top to bottom.

### Run the API server
```bash
python Langserve.py
```
The server starts at `http://localhost:5000`. Then open:

- **Playground:** http://localhost:5000/chain/playground/ – try the chain in your browser
- **API docs:** http://localhost:5000/docs – auto-generated endpoint docs

**Example request:**
```bash
curl -X POST http://localhost:5000/chain/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"language": "German", "text": "Hello, how are you?"}}'
```

**Example response:**
```json
{"output": "Hallo, wie geht es dir?", ...}
```

### Available endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chain/invoke` | Run the chain once on a single input |
| POST | `/chain/batch` | Run the chain on a list of inputs |
| POST | `/chain/stream` | Stream the output as it's generated |
| GET | `/chain/playground/` | Interactive web UI |

## Tech stack

- [LangChain](https://python.langchain.com/) (LCEL)
- [Groq](https://groq.com/) – fast LLM inference
- [LangServe](https://github.com/langchain-ai/langserve) + [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
- [LangSmith](https://smith.langchain.com/) – tracing (optional)
