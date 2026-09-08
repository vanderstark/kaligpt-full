#!/usr/bin/env python3

# /agents/gemini.py
# KaliGPT Gemini_agent
# Updated: 14 apr 2026


from google import genai
from google.genai import types
import sys
import time

from .utils.parse_n_print_response import parse_n_print_response
from .utils.prompts import WEB_BUG_BOUNTY_AGENT as SYSTEM_PROMPT
from .utils.agent_configs import get_api_key, get_default_model, get_ai_specific_default_model
from .utils.tools import get_tools_info
from .utils.agent_management import agent_management, AI_MANAGEMENT_OPTIONS

# --- GLOBAL VARIABLES (with safe defaults) ---
GEMINI_API_KEY: str | None = None
GEMINI_MODEL: str | None = None
TOOLS_INFO: list = []
client = None
TOOL_FUNCTION_MAP: dict = {}

# Maximum tool-calling iterations to prevent infinite loops
MAX_TOOL_LOOPS = 5


def initialize_configs():
    global GEMINI_API_KEY, GEMINI_MODEL, client, TOOLS_INFO, TOOL_FUNCTION_MAP
    try:
        GEMINI_API_KEY = get_api_key("gemini")
        GEMINI_MODEL = get_ai_specific_default_model("gemini")

        if not GEMINI_API_KEY:
            print(f"[!] GEMINI API Key not Found. exiting!")
            sys.exit(0)

        # Configure the API for the entire library
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 2. LOAD TOOLS
        TOOLS_INFO = get_tools_info()

        # --- TOOL EXECUTION HELPER (Your Original Function) ---
        TOOL_FUNCTION_MAP = {func.__name__: func for func in TOOLS_INFO} if TOOLS_INFO else {}

        if not TOOLS_INFO:
            print("[!] No external tools loaded.")

    except Exception as e:
        print(f"Failed to initialize Agent: {e}")
        sys.exit(1)


def execute_function_calls(function_calls: list):
    response_parts = []
    print("\n[HackerX Tool Use] Owo! I found a tool I need to run! <3")
    for call in function_calls:
        func_name = call.name
        # Safely handle None or non-dict args
        func_args = dict(call.args) if call.args else {}
        if func_name in TOOL_FUNCTION_MAP:
            print(f"[HackerX Tool Use] Running tool: {func_name} with args: {func_args}")
            try:
                result_text = TOOL_FUNCTION_MAP[func_name](**func_args)
            except Exception as e:
                result_text = f"Tool execution failed with error: {e}"
        else:
            result_text = f"Tool {func_name} not found in map!"
        response_parts.append(
            types.Part.from_function_response(name=func_name, response={"result": result_text})
        )
        print(f"[HackerX Tool Use] Tool result ready to send back.")
    return response_parts


def get_gemini_response(history: list[types.Content], new_input: str, tools: list):
    """
    Generates content, including multi-turn tool calling logic, while correctly
    managing history and enabling Chain-of-Thought (CoT) via system_instruction.
    """

    # 1. Start the contents list by incorporating the entire history.
    #     The history contains all previous alternating user/model/tool turns.
    contents = history[:]

    # 2. Add the current user input as the new last message.
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=new_input)])
    )

    """ 
    3. Determine the system instruction for the current turn.
    The system instruction should only be passed once per request, but we pass it
    for EVERY request to ensure the model *always* has the persona and core rules.
    
    We use the full system instruction string here.
    """
    current_system_instruction = SYSTEM_PROMPT

    # --- The Multi-Turn Tool Loop ---
    loop_count = 0
    while loop_count < MAX_TOOL_LOOPS:
        loop_count += 1

        # 4. Call the Model with current contents and config
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=tools,
                thinking_config=types.ThinkingConfig(thinking_budget=1),
                system_instruction=current_system_instruction,
            ),
        )

        # After the first turn, don't re-send the instruction
        current_system_instruction = None

        # 5. Check for Function Calls (safe attribute access)
        if hasattr(response, "function_calls") and response.function_calls:

            function_calls = response.function_calls
            function_response_parts = execute_function_calls(function_calls)

            # Safely append candidate content
            if response.candidates and len(response.candidates) > 0:
                contents.append(response.candidates[0].content)
            else:
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text="(no content)")]))

            # Append the tool's result (FunctionResponse)
            contents.append(types.Content(role="tool", parts=function_response_parts))

            time.sleep(0.5)
            continue

        # 6. No Function Call -> Final Text Response
        else:
            # Safely append final model response
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            new_history = contents

            # response.text may be None when model only returns tool calls
            return (response.text or ""), new_history

    # If we exhausted max loops, return what we have
    print(f"[!] Warning: Reached maximum tool call limit ({MAX_TOOL_LOOPS})")
    return (response.text or ""), contents


def main(prompt=None):
    chat_history: list[types.Content] = []

    initialize_configs()   # initialize configs for gemini

    print(f"㉿ HackerX ( Gemini/{GEMINI_MODEL} )")
    while True:
        try:
            if prompt is None:
                prompt = input("\nYou ➤ ")


            if prompt.lower().replace("-", " ").strip() in AI_MANAGEMENT_OPTIONS:
                agent_management(prompt.lower().replace("-", " ").strip())
                prompt = None
                continue

            gemini_response, chat_history = get_gemini_response(
                history=chat_history,
                new_input=prompt,
                tools=TOOLS_INFO
            )

            parse_n_print_response(gemini_response)
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
