#!/usr/bin/env python3

# kaligpt Ollama Agent
# /agent/ollama_.py
# Updated: 23 March 2026


import sys

from ollama import Client

from .utils.parse_n_print_response import parse_n_print_response
from .utils.prompts import WEB_BUG_BOUNTY_AGENT as SYSTEM_PROMPT
from .utils.agent_configs import get_ai_specific_default_model, get_api_key
from .utils.tools import get_tools_info
from .utils.agent_management import AI_MANAGEMENT_OPTIONS, agent_management
from .utils.openai_tool_adapter import openai_tool_adapter
from .utils.ollama_tool_think_support_check import model_support_check


# --- GLOBAL VARIABLES ---
OLLAMA_API_URL: str   # OLLAMA API URL as OLLAMA_API_KEY
OLLAMA_MODEL: str
TOOLS_INFO: list
TOOL_FUNCTION_MAP: dict
client: Client
SUPPORT_STAGE: int


def initialize_agent():
    global SUPPORT_STAGE, OLLAMA_API_URL
    global OLLAMA_MODEL
    OLLAMA_MODEL = get_ai_specific_default_model("ollama")

    # Check Models for Tools & thinking support and specify SUPPORT_STAGE based on that
    OLLAMA_API_URL = get_api_key("ollama")

    SUPPORT_STAGE = model_support_check(OLLAMA_MODEL, OLLAMA_API_URL)


def initialize_configs():
    global OLLAMA_API_URL, TOOLS_INFO, TOOL_FUNCTION_MAP, client
    try:
        OLLAMA_API_URL = get_api_key("ollama")

        initialize_agent()

        # initialize ollama AsyncClient
        client = Client(host=OLLAMA_API_URL)

        tools = get_tools_info()
        TOOLS_INFO = [openai_tool_adapter(f) for f in tools]

        if not TOOLS_INFO:
            print("[!] No external tools loaded.")

        # --- TOOL EXECUTION HELPER (Your Original Function) ---
        TOOL_FUNCTION_MAP = {func.__name__: func for func in tools} if tools else {}


    except Exception as e:
        print(f"Failed to initialize Ollama Agent: {e}\n[!] OLLAMA_API_URL may be misconfigured or unreachable.")
        sys.exit(1)


MAX_TURNS = 6   # user+assistant pairs

def trim_history(history):
    """ Trim chat history to keep within MAX_TURNS """
    system = [m for m in history if m["role"] == "system"]
    rest = [m for m in history if m["role"] != "system"]
    return system + rest[-MAX_TURNS * 2:]


def execute_function_calls(function_calls):
    response_parts = []

    for call in function_calls:
        func_name = call.function.name
        func_args = dict(call.function.arguments)

        print(f"\n[HackerX Tool Use] name: {func_name}, args: {func_args}")

        if func_name in TOOL_FUNCTION_MAP:
            try:
                result_text = TOOL_FUNCTION_MAP[func_name](**func_args)
            except Exception as e:
                result_text = f"Tool execution failed with error: {e}"
        else:
            result_text = f"Tool {func_name} not found!"

        response_parts.append({
                "name": func_name,
                "result": str(result_text)
            })

    return response_parts


def request_resp(messages, tools):

    match SUPPORT_STAGE:
        case 0:
            # No thinking & tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
            )
            return response

        case 1:
            # Thinking supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                think=True,
            )
            return response

        case 2:
            # tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
            )
            return response

        case _:
            # Both Thinking and Tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
                think=True,
            )
            return response


def ask(user_input, history, tools):
    """Ask Ollama Models for Response based on Support Stage

        Stage   Description
        0       Not Supports both Tool & Thinking
        1       Supports Thinking
        2       Supports Tools
        3       Supports Both Tools & Thinking.
    """

    messages = trim_history(history) + [{"role": "user", "content": user_input}]
    full_content: str

    while True:
        try:
            response = request_resp(messages=messages, tools=tools)

            tool_calls = []
            full_content = ""

            if response.message.content:
                # print(chunk.message.content, end="", flush=True)
                full_content += response.message.content
            if response.message.tool_calls:
                tool_calls.extend(response.message.tool_calls)

            # Append full assistant message to history
            messages.append({
                "role": "assistant",
                "content": full_content,
                "tool_calls": tool_calls
            })

            if tool_calls:
                tool_results = execute_function_calls(tool_calls)
                messages.append({
                    "role": "tool",
                    "content": str(tool_results)
                })
            else:
                break

        except Exception as e:
            print(f"[!] Error: {e}")
            sys.exit(1)

    return full_content, messages


def main(prompt=None):

    # Initialize chat history with system prompt
    chat_history: list = [{"role": "system", "content": SYSTEM_PROMPT}]

    initialize_configs()   # initialize configs for Ollama

    # Print tool banner
    print(f"㉿ HackerX ( ollama/{OLLAMA_MODEL} )")
    while True:
        try:
            if prompt is None:
                prompt = str(input("\nYou ➤ "))

            if prompt.lower().replace("-", " ").strip() in AI_MANAGEMENT_OPTIONS:
                agent_management(prompt.lower().replace("-", " ").strip())
                initialize_agent()
                prompt = None
                continue

            response, chat_history = ask(
                history=chat_history,
                user_input=prompt,
                tools=TOOLS_INFO
            )

            parse_n_print_response(response)
            prompt = None

        except KeyboardInterrupt:
            print("\n   Exiting HackerX. See you later!")
            break

        except Exception as err:
            print(f"\n[!] An error occurred: {err}")
            break

if __name__ == "__main__":

    if len(sys.argv) > 1:
        args = ' '.join(sys.argv[1:])
        main(args)
    else:
        main()
