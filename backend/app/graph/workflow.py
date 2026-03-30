from app.graph.base import llm,search_tool,client
from langchain.messages import AIMessage,HumanMessage
from app.graph.schema import chat_schema
from langgraph.graph import StateGraph,START,END
from app.services.database import DatabaseService

from google.genai import types

import logging


logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

db_service=DatabaseService()

def build_workflow(memory):

    def chat_node(state:chat_schema):
        message=state.messages

        prompt=f"""
        You are an intelligent AI assistant connected to:
1. A vector database (RAG knowledge base)
2. A web search tool

Your job is to decide whether the user's query can be answered using the RAG knowledge base or requires web search.

User Query:
{message}

Instructions:

1. FIRST, assume the vector database is the primary source.
2. If the query is:
   - Related to stored documents, past conversations, internal knowledge, or specific domain data → USE RAG
   - General knowledge, recent events, unknown topics, or not clearly covered in the database → USE WEB SEARCH

3. If the query is unclear, vague, or you are not confident the RAG contains the answer → USE WEB SEARCH

4. Do NOT hallucinate or guess.

5. Output strictly ONE of the following:
   - "USE_RAG"
   - "NEED_WEB"

Do not output anything else.

"""
        response=llm.invoke(prompt)

        return {"messages":[response]}

    def route_from_chat(state:chat_schema):
        last_message=state.messages[-1].content
        logger.info(f"last message is,{last_message}")

        if "NEED_WEB" in last_message:
            return "web_search"
        if "USE_RAG" in last_message:
            return "document_search"
        return END

    def web_search(state:chat_schema):
        last_msg=state.messages[-2].content
        response=search_tool.search(last_msg)
        return {"messages":[AIMessage(content=response['results'])]}



    def document_search(state:chat_schema):
        last_msg=state.messages[-2].content

        result=client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=last_msg ,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
)
       
        query_embedding=result.embeddings[0].values
   
        docs= db_service.fetch_documents(query_embedding,state.thread_id)   
        
        
        context = "\n".join([doc.content for doc in docs])



        logger.info(f"Retrieved context iss {context}")
        final_prompt = f"""
Answer using ONLY the context.

Context:
{context}

Question:
{last_msg}

If not found, say "I don't know"
"""

        response = llm.invoke(final_prompt)

        return {"messages": [response]}


    graph=StateGraph(chat_schema)

    #nodes creation 
    graph.add_node("chat_node",chat_node)
    graph.add_node("web_search",web_search)
    graph.add_node("document_search",document_search)



    #edges creation
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges(
        "chat_node",
        route_from_chat,
        {
            "web_search":"web_search",
            "document_search":"document_search",
            END:END
        }
        )
    
    graph.add_edge("web_search",END)



    return graph.compile(checkpointer=memory)
