from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from .reportee_data import reportee_tool
from .basic_emp_info import basic_info_tool

hr_basic_agent= LlmAgent(
    name="hr_basic_info_agent",
    model="gemini-2.5-flash",
    description=(
        "Fetches employee-related HR data. "
        "Returns factual, structured information only. "
        "Takes raw HR data and rephrases it into a clear, "
        "polite, conversational response for the end user."
    ),
    tools=[basic_info_tool]
)

hr_reportee_agent = LlmAgent(
    name="hr_reportee_agent",
    model="gemini-2.5-flash",
    description=(
        "Fetches employee-related HR data. "
        "Returns factual, structured information only. "
        "Takes raw HR data and rephrases it into a clear, "
        "polite, conversational response for the end user."
    ),
    tools=[reportee_tool]
)

hr_basic_agent_tool = AgentTool(agent=hr_basic_agent)
hr_reportee_agent_tool = AgentTool(agent=hr_reportee_agent)


hrms_chatbot_agent = LlmAgent(
    name="hrms_chatbot",
    model="gemini-2.5-flash",   # ✅ tool-capable
    description=(
        "You are an HRMS assistant. "
        "Answer employee HR-related questions such as leave, tax, overtime, "
        "reportee details, and general HR policy questions."
    ),
    tools=[
        hr_basic_agent_tool,
        hr_reportee_agent_tool
    ]
)

root_agent = hrms_chatbot_agent