"""கபிலர் (Kapilar) — Search/Retrieval agent, M1 issue #4.

Answers queries by retrieving and ranking Sangam verses, grounded in the corpus
tools, with a focus on Kurinji tiṇai and nature imagery.
"""

from google.adk.agents import LlmAgent

from ..config import get_model
from ..instructions import KAPILAR_INSTRUCTION
from ..tools import find_parallel_verses, get_tinai_context, get_verse, search_verses

kapilar_agent = LlmAgent(
    name="kapilar",
    model=get_model(),
    description="கபிலர் (Kapilar) — தேடல் வினாக்களுக்கு ஏற்பப் பொருத்தமான சங்கப் பாடல்களைத் தேடி மீட்டெடுத்து வரிசைப்படுத்தித் தருபவர்.",
    instruction=KAPILAR_INSTRUCTION,
    tools=[get_verse, search_verses, get_tinai_context, find_parallel_verses],
)


