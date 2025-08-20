"""
Legal Analyzer Service
Provides comprehensive legal document analysis including risk assessment, entity extraction, and legal insights
"""

import logging
from typing import Dict, Any, List, Optional
import re
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self, settings):
        self.settings = settings
        logger.info("LegalAnalyzer initialized successfully")
    
    async def analyze_document(self, text_content: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document content and provide insights.
        """
        try:
            analysis_result = {
                'document_id': document_info.get('document_id'),
                'filename': document_info.get('filename'),
                'analysis_timestamp': datetime.now().isoformat(),
                'summary': await self._generate_summary(text_content),
                'risk_assessment': await self._assess_risks(text_content),
                'entities': await self._extract_entities(text_content),
                'classification': await self._classify_document(text_content),
                'compliance_check': await self._check_compliance(text_content),
                'recommendations': await self._generate_recommendations(text_content)
            }
            
            logger.info(f"Document analysis completed for {document_info.get('filename')}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text using simple pattern matching."""
        try:
            topics = []
            
            # Common research/legal topic patterns
            topic_patterns = [
                r'\b(?:machine learning|artificial intelligence|AI|ML|deep learning|neural networks)\b',
                r'\b(?:quantum computing|blockchain|cryptocurrency|bitcoin|ethereum)\b',
                r'\b(?:climate change|global warming|sustainability|renewable energy)\b',
                r'\b(?:cybersecurity|privacy|data protection|encryption|authentication)\b',
                r'\b(?:contract|agreement|legal|law|regulation|compliance)\b',
                r'\b(?:research|study|analysis|investigation|experiment)\b',
                r'\b(?:technology|innovation|startup|entrepreneurship|business)\b'
            ]
            
            for pattern in topic_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    topic = match.group().lower()
                    if topic not in topics:
                        topics.append(topic)
            
            # If no specific topics found, extract capitalized phrases
            if not topics:
                cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
                matches = re.finditer(cap_pattern, text)
                potential_topics = [match.group() for match in matches]
                
                # Filter out common words and take first few
                common_words = ['The', 'And', 'For', 'With', 'From', 'This', 'That', 'They', 'Have', 'Will', 'Been', 'Were', 'Would', 'Could', 'Should']
                topics = [topic for topic in potential_topics if topic not in common_words][:5]
            
            return topics[:10]  # Limit to 10 topics
            
        except Exception as e:
            logger.error(f"Error extracting key topics: {e}")
            return []

    async def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate document summary using basic text analysis."""
        try:
            if not text:
                return {"summary": "No text content available", "word_count": 0, "key_topics": []}
            
            # Basic text statistics
            words = text.split()
            word_count = len(words)
            sentences = re.split(r'[.!?]+', text)
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Extract key topics (simplified)
            key_topics = self._extract_key_topics(text)
            
            # Generate summary (first few sentences)
            summary_sentences = sentences[:3]
            summary = ' '.join([s.strip() for s in summary_sentences if s.strip()])
            
            return {
                "summary": summary,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "key_topics": key_topics,
                "summary_length": len(summary)
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"summary": "Error generating summary", "word_count": 0, "key_topics": []}
    
    async def _assess_risks(self, text: str) -> Dict[str, Any]:
        """Assess potential risks in the document."""
        try:
            risk_factors = {
                "high_risk_terms": [],
                "confidentiality_issues": [],
                "legal_compliance_risks": [],
                "overall_risk_score": 0
            }
            
            # Check for high-risk terms
            high_risk_patterns = [
                r'\b(?:confidential|secret|classified|restricted|private)\b',
                r'\b(?:breach|violation|non-compliance|penalty|fine)\b',
                r'\b(?:terminate|cancel|void|invalid|unenforceable)\b',
                r'\b(?:liability|damages|compensation|settlement)\b'
            ]
            
            for pattern in high_risk_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    risk_factors["high_risk_terms"].append({
                        "term": match.group(),
                        "context": text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Check for confidentiality issues
            confidential_patterns = [
                r'\b(?:ssn|social\s+security|credit\s+card|bank\s+account|password)\b',
                r'\b(?:address|phone|email|birth\s+date|driver\s+license)\b'
            ]
            
            for pattern in confidential_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    risk_factors["confidentiality_issues"].append({
                        "type": "personal_information",
                        "context": text[max(0, match.start()-20):match.end()+20]
                    })
            
            # Calculate overall risk score
            risk_score = 0
            risk_score += len(risk_factors["high_risk_terms"]) * 10
            risk_score += len(risk_factors["confidentiality_issues"]) * 15
            risk_score = min(risk_score, 100)  # Cap at 100
            
            risk_factors["overall_risk_score"] = risk_score
            
            # Determine risk level
            if risk_score >= 70:
                risk_factors["risk_level"] = "HIGH"
            elif risk_score >= 40:
                risk_factors["risk_level"] = "MEDIUM"
            else:
                risk_factors["risk_level"] = "LOW"
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {"overall_risk_score": 0, "risk_level": "UNKNOWN", "error": str(e)}
    
    async def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        try:
            entities = {
                "organizations": [],
                "persons": [],
                "dates": [],
                "locations": [],
                "legal_references": [],
                "monetary_amounts": []
            }
            
            # Extract organizations (simplified pattern matching)
            org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:LLC|Inc|Corp|Company|Organization|Institute|University|College)\b'
            org_matches = re.finditer(org_pattern, text)
            entities["organizations"] = list(set([match.group() for match in org_matches]))
            
            # Extract dates
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
            ]
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                entities["dates"].extend([match.group() for match in matches])
            
            # Extract legal references
            legal_patterns = [
                r'\b(?:Section|Article|Chapter|Part|Rule|Regulation)\s+\d+[A-Za-z]*\b',
                r'\b(?:Act|Statute|Code|Law)\s+(?:of|No\.?|Number)?\s*[A-Za-z0-9\s]+\b',
                r'\b(?:Case|Matter|Petition|Appeal|Writ|Suit)\s+(?:No\.?|Number)?\s*[:\-]?\s*[A-Za-z0-9\/\-]+\b'
            ]
            
            for pattern in legal_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                entities["legal_references"].extend([match.group() for match in matches])
            
            # Extract monetary amounts
            money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|EUR|GBP)'
            money_matches = re.finditer(money_pattern, text, re.IGNORECASE)
            entities["monetary_amounts"] = list(set([match.group() for match in money_matches]))
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"error": str(e)}
    
    async def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type based on content."""
        try:
            classification = {
                "document_type": "unknown",
                "confidence": 0.0,
                "indicators": []
            }
            
            # Define document type patterns
            doc_patterns = {
                "contract": [
                    r'\b(?:agreement|contract|terms|conditions|clause|party|parties)\b',
                    r'\b(?:effective\s+date|termination|renewal|amendment)\b'
                ],
                "legal_notice": [
                    r'\b(?:notice|notification|warning|cease\s+and\s+desist|demand)\b',
                    r'\b(?:legal\s+action|lawsuit|litigation|court|judgment)\b'
                ],
                "policy_document": [
                    r'\b(?:policy|procedure|guideline|standard|requirement|compliance)\b',
                    r'\b(?:employee|staff|personnel|workplace|conduct)\b'
                ],
                "research_paper": [
                    r'\b(?:abstract|introduction|methodology|conclusion|references|bibliography)\b',
                    r'\b(?:research|study|analysis|investigation|findings)\b'
                ]
            }
            
            # Score each document type
            scores = {}
            for doc_type, patterns in doc_patterns.items():
                score = 0
                indicators = []
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    count = len(list(matches))
                    score += count
                    if count > 0:
                        indicators.append(f"Found {count} {doc_type} indicators")
                
                scores[doc_type] = {"score": score, "indicators": indicators}
            
            # Find the best match
            best_type = max(scores.keys(), key=lambda x: scores[x]["score"])
            best_score = scores[best_type]["score"]
            
            if best_score > 0:
                classification["document_type"] = best_type
                classification["confidence"] = min(best_score / 10.0, 1.0)  # Normalize to 0-1
                classification["indicators"] = scores[best_type]["indicators"]
            else:
                classification["document_type"] = "general_document"
                classification["confidence"] = 0.1
                classification["indicators"] = ["No specific document type indicators found"]
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying document: {e}")
            return {"document_type": "unknown", "confidence": 0.0, "error": str(e)}
    
    async def _check_compliance(self, text: str) -> Dict[str, Any]:
        """Check document compliance with common regulations."""
        try:
            compliance_check = {
                "gdpr_compliance": {"status": "unknown", "issues": []},
                "hipaa_compliance": {"status": "unknown", "issues": []},
                "sox_compliance": {"status": "unknown", "issues": []},
                "overall_compliance": "unknown"
            }
            
            # GDPR compliance check
            gdpr_patterns = [
                r'\b(?:personal\s+data|data\s+subject|consent|right\s+to\s+erasure)\b',
                r'\b(?:data\s+protection|privacy|processing|storage|transfer)\b'
            ]
            
            gdpr_indicators = 0
            for pattern in gdpr_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                gdpr_indicators += len(list(matches))
            
            if gdpr_indicators > 5:
                compliance_check["gdpr_compliance"]["status"] = "relevant"
                compliance_check["gdpr_compliance"]["issues"].append("Document contains personal data processing information")
            else:
                compliance_check["gdpr_compliance"]["status"] = "not_applicable"
            
            # HIPAA compliance check
            hipaa_patterns = [
                r'\b(?:health\s+information|medical\s+record|patient|treatment|diagnosis)\b',
                r'\b(?:phi|protected\s+health\s+information|healthcare|hospital|clinic)\b'
            ]
            
            hipaa_indicators = 0
            for pattern in hipaa_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                hipaa_indicators += len(list(matches))
            
            if hipaa_indicators > 3:
                compliance_check["hipaa_compliance"]["status"] = "relevant"
                compliance_check["hipaa_compliance"]["issues"].append("Document contains health information")
            else:
                compliance_check["hipaa_compliance"]["status"] = "not_applicable"
            
            # Determine overall compliance
            relevant_checks = [check for check in compliance_check.values() if isinstance(check, dict) and check.get("status") == "relevant"]
            if not relevant_checks:
                compliance_check["overall_compliance"] = "not_applicable"
            elif any(check.get("issues") for check in relevant_checks):
                compliance_check["overall_compliance"] = "needs_review"
            else:
                compliance_check["overall_compliance"] = "compliant"
            
            return compliance_check
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            return {"overall_compliance": "error", "error": str(e)}
    
    async def _generate_recommendations(self, text: str) -> List[str]:
        """Generate recommendations based on document analysis."""
        try:
            recommendations = []
            
            # Check document length
            word_count = len(text.split())
            if word_count < 100:
                recommendations.append("Document is very short - consider adding more detail")
            elif word_count > 5000:
                recommendations.append("Document is very long - consider breaking into sections")
            
            # Check for missing elements
            if not re.search(r'\b(?:date|effective\s+date|issued|created)\b', text, re.IGNORECASE):
                recommendations.append("Consider adding a date or effective date")
            
            if not re.search(r'\b(?:signature|signed|authorized|approved)\b', text, re.IGNORECASE):
                recommendations.append("Consider adding signature or authorization information")
            
            # Check for clarity
            if re.search(r'\b(?:shall|must|will|should)\b', text, re.IGNORECASE):
                recommendations.append("Document contains obligations - ensure clarity and enforceability")
            
            # Add general recommendations
            if not recommendations:
                recommendations.append("Document appears well-structured")
                recommendations.append("Consider having legal counsel review if this is a binding agreement")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"] 