from langgraph.graph import StateGraph, END
from schemas.agent_state_schema import ChatState
from agents.router_agent import run_router_agent
from agents.answer_agent import run_answer_agent

def router_node(state: ChatState) -> ChatState:
    return run_router_agent(state)

def answer_node(state: ChatState) -> ChatState:
    return run_answer_agent(state)

def off_topic_rejector_node(state: ChatState) -> ChatState:
    state.agent_response = "我是一个专业的机器学习实训导师，你的问题与当前学习的内容无关，请回到课程内容。"
    return state

def route_decision(state: ChatState) -> str:
    if state.next_node == "ask_question":
        return "answer_node"
    elif state.next_node == "submit_quiz":
        # 暂未实现 quiz agent，打回 answer_node 统一处理
        return "answer_node"
    else:
        return "off_topic_rejector_node"

# 组装图谱
workflow = StateGraph(ChatState)
workflow.add_node("router", router_node)
workflow.add_node("answer_node", answer_node)
workflow.add_node("off_topic_rejector_node", off_topic_rejector_node)

workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_decision)
workflow.add_edge("answer_node", END)
workflow.add_edge("off_topic_rejector_node", END)

chat_app = workflow.compile()

def run_chat_workflow(state: ChatState) -> ChatState:
    # 兼容直接传入 pydantic 对象，langgraph 返回 dict
    result_dict = chat_app.invoke(state.model_dump())
    return ChatState(**result_dict)
