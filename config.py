########  GENERAL APP INFORMATION  ##############

APP_TITLE = "Ebola Virus Ecology and Transmission (AI Assistants Template)"
APP_INTRO = """This is a simple app that assesses the user's understanding of a simple case study. It is for demonstrating the capabilities of a AI MicroApp. 

"""

APP_HOW_IT_WORKS = """
            This is an **AI-Tutored Rubric exercise** that acts as a tutor guiding a student through a shared asset, like an article. It uses the OpenAI Assistants API with GPT-4. The **questions and rubric** are defined by a **faculty**. The **feedback and the score** are generarated by the **AI**. 

It can:

1. provide feedback on a student's answers to questions about an asset
2. roughly "score" a student to determine if they can move on to the next section.  

Scoring is based on a faculty-defined rubric on the backend. These rubrics can be simple (i.e. "full points if the student gives a thoughtful answer") or specific with different criteria and point thresholds. The faculty also defines a minimum pass threshold for each question. The threshold could be as low as zero points to pass any answer, or it could be higher. 

Using AI to provide feedback and score like this is a very experimental process. Some things to note: 

 - AIs make mistakes. Users are encourage to skip a question if the AI is not understanding them or giving good feedback. 
 - The AI might say things that it can't do, like "Ask me anything about the article". I presume further refinement can reduce these kinds of responses. 
 - Scoring is highly experimental. At this point, it should mainly be used to gauge if a user gave an approximately close answer to what the rubric suggests. It is not recommended to show the user the numeric score. 

 """

SHARED_ASSET = {
    "name":"Ebola Poster",
    "path":"cdc_ebola_poster.pdf",
    "button_text":"Read PDF"
}

HTML_BUTTON = {}

COMPLETION_MESSAGE = "You've reached the end! I hope you learned something!"
COMPLETION_CELEBRATION = False

SCORING_DEBUG_MODE = True

 ####### PHASES INFORMATION #########

PHASES = {
    "about": {
        "type": "text_area",
        "height": 200,
        "label": """What is this case study about?""",
        "instructions": """The user will summarize the shared case study. Please critically review their response for accuracy. You will give them credit for mentioning Ebola, and you will be very pleased if they mention it is about Ebola with any other relevant details.""",
        "value": "The case study is about Ebola, and how it can be transmitted from animals to humans (a spillover event), humans to humans. It also includes details on how to support survivors returning to the community. ",
        "scored_phase": True,
        "rubric": """
            1. About
                2 points - The user provides details that the case study is about Ebola and its transmission. 
                1 point - The user mentions the case study is about Ebola, but provides no further details. 
                0 points - The user does not accurately describe the shared case study. 
        """,
        "minimum_score": 2
    },
    "spillover": {
        "type": "text_area",
        "height": 300,
        "label": """Describe a spillover event and how one might occur.""",
        "button_label": "Submit",
        "value": "A spillover event is when a virus jumps from one species to another, like from a bat to a monkey, or a monkey to a human. This occurs through direct contact with contaminated meat like eating an infected carcass or preparing raw meat.",
        "scored_phase": True,
        "instructions": """ The user will describe a spillover event in the context of this shared document and how one might happen. Critically assess whether the user has accurately defined a spillover event and provided true examples for how one might happen. Provide feedback on their answer. If relevant, add further examples of how a spillover event might happen. 
        """,
        "rubric": """
                1. Definition
                    1 point - The response accurately defines a spillover event
                    0 points - The response does not accurately define a spillover event.
                2. Examples
                    1 point - The response provides one or more plausible examples of how a spillover event might occur. 
                    0 points - The response does not provide any plausible examples of how a spillover event might occur. 
        """,
        "minimum_score": 2,
        "user_input": "",
        "ai_response": "",
        "allow_skip": True
    },
    "survivors": {
       "type": "text_area",
       "height": 300,
       "label": "Imagine you are a public health worker in an area affected by Ebola. How might you ease the transition for survivors as they re-enter their communities?",
       "value":"Survivors could be supported by providing them leave as they manage their symptoms. Also by providing education to the community about the safety and struggles of survivors. Maybe a support group of survivors and supporters, too?",
       "instructions": """The user will hypothesize about ways to support survivors as they re-enter the community. Critically evaluate their response to determine if they understand and have made a valid attempt to answer the question. If so, be supportive of their answer and their work on this exercise. 
        """,   
       "scored_phase": False,
       "user_input": "",
       "allow_skip": True
    },
    # "reflect": {
    #    "type": "text_area",
    #    "height": 100,
    #    "label": "Now, please reflect on this exercise",
    #    "button_label": "Finish",
    #    "value":"I think I did well on this exercise and I'm glad that I got immediate feedback. ",
    #    "instructions": """The user is reflecting on their experience. Acknowledge their reflection.
    #     """,   
    #    "scored_phase": True,
    #    "rubric": """
    #            1. Correctness
    #                1 point - The user has added an appropriate reflection
    #                0 points - The user has not added an appropriate reflection
    #            """,
    #    "minimum_score": 1,
    #    "user_input": "",
    #    "ai_response": "",
    #    "allow_skip": True

    # #Add more steps as needed
    # },
    # "short_text": {
    #    "type": "text_input",
    #    "label": "Here is a question that requires a short text response",
    #    "instructions": "Tell the AI what to do here...",
    #    "scored_phase": False,
    #    "rubric": """
    #       1. Criteria 1
    #            2 points - Requirements to receive 2 points
    #            1 point - Requirements to receive 1 point
    #            0 points - Requirements to receive 0 points
    #       """,
    #    "minimum_score": 1,
    #    "allow_skip": True
    # },
    # "long_text": {
    #    "type": "text_area",
    #    "height": 100,
    #    "label": "Here is a question that requires a long text response",
    #    "instructions": "Tell the AI what to do here...",
    #    "scored_phase": False,
    #    "rubric": """
    #       1. Criteria 1
    #            2 points - Requirements to receive 2 points
    #            1 point - Requirements to receive 1 point
    #            0 points - Requirements to receive 0 points
    #       """,
    #    "minimum_score": 1,
    #    "allow_skip": True
    # },
    # "selection": {
    #    "type": "selectbox",
    #    "options": ['Option 1', 'Option 2', 'Option 3'],
    #    "label": "Here is a question that asks a user to choose one from a list of options",
    #    "instructions": "Tell the AI what to do here...",
    #    "scored_phase": False,
    #    "rubric": """
    #       1. Criteria 1
    #            2 points - Requirements to receive 2 points
    #            1 point - Requirements to receive 1 point
    #            0 points - Requirements to receive 0 points
    #       """,
    #    "minimum_score": 1,
    #    "allow_skip": True
    # },
    # "radio": {
    #    "type": "radio",
    #    "options": ['Option 1', 'Option 2', 'Option 3'],
    #    "label": "Here is a question that asks a user to choose one from a list of radio options",
    #    "instructions": "Tell the AI what to do here...",
    #    "scored_phase": False,
    #    "rubric": """
    #       1. Criteria 1
    #            2 points - Requirements to receive 2 points
    #            1 point - Requirements to receive 1 point
    #            0 points - Requirements to receive 0 points
    #       """,
    #    "minimum_score": 1,
    #    "allow_skip": True
    # }

}

######## AI CONFIGURATION #############

########## AI ASSISTANT CONFIGURATION #######
ASSISTANT_NAME = "Case Study Tutor"
ASSISTANT_INSTRUCTIONS = """
You are providing feedback on a user's understanding of a shared case study about Ebola. The case study has been uploaded to the file search for shared reference by you and the student.  """


LLM_CONFIGURATION = {
    "gpt-4-turbo":{
        "name":ASSISTANT_NAME,
        "instructions": ASSISTANT_INSTRUCTIONS,
        "tools":[{"type":"file_search"}],
        "model":"gpt-4-turbo",
        "temperature":0,
        "price_per_1k_prompt_tokens":.01,
        "price_per_1k_completion_tokens": .03
    },
    "gpt-4o":{
        "name":ASSISTANT_NAME,
        "instructions": ASSISTANT_INSTRUCTIONS,
        "tools":[{"type":"file_search"}],
        "model":"gpt-4o",
        "temperature":0,
        "price_per_1k_prompt_tokens":.005,
        "price_per_1k_completion_tokens": .015
    },
    "gpt-3.5-turbo":{
        "name":ASSISTANT_NAME,
        "instructions": ASSISTANT_INSTRUCTIONS,
        "tools":[{"type":"file_search"}],
        "model":"gpt-3.5-turbo-0125",
        "temperature":0,
        "price_per_1k_prompt_tokens":0.0005,
        "price_per_1k_completion_tokens": 0.0015
    }
}


ASSISTANT_THREAD = ""
ASSISTANT_ID_FILE = "assistant_id.txt"