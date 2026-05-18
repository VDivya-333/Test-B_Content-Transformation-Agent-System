from app.agents.style_analysis_agent import StyleAnalysisAgent
from app.agents.planning_agent import PlanningAgent
from app.agents.conversion_agent import ConversionAgent
from app.agents.quality_control_agent import QualityControlAgent
from app.graph.state import GraphState
# import logging # Removed
from app.utils.logger import get_logger # Added

logger = get_logger() # Modified

style_agent = StyleAnalysisAgent()
planning_agent = PlanningAgent()
conversion_agent = ConversionAgent()
qc_agent = QualityControlAgent()

async def analyze_style(state: GraphState):
    logger.info(f"Queue | Job {state['job_id']} | Stage: Analyzing style...")
    analysis = await style_agent.analyze(state["source_text"])
    return {"analysis": analysis}

async def create_plan(state: GraphState):
    logger.info(f"Queue | Job {state['job_id']} | Stage: Creating plan...")
    plan = await planning_agent.create_plan(
        state["analysis"],
        state["target_style"],
        state["target_complexity"],
        state["target_format"]
    )
    return {"plan": plan}

async def transform_content(state: GraphState):
    logger.info(f"Queue | Job {state['job_id']} | Stage: Transforming (Iter {state.get('iteration_count', 0)})...")
    retry_reason = state.get("retry_reason")
    transformed = await conversion_agent.transform(state["source_text"], state["plan"], retry_reason)
    return {"transformed_content": transformed, "retry_reason": None} # Clear retry_reason after use

async def verify_output(state: GraphState):
    logger.info(f"Queue | Job {state['job_id']} | Stage: Verifying quality...")
    metrics = await qc_agent.verify(
        state["source_text"],
        state["transformed_content"],
        state["target_style"],
        state["target_complexity"],
        state["target_format"]
    )

    iteration_count = state.get("iteration_count", 0) + 1
    max_loops = state.get("max_iterations", 3)
    
    # Determine if a retry is needed and capture the reasoning in the state
    retry_reason = None
    fact_score = metrics.get("fact_preservation_score", 100)
    overall_score = metrics.get("overall_quality_score", 0)
    unsupported_claims = metrics.get("unsupported_claims", False)

    if (overall_score < 90 or fact_score < 95 or unsupported_claims) and iteration_count < max_loops:
        feedback_message = ""
        if fact_score < 95:
            feedback_message += f"Factual preservation score is low ({fact_score}%). Reasoning: {metrics.get('fact_reasoning', 'No specific reason provided.')}\n"
        if overall_score < 90:
            feedback_message += f"Overall quality score is low ({overall_score}%). Feedback: {metrics.get('feedback', 'No specific feedback provided.')}\n"
        if unsupported_claims:
            feedback_message += "Detected unsupported claims in the transformed content.\n"
        
        # METRIC LOGGING: Recording failures for observability dashboards
        logger.warning(
            f"METRIC | Transformation Failure | "
            f"Iteration: {iteration_count} | "
            f"Fact Score: {fact_score} | "
            f"Overall Score: {overall_score}"
        )
        # Add Failure Metrics as requested
        logger.warning(
            f"METRIC | FAILURE | "
            f"Low Quality Score: {overall_score}"
        )
        retry_reason = feedback_message.strip() if feedback_message else "Content needs refinement due to low quality or factual issues."
        # Add Retry Observability as requested
        logger.warning(
            f"RETRY_TRIGGERED | "
            f"Reason: {retry_reason}"
        )

    # Prepare the final output object to match TransformResponse schema
    # We only update final_output if we are not retrying, to keep the stream clean
    final_output = state.get("final_output")
    if not retry_reason:
        final_output = {
            "transformed_content": state["transformed_content"],
            "quality_score": metrics.get("overall_quality_score", 0.0)
        }

    # METRIC LOGGING: Recording successful completion
    if not retry_reason:
        logger.info(
            f"METRIC | Transformation Success | "
            f"Final Score: {metrics.get('overall_quality_score')} | "
            f"Total Iterations: {iteration_count}"
        )
        # Add Success Metrics as requested
        logger.info(
            f"METRIC | SUCCESS | "
            f"Quality Score: {metrics.get('overall_quality_score')}"
        )

    return {
        "quality_metrics": metrics,
        "iteration_count": iteration_count,
        "retry_reason": retry_reason,
        "final_output": final_output
    }
