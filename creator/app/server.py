from fastapi import FastAPI
from creator.agents.creator_agent import create_llm, create_creator_agent
from creator.config.library import config
from creator.__version__ import __version__ as version
from pydantic import BaseModel


class Input(BaseModel):
    messages: list[dict]


class Output(BaseModel):
    messages: list[dict]


app = FastAPI(
    title="Open Creator Server",
    version=version,
    description="A simple api server using Langchain's Runnable interfaces",
)

config.use_rich = False
open_creator_agent = create_creator_agent(create_llm(config))


@app.post("/agents/creator")
async def run_agent(inputs: Input):
    return await open_creator_agent.ainvoke(inputs.model_dump())


def run_server(host="0.0.0.0", port=8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)
