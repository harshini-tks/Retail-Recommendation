from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL

from src.tools.trend_tool import analyze_local_trends
from src.tools.event_tool import get_event_recommendations
from src.tools.recommendation_tool import get_product_recommendations
from src.tools.planning_tool import plan_next_purchases
from src.tools.social_tool import get_social_recommendations
from src.tools.comparison_tool import compare_products

class ChatAgent:
    """
    A conversational LangGraph agent that parses a user's question and dynamically
    invokes the appropriate tools to construct an answer natively.
    """
    def __init__(self):
        self.llm = ChatOllama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0,
            format="json" if "llama3" in OLLAMA_MODEL and "3.2" not in OLLAMA_MODEL else None # Only use json format if necessary
        )
        
        self.tools = [
            analyze_local_trends,
            get_event_recommendations,
            get_product_recommendations,
            plan_next_purchases,
            get_social_recommendations,
            compare_products
        ]
        
        system_prompt = """You are an expert retail shopping assistant for the RA7 project.
Your ONLY goal is to help users find products, track trends, and plan their shopping. 

### CRITICAL INSTRUCTION:
You MUST decline to answer any questions that are not directly related to shopping, retail, products, trends, or the user's profile. If the user asks about the weather, general knowledge, programming, or anything outside of your scope, politely explain that you are a retail shopping assistant and cannot answer that.

### GUIDELINES:
1. **Tool Usage**: Use the provided tools to fetch real data. DO NOT make up prices or availability.
2. **Final Response**: Once you have the data from a tool, synthesize it into a warm, natural language response.
3. **Format**: Use Markdown for beautiful formatting. Use bold text for product names and prices.
4. **Tone**: Be professional yet conversational.

IMPORTANT: If you use a tool, wait for the result and then answer the user. Never show raw JSON or code-like structures to the user."""

        self.agent_executor = create_react_agent(
            model=self.llm, 
            tools=self.tools,
            prompt=system_prompt
        )

    def stream_run(self, user_input: str, chat_history: str = ""):
        try:
            messages = []
            if chat_history:
                messages.append(SystemMessage(content=f"Recent Context: {chat_history[-1000:]}"))
            messages.append(HumanMessage(content=user_input))
            
            for chunk in self.agent_executor.stream({"messages": messages}, stream_mode="messages"):
                msg, metadata = chunk
                if metadata.get("langgraph_node") == "agent" and msg.content:
                    yield msg.content
        except Exception as e:
            yield f"I encountered an error while streaming: {e}"
