# import os

# from dotenv import load_dotenv

# from langchain.agents import create_agent
# from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import (
#     HumanMessage,
#     AIMessage
# )

# from .tools import TOOLS
# from .memory import get_history


# load_dotenv()
# model = ChatOpenAI(
#     model="gpt-5.6-luna",
#     temperature=0,
# )


# # model = ChatOllama(
# #     temperature=0,
# #     model="qwen3.5:9b",
# #     base_url="http://host.docker.internal:11434",
# # )

# SYSTEM_PROMPT = """
# You are a helpful ReAct-style AI agent.

# You have access to three tools:

# 1. search
#    Use this for current or external information.

# 2. calc
#    Use this for mathematical calculations.

# 3. db_query
#    Use this to retrieve customer information from the database.

# Rules:

# - Think about which tool is appropriate.
# - Do not use search for mathematical calculations.
# - Do not use search when the answer can be obtained from db_query.
# - Use calc for calculations.
# - Use db_query for customer database information.
# - If a tool fails, analyze the error and retry using a corrected
#   tool call when possible.
# - Never expose internal tool errors to the user unless recovery
#   is impossible.
# """


# agent = create_agent(
#     model=model,
#     tools=TOOLS,
#     system_prompt=SYSTEM_PROMPT
# )


# def build_messages(session_id, user_message):

#     history = get_history(
#         session_id
#     )

#     messages = []

#     for item in history:

#         messages.append(
#             HumanMessage(
#                 content=item.user_message
#             )
#         )

#         messages.append(
#             AIMessage(
#                 content=item.assistant_message
#             )
#         )

#     messages.append(
#         HumanMessage(
#             content=user_message
#         )
#     )

#     return messages

# def extract_token_usage(result):

#     input_tokens = 0
#     output_tokens = 0
#     total_tokens = 0

#     messages = result.get(
#         "messages",
#         []
#     )

#     for message in messages:

#         usage = getattr(
#             message,
#             "usage_metadata",
#             None
#         )

#         if not usage:
#             continue

#         input_tokens += usage.get(
#             "input_tokens",
#             0
#         )

#         output_tokens += usage.get(
#             "output_tokens",
#             0
#         )

#         total_tokens += usage.get(
#             "total_tokens",
#             0
#         )

#     return {
#         "input_tokens": input_tokens,
#         "output_tokens": output_tokens,
#         "total_tokens": total_tokens
#     }

# from .memory import save_message


# def run_agent(
#     session_id: str,
#     user_message: str
# ):

#     messages = build_messages(
#         session_id,
#         user_message
#     )

#     result = agent.invoke(
#         {
#             "messages": messages
#         }
#     )
#     final_message = result["messages"][-1]

#     answer = final_message.content

#     usage = extract_token_usage(
#         result
#     )

#     # Example pricing.
#     # Replace with the pricing of your model.
#     input_cost = (
#         usage["input_tokens"] / 1_000_000
#     ) * 0.15

#     output_cost = (
#         usage["output_tokens"] / 1_000_000
#     ) * 0.60

#     total_cost = (
#         input_cost + output_cost
#     )

#     save_message(
#         session_id=session_id,
#         user_message=user_message,
#         assistant_message=answer
#     )

#     return {
#         "answer": answer,

#         "usage": {
#             **usage,
#             "estimated_cost_usd": round(
#                 total_cost,
#                 8
#             )
#         } 
#     }




from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

from .tools import TOOLS
from .memory import get_history, save_message


load_dotenv()

# Ollama Cloud model
model = ChatOllama(
    model="gpt-oss:120b-cloud",
    temperature=0,
    base_url="http://host.docker.internal:11434",
)


SYSTEM_PROMPT = """
You are a helpful ReAct-style AI agent.

You have access to three tools:

1. search
   Use this for current or external information.

2. calc
   Use this for mathematical calculations.

3. db_query
   Use this to retrieve customer information from the database.

Rules:

- Think about which tool is appropriate.
- Do not use search for mathematical calculations.
- Do not use search when the answer can be obtained from db_query.
- Use calc for calculations.
- Use db_query for customer database information.
- If a tool fails, analyze the error and retry using a corrected
  tool call when possible.
- Never expose internal tool errors to the user unless recovery
  is impossible.
"""


agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT
)


def build_messages(session_id, user_message):

    history = get_history(session_id)

    messages = []

    for item in history:
        messages.append(
            HumanMessage(content=item.user_message)
        )

        messages.append(
            AIMessage(content=item.assistant_message)
        )

    messages.append(
        HumanMessage(content=user_message)
    )

    return messages


def extract_token_usage(result):

    input_tokens = 0
    output_tokens = 0
    total_tokens = 0

    messages = result.get("messages", [])

    for message in messages:

        usage = getattr(
            message,
            "usage_metadata",
            None
        )

        if not usage:
            continue

        input_tokens += usage.get(
            "input_tokens",
            0
        )

        output_tokens += usage.get(
            "output_tokens",
            0
        )

        total_tokens += usage.get(
            "total_tokens",
            0
        )

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }


def run_agent(session_id: str, user_message: str):

    messages = build_messages(
        session_id,
        user_message
    )

    result = agent.invoke(
        {
            "messages": messages
        }
    )

    final_message = result["messages"][-1]

    answer = final_message.content

    usage = extract_token_usage(result)

    save_message(
        session_id=session_id,
        user_message=user_message,
        assistant_message=answer
    )

    return {
        "answer": answer,
        "usage": usage
    }