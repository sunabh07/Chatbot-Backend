from app.graph.base import llm,search_tool
from langchain.messages import AIMessage,HumanMessage
from app.graph.schema import chat_schema
from langgraph.graph import StateGraph,START,END

import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


def build_workflow(memory):

    def chat_node(state:chat_schema):
        message=state.messages

        prompt=f"""
        You are an expert AI whose job is to answer the questions of the user based on your knowledge
        User message : {message}
        If you think that query is out of your knowledge base and would require some web search
        then answer only:NEED_WEB
        otherwise answer as you know

"""
        response=llm.invoke(prompt)

        return {"messages":[response]}

    def route_from_chat(state:chat_schema):
        last_message=state.messages[-1].content
        logger.info(f"last message is,{last_message}")

        if "NEED_WEB" in last_message:
            return "web_search"
        return END

    def web_search(state:chat_schema):
        last_msg=state.messages[-2].content
        response=search_tool.search(last_msg)
        return {"messages":[AIMessage(content=response['results'])]}

    graph=StateGraph(chat_schema)

    graph.add_node("chat_node",chat_node)
    graph.add_node("web_search",web_search)



    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges(
        "chat_node",
        route_from_chat,
        {
            "web_search":"web_search",
            END:END
        }
        )
    
    graph.add_edge("web_search",END)



    return graph.compile(checkpointer=memory)
