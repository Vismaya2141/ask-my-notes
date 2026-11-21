# agent_langchain.py - the same agent in a few lines, with LangChain
from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from tools import SYSTEM_PROMPT, search_notes, calculate, today, add_task

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

tools = [tool(search_notes), tool(calculate), tool(today), tool(add_task)]
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    return_intermediate_steps=True,
)


def ask_agent(question):
    result = agent_executor.invoke({"input": question})
    steps = [action.tool for action, _ in result["intermediate_steps"]]
    return result["output"], steps


if __name__ == "__main__":
    while True:
        question = input("\nYou: ")
        if question.lower() in ("quit", "exit"):
            break
        answer, steps = ask_agent(question)
        print("  🛠  tools used:", steps or "none")
        print("Agent:", answer)
