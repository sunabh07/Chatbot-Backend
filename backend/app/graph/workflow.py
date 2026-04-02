from app.graph.base import llm,search_tool,client
from langchain.messages import AIMessage,HumanMessage
from app.graph.schema import chat_schema
from langgraph.graph import StateGraph,START,END
from app.services.database import DatabaseService
import json
from google.genai import types
from app.services.email_service import email_service
import asyncio  
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
3. A Email sender tool 
4. A Email fetcher tool (In which Users inbox is present all its mails)

Your job is to decide whether the user's query can be answered using the RAG knowledge base or requires web search.

User Query:
{message}

Instructions:

1. FIRST, assume the vector database is the primary source.
2. If the query is:
   - Related to stored documents, past conversations, internal knowledge, or specific domain data → USE RAG
   - General knowledge, recent events, unknown topics, or not clearly covered in the database → USE WEB SEARCH
   - User asks to send email / share report / mail something → SEND_EMAIL
   - User asks to read emails / inbox / messages → FETCH_EMAILS

3. If the query is unclear, vague, or you are not confident the RAG contains the answer → USE WEB SEARCH

4. Do NOT hallucinate or guess.

5. Output strictly ONE of the following:
   - "USE_RAG"
   - "NEED_WEB"
   - "SEND_EMAIL"
   - "FETCH_EMAILS

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
        if "SEND_EMAIL" in last_message:
            return "send_email"
        if "FETCH_EMAILS" in last_message:
            return "fetch_emails"
        return END

    def web_search(state:chat_schema):
        last_msg=state.messages[-2].content
        response=search_tool.search(last_msg)
        return {"messages":[AIMessage(content=response['results'])]}


    def send_email(state:chat_schema):
        last_message=state.messages[-2].content

        prompt=f"""
From the users last message, you have to extract the following things
- email
- subject
- body

User Query:
{last_message}

You have to return the output as mentioned below and in this format only 


Return in JSON:
{{
    "email": "",
    "subject": "",
    "body": ""
}}

You MUST return ONLY valid JSON.
Do NOT wrap in ```json or ``` blocks.
Do NOT add any explanation.
"""
        response=llm.invoke(prompt)
        logger.info(f"This the response we got {response.content}")
        try:
            data=json.loads(response.content)
            logger.info(f"data recieved is {data}")
        except:
            return {"messages": [AIMessage(content="Could not extract email details")]}
        
        asyncio.create_task(
        email_service.send_mail(
            to_email=data["email"],
            subject=data["subject"],
            body=data["body"]
        )
    )

        return {"messages": [AIMessage(content="Email sent successfully")]}
        
    
    def fetch_emails(state:chat_schema):
        last_message=state.messages[-2].content
        emails=email_service.get_mail(limit=100)

         # Convert to text
        email_text = "\n".join([
        f"From: {e['from']} | Subject: {e['subject']}"
        for e in emails
    ])
        logger.info(f"Emails converted into email_text are {email_text}")
        prompt = f"""
User Query:
{last_message}

Here are emails:
{email_text}

Based on the Users query, return relevant emails or summary. Fetch all the relevant emails and then answer according to the user's query 
"""
        response=llm.invoke(prompt)

        return {"messages":[response]}




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


    
    #graph initialization
    graph=StateGraph(chat_schema)



    #nodes creation 
    graph.add_node("chat_node",chat_node)
    graph.add_node("web_search",web_search)
    graph.add_node("document_search",document_search)
    graph.add_node("send_email",send_email)
    graph.add_node("fetch_emails",fetch_emails)



    #edges creation
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges(
        "chat_node",
        route_from_chat,
        {
            "web_search":"web_search",
            "document_search":"document_search",
            "send_email":"send_email",
            "fetch_emails":"fetch_emails",
            END:END
        }
        )
    
    
    graph.add_edge("web_search",END)



    return graph.compile(checkpointer=memory)
