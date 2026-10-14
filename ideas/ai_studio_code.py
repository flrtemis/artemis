# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemma-4-26b-a4b-it"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Hi"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Hi"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Hi"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""\"HiHiHi\"
The user is being energetic, friendly, or playful. It's a triple \"Hi,\" which suggests high enthusiasm.
Friendly, welcoming, and responsive.

    *   Acknowledge the energy.
    *   Match the tone (friendly/enthusiastic).
    *   Offer assistance.

    *   *Option 1 (Simple):* \"Hello! How can I help you today?\" (A bit too formal/dry).
    *   *Option 2 (Matching energy):* \"Hello! Hello! Hello! How's it going?\" (Better).
    *   *Option 3 (Playful):* \"Hi there! You seem energetic! How can I help you today?\" (Good).
    *   *Option 4 (Casual/Friendly):* \"Hi! Hi! Hi! What's up? How can I help you today?\" (Very natural).

    \"Hi! Hi! Hi! 👋 How's it going? How can I help you today?\""""),
                types.Part.from_text(text="""Hi! Hi! Hi! 👋

How are you doing today? Is there anything I can help you with?"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(code_execution=types.ToolCodeExecution),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MINIMAL",
        ),
        audio_transcription_config=types.AudioTranscriptionConfig(
        ),
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE",  # Block none
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE",  # Block none
            ),
        ],
        tools=tools,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            properties = {
                "response": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            },
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.parts is None
        ):
            continue
        if chunk.parts[0].text:
            print(chunk.parts[0].text, end="")
        if chunk.parts[0].executable_code:
            print(chunk.parts[0].executable_code)
        if chunk.parts[0].code_execution_result:
            print(chunk.parts[0].code_execution_result)

if __name__ == "__main__":
    generate()


