from langchain.messages import AIMessage,HumanMessage
from app.graph.base import llm
from app.graph.workflow import build_workflow
import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def process_message(memory,thread_id,query):

    logger.info("Inside message workflow")


    work = build_workflow(memory)
    if not query:
        return {
                "error":"Empty message not allowed",
                "answer":None
                    }
        
    config={"configurable":{"thread_id":thread_id}}
    try:

        response=work.invoke(
            {
                "messages":[HumanMessage(content=query)],
                "thread_id":thread_id
            },
            config=config
        )
        ai_content=response['messages'][-1].content

        return {
            "answer":ai_content,
            "error":None
        }
    except Exception as e:
        logger.error(f"Error occured during chat,{str(e)}")
        return {
            "error":str(e),
            "answer":None
        }


