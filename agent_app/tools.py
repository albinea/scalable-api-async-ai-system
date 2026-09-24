import os
import sqlite3
import random



from dotenv import load_dotenv
from langchain.tools import tool
from langchain_tavily import TavilySearch


load_dotenv()


# --------------------------------------------------
# 1. SEARCH TOOL
# --------------------------------------------------

tavily = TavilySearch(
    max_results=3
)


@tool
def search(query: str) -> str:
    """
    Search the web for up-to-date information.
    Use this when the user asks for current or external information.
    """

    result = tavily.invoke({
        "query": query
    })

    return str(result)


# --------------------------------------------------
# 2. CALCULATOR TOOL
# --------------------------------------------------

@tool
def calc(expression: str) -> str:
    """
    Calculate a mathematical expression.

    Example:
    100 * 1.18
    """

    try:
        # For a demo only.
        # In production use a safe mathematical parser.
        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return str(result)

    except Exception as exc:
        return f"CALC_ERROR: {exc}"


# --------------------------------------------------
# 3. DATABASE QUERY TOOL
# --------------------------------------------------

DATABASE = "business.db"


@tool
def db_query(query: str) -> str:
    """
    Query the customer database.

    Only SELECT queries are allowed.
    """

    if "FAIL_TEST" in query:
        raise RuntimeError(
            "Simulated database connection failure"
        )

    if not query.strip().lower().startswith("select"):
        return "DB_ERROR: Only SELECT queries are allowed."

    try:

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        connection.close()

        return str([
            dict(zip(columns, row))
            for row in rows
        ])

    except Exception as exc:

        return f"DB_ERROR: {exc}"


TOOLS = [
    search,
    calc,
    db_query,
]