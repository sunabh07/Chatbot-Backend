from graph.base import llm
from graph.schema import chat_schema
import os
from langchain_core.messages import HumanMessage
from graph.workflow import build_workflow
import logging 
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

def chat_function():
    work=build_workflow()
    try:

        while(True):
            user_msg=input("Type your message")
            if not user_msg:
                logger.info("No message by the user")
                
            if user_msg.strip().lower() in ['exit','quit']:
                print("good bye")
                logger.info("chat ended successfully")
                break
            config={"configurable":{"thread_id":1}}
            response=work.invoke(
                {
                    'messages':[HumanMessage(content=user_msg)]
                },
                    config=config
                )
            ai_msg=response['messages'][-1].content
            print("AI MEssage: ",ai_msg)

        return {"message":"chat completed"}
    except Exception as e:
        logger.error(f"Unexpected error in the function: {e}")
        return {"message":"chat failed due to error",
                "error":str(e)
                }
    

