import asyncio
from typing import Any, Dict, Optional


class Orchestrator:
    def __init__(self, document_processor, legal_analyzer, web_scraper, knowledge_graph, literature) -> None:
        self.document_processor = document_processor
        self.legal_analyzer = legal_analyzer
        self.web_scraper = web_scraper
        self.knowledge_graph = knowledge_graph
        self.literature = literature

    async def run_full_pipeline(self, document_id: str) -> Dict[str, Any]:
        document = await self.document_processor.get_document(document_id)
        if not document:
            return {"status": "error", "detail": "Document not found"}

        analysis = await self.legal_analyzer.analyze_document(
            document_id=document_id,
            analysis_type="comprehensive",
            include_translation=True,
            include_risk_assessment=True,
            include_entities=True,
            include_precedents=True,
        )

        entities = analysis.get("entities", {})
        graph_json = self.knowledge_graph.build_from_document(document_id, entities)

        title_or_query = analysis.get("summary", {}).get("title") or analysis.get("classification", {}).get("top_label") or "legal research"
        literature = self.literature.aggregate_results(title_or_query, limit=8)

        return {
            "status": "ok",
            "analysis": analysis,
            "knowledge_graph": graph_json,
            "literature": literature,
        }

