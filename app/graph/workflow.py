from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    analyze_style,
    create_plan,
    transform_content,
    verify_output
)

workflow = StateGraph(GraphState)

workflow.add_node("analyze_style", analyze_style)
workflow.add_node("create_plan", create_plan)
workflow.add_node("transform_content", transform_content)
workflow.add_node("verify_output", verify_output)

workflow.set_entry_point("analyze_style")

workflow.add_edge("analyze_style", "create_plan")
workflow.add_edge("create_plan", "transform_content")
workflow.add_edge("transform_content", "verify_output")

def should_continue(state: GraphState):
    """
    Step 5: Decision Logic
    Determines if the quality is high enough or if we need to loop back to Step 3.
    Note: State updates (like retry_reason) are handled in the verify_output node.
    """
    if state.get("quality_metrics") and "error" in state["quality_metrics"]:
        return END

    if state.get("retry_reason"):
        return "transform_content"
    return END

workflow.add_conditional_edges(
    "verify_output",
    should_continue,
    {
        "transform_content": "transform_content",
        END: END
    }
)

app_workflow = workflow.compile()

async def run_workflow(job_id, source_text, target_format, target_style, target_complexity, preserve_facts=True, max_iterations=3):
    """
    Asynchronously runs the transformation workflow with the given inputs.
    """
    initial_state = {
        "job_id": job_id,
        "source_text": source_text,
        "target_format": target_format,
        "target_style": target_style,
        "target_complexity": target_complexity,
        "preserve_facts": preserve_facts,
        "max_iterations": max_iterations,
        "analysis": None,
        "plan": None,
        "transformed_content": None,
        "quality_metrics": None,
        "final_output": None,
        "iteration_count": 0
    }

    # Asynchronously invoke the workflow
    # Passing job_id in config for better observability in tracing tools
    final_state = await app_workflow.ainvoke(
        initial_state, 
        config={
            "configurable": {"thread_id": job_id},
            "tags": [f"job_id:{job_id}"]
        }
    )
    return final_state