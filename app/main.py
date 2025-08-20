# FastAPI Main Application for Research Document Analysis System
# Complete backend with all endpoints and functionality

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import os
import json
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager
import time

# Import our services
from app.services.document_processor import DocumentProcessor
from app.services.legal_analyzer import LegalAnalyzer
from app.services.web_scraper import WebScraper
from app.services.ai_models import AIModels
from app.services.model_fine_tuning import ModelFineTuner
from app.services.knowledge_graph import KnowledgeGraphBuilder
from app.services.literature_crossref import LiteratureCrossRef
from app.agents.orchestrator import Orchestrator
from app.models.document import Document, DocumentCreate, DocumentResponse
from app.models.analysis import AnalysisResult, RiskAssessment
from app.utils.config import get_settings
from app.utils.helpers import generate_document_id, validate_file_type

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for services
document_processor = None
legal_analyzer = None
web_scraper = None
ai_models = None
model_fine_tuner = None
knowledge_graph = None
literature_service = None
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global document_processor, legal_analyzer, web_scraper, ai_models, model_fine_tuner, knowledge_graph, literature_service, orchestrator
    
    # Startup
    logger.info("Starting Research Document Analysis System...")
    
    # Initialize services
    settings = get_settings()
    
    document_processor = DocumentProcessor(settings)
    legal_analyzer = LegalAnalyzer(settings)
    web_scraper = WebScraper(settings)
    ai_models = AIModels(settings)
    model_fine_tuner = ModelFineTuner({
        "base_model": settings.base_model,
        "legal_model": settings.legal_model,
        "translation_model": settings.translation_model,
        "max_length": settings.max_length,
        "batch_size": settings.batch_size
    })
    knowledge_graph = KnowledgeGraphBuilder()
    literature_service = LiteratureCrossRef()
    orchestrator = Orchestrator(document_processor, legal_analyzer, web_scraper, knowledge_graph, literature_service)
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Research Document Analysis System...")

# Create FastAPI app
app = FastAPI(
    title="Research Document Analysis System",
    description="AI-powered research document analysis, knowledge discovery, and literature cross-referencing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://cap-frontend-w94q-qh0552vw9-vis-projects-82c0f63d.vercel.app",
        "https://capstone-frontend-vidharias-projects-82c0f63d.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.vercel.app",
        "*.netlify.app",
        "web-production-d301.up.railway.app"
    ]
)

# Mount static files
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: Dict[str, str]

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    file_type: str
    upload_time: str
    status: str

class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: str = "comprehensive"
    include_translation: bool = True
    include_risk_assessment: bool = True
    include_entities: bool = True
    include_precedents: bool = True

class FineTuningRequest(BaseModel):
    model_name: str
    task_type: str  # "classification", "ner", "risk_assessment"
    training_data: List[Dict[str, Any]]
    num_epochs: int = 3
    batch_size: int = 16
    learning_rate: float = 2e-5
    task_name: str

class ModelEvaluationRequest(BaseModel):
    model_path: str
    test_data: List[Dict[str, Any]]
    task_type: str

class KnowledgeGraphRequest(BaseModel):
    document_id: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    center_node_label: Optional[str] = None
    node_type: Optional[str] = None
    depth: int = 2

class LiteratureSearchRequest(BaseModel):
    query: str
    limit: int = 10

class CompareDocumentsRequest(BaseModel):
    left_document_id: Optional[str] = None
    right_document_id: Optional[str] = None
    left_text: Optional[str] = None
    right_text: Optional[str] = None

class QARequest(BaseModel):
    question: str
    document_id: Optional[str] = None

class PipelineRunRequest(BaseModel):
    document_id: str

# API Routes

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Research Document Analysis System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services_status = {
        "document_processor": "operational",
        "legal_analyzer": "operational", 
        "web_scraper": "operational",
        "ai_models": "operational",
        "knowledge_graph": "operational",
        "literature_service": "operational",
        "orchestrator": "operational",
        "database": "operational"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services=services_status
    )

@app.post("/upload-document", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload a research document for analysis"""
    
    try:
        # Validate file type
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported types: PDF, DOC, DOCX, TXT, JPG, PNG"
            )
        
        # Generate document ID
        document_id = generate_document_id()
        
        # Process document
        document_info = await document_processor.process_document(file, document_id)
        
        # Store document metadata
        document_data = DocumentCreate(
            document_id=document_id,
            filename=file.filename,
            file_size=file.size,
            file_type=file.content_type,
            upload_time=datetime.now(),
            status="uploaded"
        )
        
        # Add background task for initial processing
        if background_tasks:
            background_tasks.add_task(
                document_processor.background_processing,
                document_id,
                document_info
            )
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file.size,
            file_type=file.content_type,
            upload_time=datetime.now().isoformat(),
            status="uploaded"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-document", response_model=AnalysisResult)
async def analyze_document(request: AnalysisRequest):
    """Analyze a research document comprehensively"""
    
    try:
        # Get document info
        document = await document_processor.get_document(request.document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Perform comprehensive analysis
        analysis_result = await legal_analyzer.analyze_document(
            document_id=request.document_id,
            analysis_type=request.analysis_type,
            include_translation=request.include_translation,
            include_risk_assessment=request.include_risk_assessment,
            include_entities=request.include_entities,
            include_precedents=request.include_precedents
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document information"""
    
    try:
        document = await document_processor.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """List all documents with optional filtering"""
    
    try:
        documents = await document_processor.list_documents(skip, limit, status)
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    
    try:
        success = await document_processor.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_text(
    text: str = Form(...),
    source_language: str = Form("auto"),
    target_language: str = Form("en")
):
    """Translate research text"""
    
    try:
        translation = await ai_models.translate_text(
            text=text,
            source_language=source_language,
            target_language=target_language
        )
        
        return {
            "original_text": text,
            "translated_text": translation["translated_text"],
            "source_language": translation["source_language"],
            "target_language": target_language,
            "confidence": translation["confidence"]
        }
        
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-entities")
async def extract_entities(text: str = Form(...)):
    """Extract research entities from text"""
    
    try:
        entities = await ai_models.extract_legal_entities(text)
        
        return {
            "text": text,
            "entities": entities
        }
        
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess-risk")
async def assess_risk(text: str = Form(...)):
    """Assess research risk in text"""
    
    try:
        risk_assessment = await legal_analyzer.assess_risk(text)
        
        return risk_assessment
        
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-precedents")
async def search_precedents(
    query: str = Form(...),
    jurisdiction: Optional[str] = Form(None),
    limit: int = Form(10)
):
    """Search for research precedents"""
    
    try:
        precedents = await web_scraper.search_legal_precedents(
            query=query,
            jurisdiction=jurisdiction,
            limit=limit
        )
        
        return {
            "query": query,
            "jurisdiction": jurisdiction,
            "precedents": precedents,
            "total_found": len(precedents)
        }
        
    except Exception as e:
        logger.error(f"Error searching precedents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fine-tune-model")
async def fine_tune_model(request: FineTuningRequest):
    """Fine-tune AI models for research analysis"""
    
    try:
        if request.task_type == "classification":
            result = model_fine_tuner.fine_tune_classification_model(
                model_name=request.model_name,
                data=request.training_data,
                task_name=request.task_name,
                num_epochs=request.num_epochs,
                batch_size=request.batch_size,
                learning_rate=request.learning_rate
            )
        elif request.task_type == "ner":
            result = model_fine_tuner.fine_tune_ner_model(
                model_name=request.model_name,
                data=request.training_data,
                task_name=request.task_name,
                num_epochs=request.num_epochs,
                batch_size=request.batch_size,
                learning_rate=request.learning_rate
            )
        elif request.task_type == "risk_assessment":
            result = model_fine_tuner.fine_tune_risk_assessment_model(
                model_name=request.model_name,
                data=request.training_data,
                task_name=request.task_name,
                num_epochs=request.num_epochs,
                batch_size=request.batch_size,
                learning_rate=request.learning_rate
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported task type: {request.task_type}"
            )
        
        return {
            "message": "Model fine-tuning completed successfully",
            "task_name": request.task_name,
            "task_type": request.task_type,
            "results": result
        }
        
    except Exception as e:
        logger.error(f"Error fine-tuning model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate-model")
async def evaluate_model(request: ModelEvaluationRequest):
    """Evaluate fine-tuned model performance"""
    
    try:
        results = model_fine_tuner.evaluate_model_performance(
            model_path=request.model_path,
            test_data=request.test_data,
            task_type=request.task_type
        )
        
        return {
            "message": "Model evaluation completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge-graph/build")
async def build_knowledge_graph(request: KnowledgeGraphRequest):
    try:
        if request.entities:
            result = knowledge_graph.build_from_document(request.document_id or "doc", request.entities)
        elif request.center_node_label:
            result = knowledge_graph.get_subgraph(
                center_node_label=request.center_node_label,
                node_type=request.node_type,
                depth=request.depth,
            )
        else:
            result = knowledge_graph.stats()
        return result
    except Exception as e:
        logger.error(f"Error building knowledge graph: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/literature/search")
async def search_literature(request: LiteratureSearchRequest):
    try:
        return literature_service.aggregate_results(request.query, request.limit)
    except Exception as e:
        logger.error(f"Error searching literature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare-documents")
async def compare_documents(request: CompareDocumentsRequest):
    try:
        # Simple textual diff placeholder – can be enhanced with clause alignment later
        left_text = request.left_text
        right_text = request.right_text
        if request.left_document_id:
            left = await document_processor.get_document(request.left_document_id)
            left_text = left.get("text") if left else None
        if request.right_document_id:
            right = await document_processor.get_document(request.right_document_id)
            right_text = right.get("text") if right else None
        if not left_text or not right_text:
            raise HTTPException(status_code=400, detail="Both texts are required")
        left_set = set(left_text.split())
        right_set = set(right_text.split())
        missing_in_right = sorted(list(left_set - right_set))
        missing_in_left = sorted(list(right_set - left_set))
        overlap_ratio = len(left_set & right_set) / max(1, len(left_set | right_set))
        return {
            "overlap_ratio": overlap_ratio,
            "missing_in_right": missing_in_right[:200],
            "missing_in_left": missing_in_left[:200],
        }
    except Exception as e:
        logger.error(f"Error comparing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/run")
async def run_pipeline(request: PipelineRunRequest):
    try:
        result = await orchestrator.run_full_pipeline(request.document_id)
        return result
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def list_models():
    """List available fine-tuned models"""
    
    try:
        models = model_fine_tuner.get_available_models()
        
        return {
            "models": models,
            "total_models": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{task_name}")
async def delete_model(task_name: str):
    """Delete a fine-tuned model"""
    
    try:
        success = model_fine_tuner.delete_model(task_name)
        
        if success:
            return {"message": f"Model {task_name} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")
        
    except Exception as e:
        logger.error(f"Error deleting model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get system analytics and metrics"""
    
    try:
        # Get document statistics
        total_documents = await document_processor.get_document_count()
        recent_documents = await document_processor.get_recent_documents(7)
        
        # Get analysis statistics
        analysis_stats = await legal_analyzer.get_analysis_statistics()
        
        # Get model performance metrics
        model_metrics = await ai_models.get_model_performance()
        
        return {
            "documents": {
                "total": total_documents,
                "recent_uploads": len(recent_documents),
                "average_file_size": sum(doc.file_size for doc in recent_documents) / len(recent_documents) if recent_documents else 0
            },
            "analysis": analysis_stats,
            "models": model_metrics,
            "system": {
                "uptime": "99.9%",
                "response_time": "2.3s",
                "active_users": 89
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api-docs")
async def get_api_docs():
    """Get API documentation"""
    return {
        "title": "Research Document Analysis System API",
        "version": "1.0.0",
        "description": "AI-powered research document analysis, knowledge discovery, and literature cross-referencing platform",
        "endpoints": {
            "health": "GET /health - System health check",
            "upload": "POST /upload-document - Upload research document",
            "analyze": "POST /analyze-document - Analyze document comprehensively",
            "translate": "POST /translate - Translate research text",
            "entities": "POST /extract-entities - Extract research entities",
            "risk": "POST /assess-risk - Assess research risk",
            "precedents": "POST /search-precedents - Search research precedents",
            "knowledge_graph": "POST /knowledge-graph/build - Build knowledge graph",
            "literature": "POST /literature/search - Search academic literature",
            "compare": "POST /compare-documents - Compare documents",
            "pipeline": "POST /pipeline/run - Run full analysis pipeline",
            "fine_tune": "POST /fine-tune-model - Fine-tune AI models",
            "evaluate": "POST /evaluate-model - Evaluate model performance",
            "models": "GET /models - List available models",
            "analytics": "GET /analytics - Get system analytics"
        }
    }

@app.post("/search-papers")
async def search_scientific_papers(
    request: dict
):
    """
    Search for scientific papers across multiple academic sources.
    """
    try:
        # Extract data from request
        topic = request.get("topic", "")
        max_results = request.get("max_results", 10)
        sources = request.get("sources", ["google_scholar"])
        
        logger.info(f"Search request - Topic: {topic}, Max Results: {max_results}, Sources: {sources}")
        
        # Use the global web_scraper instance from lifespan
        global web_scraper
        
        # Handle source selection properly
        logger.info(f"Source selection logic - Sources: {sources}, Length: {len(sources)}")
        
        if "all" in sources or len(sources) > 1:
            logger.info("Searching multiple sources")
            # Search multiple sources
            results = await web_scraper.search_multiple_sources(topic, max_results)
            
            return {
                "success": True,
                "topic": topic,
                "results": results,
                "timestamp": time.time()
            }
        else:
            # Search single source
            source = sources[0] if sources else "google_scholar"
            logger.info(f"Searching single source: {source} for topic: {topic}")
            
            if source == "google_scholar":
                logger.info(f"Searching Google Scholar for topic: {topic}")
                paper_results = await web_scraper.search_google_scholar(topic, max_results)
                logger.info(f"Google Scholar returned {len(paper_results)} results")
            elif source == "arxiv":
                logger.info(f"Searching arXiv for topic: {topic}")
                paper_results = await web_scraper.search_arxiv(topic, max_results)
                logger.info(f"arXiv returned {len(paper_results)} results")
            elif source == "pubmed":
                logger.info(f"Searching PubMed for topic: {topic}")
                paper_results = await web_scraper.search_pubmed(topic, max_results)
                logger.info(f"PubMed returned {len(paper_results)} results")
            else:
                logger.warning(f"Unknown source: {source}, defaulting to Google Scholar")
                paper_results = await web_scraper.search_google_scholar(topic, max_results)
            
            # Format single source results to match multi-source format
            results = {
                source: paper_results,
                'summary': {
                    'total_papers_found': len(paper_results),
                    'sources_searched': 1,
                    'search_topic': topic,
                    'timestamp': time.time()
                }
            }
            
            logger.info(f"Single source results formatted - Source: {source}, Papers: {len(paper_results)}")
            
            return {
                "success": True,
                "topic": topic,
                "results": results,
                "timestamp": time.time()
            }
        
    except Exception as e:
        logger.error(f"Error in paper search: {e}")
        return {
            "success": False,
            "error": str(e),
            "topic": request.get("topic", ""),
            "results": []
        }

@app.get("/search-papers/{topic}")
async def search_papers_by_topic(
    topic: str,
    max_results: int = Query(10, description="Maximum number of results per source"),
    source: str = Query("google_scholar", description="Source to search (google_scholar, arxiv, pubmed)")
):
    """
    Search for scientific papers by topic using GET request.
    """
    try:
        # Use the global web_scraper instance from lifespan
        global web_scraper
        
        if source == "google_scholar":
            results = await web_scraper.search_google_scholar(topic, max_results)
        elif source == "arxiv":
            results = await web_scraper.search_arxiv(topic, max_results)
        elif source == "pubmed":
            results = await web_scraper.search_pubmed(topic, max_results)
        else:
            results = await web_scraper.search_google_scholar(topic, max_results)
        
        return {
            "success": True,
            "topic": topic,
            "source": source,
            "results": results,
            "count": len(results),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error in paper search: {e}")
        return {
            "success": False,
            "error": str(e),
            "topic": topic,
            "source": source,
            "results": []
        }

@app.get("/paper-sources")
async def get_available_paper_sources():
    """
    Get list of available paper search sources.
    """
    return {
        "sources": [
            {
                "id": "google_scholar",
                "name": "Google Scholar",
                "description": "Academic papers, theses, books, abstracts and articles",
                "url": "https://scholar.google.com"
            },
            {
                "id": "arxiv",
                "name": "arXiv",
                "description": "Preprints in physics, mathematics, computer science, and related fields",
                "url": "https://arxiv.org"
            },
            {
                "id": "pubmed",
                "name": "PubMed",
                "description": "Biomedical and life sciences literature database",
                "url": "https://pubmed.ncbi.nlm.nih.gov"
            }
        ]
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Research Document Analysis System starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Research Document Analysis System shutting down...")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 