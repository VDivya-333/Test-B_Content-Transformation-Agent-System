from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.style_analysis_agent import StyleAnalysisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.conversion_agent import ConversionAgent
from app.agents.quality_control_agent import QualityControlAgent

class AgentState(TypedDict):
    content: str
    target_style: str
    target_format: str
    target_complexity: str
    analysis: Dict[str, Any]
    plan: Dict[str, Any]
    transformed_content: str
    metrics: Dict[str, Any]
    feedback: str
    iteration_count: int
    preserve_facts: bool
    agent_logs: List[Dict[str, str]]

async def analyze_node(state: AgentState):
    agent = StyleAnalysisAgent()
    analysis = await agent.analyze(state['content'])
    log = {"agent": "StyleAnalyst", "action": "Analyzing source content tone and complexity."}
    return {"analysis": analysis, "agent_logs": state.get("agent_logs", []) + [log]}

async def plan_node(state: AgentState):
    agent = PlanningAgent()
    plan_data = await agent.create_plan(
        state['analysis'],
        state['target_style'],
        state['target_complexity'],
        state['target_format']
    )
    log = {"agent": "Planner", "action": f"Retrieved guidelines: {plan_data.get('guidelines')}"}
    return {"plan": plan_data, "agent_logs": state.get("agent_logs", []) + [log]}

async def transform_node(state: AgentState):
    agent = ConversionAgent()
    transformed = await agent.transform(state['content'], state['plan'])
    log = {"agent": "Converter", "action": "Content transformation applied based on plan."}
    return {"transformed_content": transformed, "agent_logs": state.get("agent_logs", []) + [log]}

async def quality_control_node(state: AgentState):
    agent = QualityControlAgent()
    metrics = await agent.verify(
        state['content'], 
        state['transformed_content'],
        state.get('target_style', 'general'),
        state.get('target_complexity', 'standard'),
        state.get('target_format', 'markdown')
    )
    log = {"agent": "QC", "action": f"Quality Check: Fact Score={metrics.get('fact_preservation_score')}, Style Match={metrics.get('style_match')}", "details": metrics.get("feedback")}
    return {"metrics": metrics, "iteration_count": state.get("iteration_count", 0) + 1, "agent_logs": state.get("agent_logs", []) + [log]}

def should_continue(state: AgentState):
    metrics = state.get("metrics", {})
    fact_score = metrics.get("fact_preservation_score", 0)
    style_score = metrics.get("style_match", 0)
    
    if (fact_score < 90 or style_score < 80) and state.get("iteration_count", 0) < 3:
        return "transform"
    return END

def create_transformation_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", analyze_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("transform", transform_node)
    workflow.add_node("quality_control", quality_control_node)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "plan")
    workflow.add_edge("plan", "transform")
    workflow.add_edge("transform", "quality_control")

    workflow.add_conditional_edges(
        "quality_control",
        should_continue,
        {"transform": "transform", END: END}
    )

    return workflow.compile()
