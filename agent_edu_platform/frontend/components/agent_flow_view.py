from pathlib import Path


def render_agent_flow(events: list[dict]) -> str:
    lines = ["digraph AgentFlow {", "  rankdir=LR;", "  node [shape=box, style=rounded];"]
    for index, event in enumerate(events):
        node_id = f"A{index}"
        label = f"{event.get('agent', 'Agent')}\\n{event.get('status', '')}"
        lines.append(f'  {node_id} [label="{label}"];')
        if index > 0:
            lines.append(f"  A{index - 1} -> {node_id};")
    lines.append("}")
    return "\n".join(lines)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]
