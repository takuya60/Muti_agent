from pathlib import Path

from schemas.agent_state_schema import KnowledgeEvidence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge_base" / "processed"


def retrieve_knowledge(query: str, limit: int = 3) -> list[KnowledgeEvidence]:
    evidences: list[KnowledgeEvidence] = []
    keywords = [token for token in query.replace("/", " ").split() if token]

    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        score = sum(1 for keyword in keywords if keyword.lower() in text.lower())
        if score > 0 or not keywords:
            title = text.splitlines()[0].lstrip("# ") if text.splitlines() else path.stem
            evidences.append(KnowledgeEvidence(
                source_id=path.stem,
                title=title,
                content=text[:1200],
                knowledge_points=_extract_points(text),
                score=float(score),
            ))

    if not evidences:
        for path in sorted(KNOWLEDGE_DIR.glob("*.md"))[:limit]:
            text = path.read_text(encoding="utf-8")
            title = text.splitlines()[0].lstrip("# ") if text.splitlines() else path.stem
            evidences.append(KnowledgeEvidence(
                source_id=path.stem,
                title=title,
                content=text[:1200],
                knowledge_points=_extract_points(text),
                score=0.0,
            ))

    evidences.sort(key=lambda item: item.score, reverse=True)
    return evidences[:limit]


def _extract_points(text: str) -> list[str]:
    points: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- 知识点："):
            points.extend(item.strip() for item in stripped.removeprefix("- 知识点：").split("、") if item.strip())
    return points
