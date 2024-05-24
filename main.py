import openai
import os
from dotenv import find_dotenv, load_dotenv
import json
import re
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.let_it_rain import rain
from contextlib import nullcontext
import openai
from config import *

load_dotenv(override=True)
client = openai.OpenAI()

function_map = {
    "text_input": st.text_input,
    "text_area": st.text_area,
    "warning": st.warning,
    "button": st.button,
    "radio": st.radio,
    "markdown": st.markdown,
    "selectbox": st.selectbox
}

user_input = {}


def build_field(i, phases_dict):
    phase_name = list(phases_dict.keys())[i]
    phase_dict = list(phases_dict.values())[i]
    field_type = phase_dict.get("type", "")
    field_label = phase_dict.get("label", "")
    field_body = phase_dict.get("body", "")
    field_value = phase_dict.get("value", "")
    field_max_chars = phase_dict.get("max_chars", None)
    field_help = phase_dict.get("help", "")
    field_on_click = phase_dict.get("on_click", None)
    field_options = phase_dict.get("options", [])
    field_horizontal = phase_dict.get("horizontal", False)
    field_height = phase_dict.get("height", None)
    field_unsafe_html = phase_dict.get("unsafe_allow_html", False)
    field_placeholder = phase_dict.get("placeholder", "")

    kwargs = {}
    if field_label:
        kwargs['label'] = field_label
    if field_body:
        kwargs['body'] = field_body
    if field_value:
        kwargs['value'] = field_value
    if field_options:
        kwargs['options'] = field_options
    if field_max_chars:
        kwargs['max_chars'] = field_max_chars
    if field_help:
        kwargs['help'] = field_help
    if field_on_click:
        kwargs['on_click'] = field_on_click
    if field_horizontal:
        kwargs['horizontal'] = field_horizontal
    if field_height:
        kwargs['height'] = field_height
    if field_unsafe_html:
        kwargs['unsafe_allow_html'] = field_unsafe_html
    if field_placeholder:
        kwargs['placeholder'] = field_placeholder

    key = f"{phase_name}_phase_status"

    # If the user has already answered this question:
    if key in st.session_state and st.session_state[key]:
        # Write their answer
        if f"{phase_name}_user_input" in st.session_state:
            if field_type != "selectbox":
                kwargs['value'] = st.session_state[f"{phase_name}_user_input"]
            kwargs['disabled'] = True

    my_input_function = function_map[field_type]

    with stylable_container(
            key="large_label",
            css_styles="""
            label p {
                font-weight: bold;
                font-size: 28px;
            }
            """,
    ):

        user_input[phase_name] = my_input_function(**kwargs)


class AssistantManager:
    assistant_id = None
    thread_id = None
    llm_configuration = LLM_CONFIGURATION["gpt-4o"]

    def __init__(self):
        self.client = openai
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        self.load_assistant_id()
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                id=AssistantManager.thread_id
            )

    def load_assistant_id(self):
        try:
            with open(ASSISTANT_ID_FILE, 'r') as file:
                AssistantManager.assistant_id = file.read().strip()
        except FileNotFoundError:
            AssistantManager.assistant_id = None

    def save_assistant_id(self, assistant_id):
        with open(ASSISTANT_ID_FILE, 'w') as file:
            file.write(assistant_id)

    def create_assistant(self):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=AssistantManager.llm_configuration["name"],
                instructions=AssistantManager.llm_configuration["instructions"],
                tools=AssistantManager.llm_configuration["tools"],
                model=AssistantManager.llm_configuration["model"]
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            self.save_assistant_id(assistant_obj.id)
            st.session_state["assistant_id"] = assistant_obj.id

    def create_thread(self):
        if not self.thread:
            if st.session_state.thread_obj:
                print(f"Grabbing existing thread...")
                thread_obj = st.session_state.thread_obj
            else:
                print(f"Creating and saving new thread")
                thread_obj = self.client.beta.threads.create()
                st.session_state.thread_obj = thread_obj

            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID::: {self.thread.id}")
        else:
            print(f"A thread already exists: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    def run_assistant(self, instructions, current_phase, scoring_run=False):
        if self.thread and self.assistant:
            if not scoring_run or (scoring_run and SCORING_DEBUG_MODE):
                res_box = st.info(body="", icon="🤖")
            report = []

            stream = self.client.beta.threads.runs.create(
                assistant_id=self.assistant.id,
                thread_id=self.thread.id,
                instructions=instructions,
                temperature=AssistantManager.llm_configuration["temperature"],
                stream=True
            )

            context_manager = st.spinner('Checking Score...') if scoring_run else nullcontext()

            result = ""
            run_id = None

            with context_manager:
                for event in stream:
                    if event.data.object == "thread.message.delta":
                        # Iterate over content in the delta
                        for content in event.data.delta.content:
                            if content.type == 'text':
                                # Print the value field from text deltas
                                report.append(content.text.value)
                                result = "".join(report).strip()
                                if scoring_run == False:
                                    res_box.info(body=f'{result}', icon="🤖")
                                if scoring_run and SCORING_DEBUG_MODE:
                                    res_box.info(body=f'SCORE (DEBUG MODE): {result}', icon="🤖")
            if not run_id:
                run_id = event.data.id

            # Retrieve the run object to get the usage information
            run = self.client.beta.threads.runs.retrieve(run_id=run_id, thread_id=self.thread.id)


            if not scoring_run:
                st_store(result, current_phase, "ai_response")
            else:
                st_store(result, current_phase, "ai_result")
                score = extract_score(result)
                st_store(score, current_phase, "ai_score")
                st.write(f"Extracted score for {current_phase}: {score}")

            # Extract token usage information from the run object
            if 'COMPLETION_TOKENS' not in st.session_state:
                st.session_state['COMPLETION_TOKENS'] = run.usage.completion_tokens
            else:
                st.session_state['COMPLETION_TOKENS'] += run.usage.completion_tokens

            if 'PROMPT_TOKENS' not in st.session_state:
                st.session_state['PROMPT_TOKENS'] = run.usage.prompt_tokens
            else:
                st.session_state['PROMPT_TOKENS'] += run.usage.prompt_tokens

            # Calculate the cost
            prompt_tokens = st.session_state['PROMPT_TOKENS']
            completion_tokens = st.session_state['COMPLETION_TOKENS']
            thread_cost = self.calculate_cost(prompt_tokens, completion_tokens)
            #if 'TOTAL_COST' not in st.session_state:
            #    st.session_state['TOTAL_COST'] = 0
            st.session_state['TOTAL_COST'] = thread_cost

    def calculate_cost(self, prompt_tokens, completion_tokens):
        price_per_1k_prompt_tokens = AssistantManager.llm_configuration["price_per_1k_prompt_tokens"]  
        price_per_1k_completion_tokens = AssistantManager.llm_configuration["price_per_1k_completion_tokens"]  
        total_cost = ((prompt_tokens / 1000) * price_per_1k_prompt_tokens) + ((completion_tokens / 1000) * price_per_1k_completion_tokens)
        return total_cost


def st_store(input, phase_name, phase_key):
    key = f"{phase_name}_{phase_key}"
    # if key not in st.session_state:
    st.session_state[key] = input


def build_scoring_instructions(rubric):
    scoring_instructions = """Please score the user's previous response based on the following rubric: \n """
    scoring_instructions += rubric
    scoring_instructions += """\n\nPlease output your response as JSON, using this format: { "[criteria 1]": "[score 1]", "[criteria 2]": "[score 2]", "total": "[total score]" }"""
    return scoring_instructions


def extract_score(text):
    # Define the regular expression pattern
    # regex has been modified to grab the total value whether or not it is returned inside double quotes. The AI seems to fluctuate between using quotes around values and not.
    pattern = r'"total":\s*"?(\d+)"?'

    # Use regex to find the score pattern in the text
    match = re.search(pattern, text)

    # If a match is found, return the score, otherwise return None
    if match:
        return int(match.group(1))
    else:
        return 0


def check_score(PHASE_NAME):
    score = st.session_state[f"{PHASE_NAME}_ai_score"]
    try:
        if score >= PHASES[PHASE_NAME]["minimum_score"]:
            st.session_state[f"{PHASE_NAME}_phase_status"] = True
            return True
        else:
            st.session_state[f"{PHASE_NAME}_phase_status"] = False
            return False
    except:
        st.session_state[f"{PHASE_NAME}_phase_status"] = False
        return False


def skip_phase(PHASE_NAME, No_Submit=False):
    st_store(user_input[PHASE_NAME], PHASE_NAME, "user_input")
    if No_Submit == False:
        st.session_state[f"{PHASE_NAME}_ai_response"] = "This phase was skipped."
    st.session_state[f"{PHASE_NAME}_phase_status"] = True
    st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)


def celebration():
    rain(
        emoji="🥳",
        font_size=54,
        falling_speed=5,
        animation_length=1,
    )


def main():
    global ASSISTANT_ID

    if 'CURRENT_PHASE' not in st.session_state:
        st.session_state.thread_obj = []

    st.title(APP_TITLE)
    st.markdown(APP_INTRO)

    if APP_HOW_IT_WORKS:
        with st.expander("Learn how this works", expanded=False):
            st.markdown(APP_HOW_IT_WORKS)

    if SHARED_ASSET:
        # Download button for the PDF
        with open(SHARED_ASSET["path"], "rb") as asset_file:
            st.download_button(label=SHARED_ASSET["button_text"],
                               data=asset_file,
                               file_name=SHARED_ASSET["name"],
                               mime="application/octet-stream")

    if HTML_BUTTON:
        st.link_button(label=HTML_BUTTON["button_text"], url=HTML_BUTTON["url"])

    # Create the assistant one time. Only if the Assistant ID is not found, create a new one.
    openai_assistant = AssistantManager()

    # Run the create_assistant. It only creates a new assistant if one is not found.
    openai_assistant.create_assistant()

    # Create a thread, or retrieve the existing thread if it exists in local Storage.
    openai_assistant.create_thread()

    i = 0

    # Create a variable for the current phase, starting at 0
    if 'CURRENT_PHASE' not in st.session_state:
        st.session_state['CURRENT_PHASE'] = 0

    # Loop until you reach the currently active phase.
    while i <= st.session_state['CURRENT_PHASE']:
        submit_button = False
        skip_button = False
        final_phase_name = list(PHASES.keys())[-1]
        final_key = f"{final_phase_name}_ai_response"

        # Build the field, according to the values in the PHASES dictionary
        build_field(i, PHASES)
        # Store the Name of the Phase and the values for that Phase
        PHASE_NAME = list(PHASES.keys())[i]
        PHASE_DICT = list(PHASES.values())[i]

        key = f"{PHASE_NAME}_phase_status"

        # Check phase status to automatically continue if it's a markdown phase
        if PHASE_DICT["type"] == "markdown":
            if key not in st.session_state:
                st.session_state[key] = True
                st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)

        if key not in st.session_state:
            st.session_state[key] = False
        # If the phase isn't passed and it isn't a recap of the final phase, then give the user a submit button
        if st.session_state[key] != True and final_key not in st.session_state:
            with st.container(border=False):
                col1, col2 = st.columns(2)
                with col1:
                    submit_button = st.button(label=PHASE_DICT.get("button_label", "Submit"), type="primary",
                                              key="submit " + str(i))
                with col2:
                    if PHASE_DICT.get("allow_skip", False):
                        skip_button = st.button(label="Skip Question", key="skip " + str(i))

        # If the phase has user input:
        key = f"{PHASE_NAME}_user_input"
        if key in st.session_state:
            # Then try to print the stored AI Response
            key = f"{PHASE_NAME}_ai_response"
            # If the AI has responded:
            if key in st.session_state:
                # Then print the stored AI Response
                st.info(st.session_state[key], icon="🤖")
            key = f"{PHASE_NAME}_ai_result"
            # If we are showing a score:
            if key in st.session_state and SCORING_DEBUG_MODE == True:
                # Then print the stored AI Response
                st.info(st.session_state[key], icon="🤖")

        if submit_button:
            # Add INSTRUCTIONS message to the thread
            openai_assistant.add_message_to_thread(
                role="assistant",
                content=PHASE_DICT.get("instructions", "")
            )
            # Store the users input in a session variable
            st_store(user_input[PHASE_NAME], PHASE_NAME, "user_input")
            # Add USER MESSAGE to the thread
            openai_assistant.add_message_to_thread(
                role="user",
                content=user_input[PHASE_NAME]
            )
            # Currently, all instructions are handled in the system prompts, so no need to add additional instructions here.
            instructions = ""
            # Run the thread
            openai_assistant.run_assistant(instructions, PHASE_NAME)


            if PHASE_DICT.get("scored_phase", "") == True:
                if "rubric" in PHASE_DICT:
                    scoring_instructions = build_scoring_instructions(PHASE_DICT["rubric"])
                    openai_assistant.add_message_to_thread(
                        role="assistant",
                        content=scoring_instructions,
                    )
                    openai_assistant.run_assistant(instructions, PHASE_NAME, True)
                    if check_score(PHASE_NAME):
                        st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)
                        # Rerun Streamlit to refresh the page
                        st.rerun()
                    else:
                        st.warning("You haven't passed. Please try again.")
                else:
                    st.error('You need to include a rubric for a scored phase', icon="🚨")
            else:
                st.session_state[f"{PHASE_NAME}_phase_status"] = True
                st.session_state['CURRENT_PHASE'] = min(st.session_state['CURRENT_PHASE'] + 1, len(PHASES) - 1)
                # Rerun Streamlit to refresh the page
                st.rerun()



        if skip_button:
            skip_phase(PHASE_NAME)
            st.rerun()

        if final_key in st.session_state and i == st.session_state['CURRENT_PHASE']:
            st.success(COMPLETION_MESSAGE)
            if COMPLETION_CELEBRATION:
                celebration()


        # Increment i, but never more than the number of possible phases
        i = min(i + 1, len(PHASES))

    if 'TOTAL_COST' in st.session_state:
        st.markdown(f"<span style='font-size: .8em; font-style: italic;'>:dollar: Cost: ${st.session_state['TOTAL_COST']}</span>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()