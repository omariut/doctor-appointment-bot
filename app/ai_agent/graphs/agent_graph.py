from app.ai_agent.prompts import chat_prompt
from app.ai_agent.tools import save_appointment, get_docs
from typing import List, Any, Optional, Dict
from langchain_core.messages import HumanMessage, trim_messages
from datetime import datetime
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from app.ai_agent.graphs.state import AgentState
from langchain_core.messages import get_buffer_string


class AppointmentGraph:

    def __init__(self, llm, qdrant):
        self.llm = llm
        self.qdrant = qdrant

    def _generate_response(self, chain, messages, state: dict) -> dict:
        # Load chat + doctors memory
        state_messages = state.get("messages", [])
        if state_messages[-1].type == "human":
            state_messages = state_messages[:-1]  # ignore the last message
        chat_history = get_buffer_string(state_messages[-20:])  # last 20 messages
        response = chain.invoke(
            {
                "user_message": messages,
                "today": state.get("today", datetime.now().strftime("%Y-%m-%d")),
                "chat_history": chat_history,
            }
        )
        return {
            "response": response,
            "messages": [response],
        }

    def response_with_tools_node(self, state: dict) -> dict:
        llm_with_tools = self.llm.bind_tools([save_appointment, get_docs])
        chain = chat_prompt | llm_with_tools
        # state["messages"] is a list; get the last message for user_message
        return self._generate_response(chain, [state["messages"][-1]], state)

    def response_without_tools_node(self, state: dict) -> dict:
        chain = chat_prompt | self.llm
        return self._generate_response(chain, [], state)

    def tool_node_condition(self, state: dict) -> bool:
        message = state["messages"][-1]
        if message.type == "tool":
            return "response_without_tools"
        else:
            return END

    def _add_nodes(self, graph: StateGraph):
        graph.add_node("response_with_tools", self.response_with_tools_node)
        graph.add_node("response_without_tools", self.response_without_tools_node)
        graph.add_node("tool_node", ToolNode([save_appointment, get_docs]))

    def _add_edges(self, graph: StateGraph):
        graph.add_edge(START, "response_with_tools")
        graph.add_edge("response_with_tools", "tool_node")
        graph.add_conditional_edges("tool_node", self.tool_node_condition)
        graph.add_edge("response_without_tools", END)

    def build_graph(self, checkpointer):
        graph = StateGraph(AgentState)
        self._add_nodes(graph)
        self._add_edges(graph)
        return graph.compile(checkpointer=checkpointer)
