from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.tools.retriever import create_retriever_tool
from langchain.chains import create_history_aware_retriever
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from dotenv import load_dotenv
import os
import pandas as pd

def ask_something(chain, query):

    print(f"User : {query}")

    chain_output = chain.invoke(
        {"input": query}
    )

    print(f"LLM : {chain_output}")


    return

def load_csv(file_path):
    df = pd.read_csv(file_path)
    documents = []
    for _, row in df.iterrows():
        content = " ".join([str(value) for value in row])
        documents.append(Document(page_content=content, metadata={"source": "csv"}))
    return documents


def init_retriever(documents):
    embedding_model = AzureOpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    chroma = Chroma("vector_store")
    vector_store = chroma.from_documents(
        documents=documents,
        embedding=embedding_model
    )

    retriever = vector_store.as_retriever(search_type="similarity")
    return retriever


def init_agent(tools):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an helpful AI assistant that helps people to give the best answer for questions in Korean"),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    azure_model = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.getenv("OPENAI_API_VERSION")
    )

    agent = create_tool_calling_agent(azure_model, tools, prompt_template)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=10)

    memory = ConversationBufferMemory(
        chat_memory=InMemoryChatMessageHistory(),
        return_messages=True
    )

    load_context_runnable = RunnablePassthrough().assign(
        chat_history=RunnableLambda(lambda x: memory.chat_memory.messages)
    )

    def save_context(agent_output):
        memory.chat_memory.add_user_message(agent_output["input"])
        memory.chat_memory.add_ai_message(agent_output["output"])
        return agent_output["output"]

    save_context_runnable = RunnableLambda(save_context)
    agent_chain = load_context_runnable | agent_executor | save_context_runnable
    return agent_chain

def init_chain(retriever):
    azure_model = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.getenv("OPENAI_API_VERSION")
    )

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        azure_model, retriever, contextualize_q_prompt
    )

    qa_system_prompt_str = """
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you cannot find the answer in the retrieved context, try to find it in chat history.
    If you don't know the answer after all, just say that you don't know. 
    Use three sentences maximum and keep the answer concise.
    Answer the question in Korean.
    
    {context} """.strip()

    qa_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt_str),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(azure_model, qa_prompt_template)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    memory = ConversationBufferMemory(
        chat_memory=InMemoryChatMessageHistory(),
        return_messages=True
    )

    load_context_runnable = RunnablePassthrough().assign(
        chat_history=RunnableLambda(lambda x: memory.chat_memory.messages)
    )

    def save_context(chain_output):
        memory.chat_memory.add_user_message(chain_output["input"])
        memory.chat_memory.add_ai_message(chain_output["answer"])
        return chain_output["answer"]

    save_context_runnable = RunnableLambda(save_context)
    rag_chain_with_history = load_context_runnable | rag_chain | save_context_runnable
    return rag_chain_with_history

if __name__ == "__main__":
    load_dotenv()

    csv_filepath = "/Users/jmj/Accommodation-Recommender/Data/preprocessed_dataset.csv"
    documents = load_csv(csv_filepath)
    
    retriever = init_retriever(documents)

    tool = create_retriever_tool(
        retriever,
        "retriever_indexing",
        "Indexing, Embedding, and comparing doc similarity"
    )

    tools = [tool]
    agent_chain = init_agent(tools)

    while True:
        q = input("You: ")
        ask_something(agent_chain, q)

