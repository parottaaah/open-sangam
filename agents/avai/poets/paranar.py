from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types

from ..config import get_model
from ..instructions import PARANAR_INSTRUCTION
from ..tools import search_verses, get_verse, get_tinai_context
from ..tools.image import generate_image

def _debug_log(msg):
    import time
    with open("paranar_debug.log", "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

_paranar_researcher = LlmAgent(
    name="_paranar_researcher",
    description="பாடல்களையும் திணைச் சூழல்களையும் திரட்டி விரிவான காட்சி விவரிப்பை (Image Prompt) உருவாக்கும் ஆராய்ச்சி முகவர்.",
    instruction=PARANAR_INSTRUCTION,
    model=get_model(),
    tools=[get_verse, search_verses, get_tinai_context]
)

from typing import AsyncGenerator
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event

class _DeterministicPainter(BaseAgent):
    name: str = "_paranar_painter"
    description: str = "ஓவியக் கருவியை நேரடியாக அழைத்துச் சித்திரங்களை உருவாக்கும் ஓவிய முகவர்."

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        _debug_log(">>> _DeterministicPainter._run_async_impl ENTERED")
        researcher_text = ""
        # Find the last text output from the researcher
        for event in reversed(ctx.session.events):
            if event.author == "_paranar_researcher" and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        researcher_text += part.text
                break
                
        if not researcher_text:
            researcher_text = "Beautiful Sangam landscape"
            
        try:
            image_result = generate_image(prompt=researcher_text, aspect_ratio="1:1")
            if image_result.image_data_uri:
                result_text = f"Here is the generated visualization:\n\n![Generated Image]({image_result.image_data_uri})\n\n*{image_result.disclaimer}*"
            else:
                result_text = f"Here is the visual scene description crafted for this verse:\n\n> {researcher_text}\n\n*{image_result.disclaimer} (Image rendering disabled — set SANGAM_IMAGE_BACKEND=gemini to render)*"
            content = types.Content(
                parts=[types.Part.from_text(text=result_text)],
                role="model"
            )
            _debug_log(f">>> _DeterministicPainter generated image result successfully, URI length: {len(image_result.image_data_uri) if image_result.image_data_uri else 'None'}")
        except Exception as e:
            _debug_log(f">>> _DeterministicPainter exception: {e}")
            content = types.Content(
                parts=[types.Part.from_text(text=f"Failed to generate image: {e}")],
                role="model"
            )
            
        _debug_log(">>> _DeterministicPainter YIELDING event")
        yield Event(author=self.name, content=content)

_paranar_painter = _DeterministicPainter()

class _ToolExposingSequentialAgent(SequentialAgent):
    """Wrapper to expose a dummy tools list so swarm.py can inject peer agent tools.
    We return a separate list rather than the sub-agent's tools to ensure peer-transfer
    tools are NOT added to the researcher, keeping the two-step extraction pipeline strictly deterministic."""
    
    _dummy_tools: list = []
    
    @property
    def tools(self):
        return self._dummy_tools
        
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        _debug_log(f">>> paranar_agent (_ToolExposingSequentialAgent) TRIGGERED with prompt: {ctx.user_content.parts[0].text if ctx.user_content and ctx.user_content.parts else 'No prompt'}")
        async for event in super()._run_async_impl(ctx):
            yield event
        _debug_log(">>> paranar_agent FINISHED")

paranar_agent = _ToolExposingSequentialAgent(
    name="paranar",
    description="பரணர் (Paranar) — சங்கப் பாடல்களின் காட்சிகளை மனக்கண் முன் கொண்டுவந்து ஓவியமாகக் காட்சிப்படுத்துபவர்.",
    sub_agents=[_paranar_researcher, _paranar_painter],
)

