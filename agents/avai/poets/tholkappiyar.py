"""தொல்காப்பியர் (Tholkappiyar) — Scenario extraction specialist."""

from google.adk.agents import LlmAgent, SequentialAgent

from ..config import get_model
from ..instructions import THOLKAPPIYAR_INSTRUCTION
from ..tools import analyze_prosody, get_colophon_metadata, get_tinai_context, get_verse, search_verses
from ..schemas import Scenario
from ..tools import (
    get_tinai_context,
    get_verse,
    list_poems,
    query_knowledge_graph,
    search_verses,
)

_tholkappiyar_researcher = LlmAgent(
    name="_tholkappiyar_researcher",
    model=get_model(),
    description="பாடல்களையும் திணைச் சூழல்களையும் திரட்டும் ஆராய்ச்சி முகவர்.",
    instruction=THOLKAPPIYAR_INSTRUCTION,
    tools=[get_verse, search_verses, get_tinai_context, analyze_prosody, get_colophon_metadata],
)


_tholkappiyar_formatter = LlmAgent(
    name="_tholkappiyar_formatter",
    model=get_model(),
    description="கட்டமைக்கப்பட்ட JSON வடிவத்தில் அக/புற சூழலை வெளிப்படுத்தும் முகவர்.",
    instruction="Format the findings into the requested JSON schema. Do not add any conversational text.",
    output_schema=Scenario,
)

class _ToolExposingSequentialAgent(SequentialAgent):
    """Wrapper to expose dummy tools list so swarm.py can inject peer agent tools."""
    
    _dummy_tools: list = []
    
    @property
    def tools(self):
        return self._dummy_tools

tholkappiyar_agent = _ToolExposingSequentialAgent(
    name="tholkappiyar",
    description="தொல்காப்பியர் (Tholkappiyar) — சங்க இலக்கிய இலக்கண ஆசிரியர்; பாடல்களிலிருந்து அக/புறச் சூழல்களைத் திட்டமிட்டுக் கட்டமைத்துப் பிரித்தெடுப்பவர்.",
    sub_agents=[_tholkappiyar_researcher, _tholkappiyar_formatter],
)

