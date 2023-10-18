import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from creator.agents.creator_agent import open_creator_agent
from creator.__version__ import __version__ as version
from langchain.callbacks import tracing_v2_enabled


app = FastAPI(
    title="Open Creator Server",
    version=version,
    description="A simple api server using Langchain's Runnable interfaces",
)


class Request(BaseModel):
    model: str = "open_creator_agent"
    messages: list[dict]
    stream: bool = True
    temperature: float = 0.0


class Response(BaseModel):
    messages: list[dict]
    model: str = "open_creator_agent"
    run_url: str


@app.post("/agents/creator/stream", response_model=Response)
async def complete(request: Request):
    if request.model == "open_creator_agent":
        # with tracing_v2_enabled(project_name="open-creator") as cb:
        # run_url = cb.get_run_url()
        inputs = {"messages": request.messages, "verbose": True}
        if request.stream:
            return StreamingResponse(open_creator_agent.astream(inputs), media_type="application/json")
        else:
    else:
        raise HTTPException(status_code=404, detail="Model not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
