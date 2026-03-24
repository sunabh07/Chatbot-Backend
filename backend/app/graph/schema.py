from pydantic import BaseModel,Field
from langchain_core.messages import BaseMessage
from typing import Optional, List, Annotated
from langgraph.graph.message import add_messages



class chat_schema(BaseModel):
    messages:Annotated[list[BaseMessage],add_messages]
    query:Optional[str]=None
    thread_id:str