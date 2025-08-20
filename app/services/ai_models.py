"""
AI Models Service - Simplified Version
Handles basic text processing without heavy ML dependencies
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class AIModels:
    def __init__(self, settings):
        self.settings = settings
        
        # Language mapping
        self.language_codes = {
            'hi': 'Hindi', 'en': 'English', 'bn': 'Bengali', 'pa': 'Punjabi',
            'gu': 'Gujarati', 'or': 'Odia', 'ta': 'Tamil', 'te': 'Telugu',
            'kn': 'Kannada', 'ml': 'Malayalam', 'mr': 'Marathi', 'ur': 'Urdu'
        }
        
        logger.info("AI Models service initialized successfully (simplified version)")
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Translate text between languages (simplified version).
        In production, this would use proper translation APIs.
        """
        try:
            if not text or source_lang == target_lang:
                return {
                    'translated_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'confidence': 1.0,
                    'method': 'no_translation_needed'
                }
            
            # Simple word replacement for demonstration
            # In production, use Google Translate API or similar
            translated_text = f"[TRANSLATED: {source_lang} -> {target_lang}] {text}"
            
            return {
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': target_lang,
                'confidence': 0.8,
                'method': 'simplified_translation'
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'translated_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'confidence': 0.0,
                'error': str(e),
                'method': 'error_fallback'
            }
    
    async def extract_entities(self, text: str, entity_types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text using pattern matching.
        """
        try:
            if entity_types is None:
                entity_types = ['PERSON', 'ORGANIZATION', 'DATE', 'LOCATION', 'MONEY']
            
            entities = {entity_type: [] for entity_type in entity_types}
            
            # Extract persons (simple pattern matching)
            if 'PERSON' in entity_types:
                person_patterns = [
                    r'\b(?:Mr\.|Ms\.|Dr\.|Prof\.|Sir|Madam)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:said|reported|announced|stated)\b'
                ]
                
                for pattern in person_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        person_name = match.group(1) if match.groups() else match.group()
                        entities['PERSON'].append({
                            'text': person_name,
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': 0.7
                        })
            
            # Extract organizations
            if 'ORGANIZATION' in entity_types:
                org_patterns = [
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:LLC|Inc|Corp|Company|Organization|Institute|University|College)\b',
                    r'\b(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Department|Ministry|Agency|Commission)\b'
                ]
                
                for pattern in org_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        org_name = match.group(1) if match.groups() else match.group()
                        entities['ORGANIZATION'].append({
                            'text': org_name,
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': 0.8
                        })
            
            # Extract dates
            if 'DATE' in entity_types:
                date_patterns = [
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
                ]
                
                for pattern in date_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        entities['DATE'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': 0.9
                        })
            
            # Extract locations
            if 'LOCATION' in entity_types:
                location_patterns = [
                    r'\b(?:in|at|from|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+(?:[A-Z]{2}|[A-Z][a-z]+)\b'
                ]
                
                for pattern in location_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        location = match.group(1) if match.groups() else match.group()
                        entities['LOCATION'].append({
                            'text': location,
                            'start': match.start(),
                            'end': match.end(),
                            'confidence': 0.6
                        })
            
            # Extract monetary amounts
            if 'MONEY' in entity_types:
                money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|USD|EUR|GBP)'
                matches = re.finditer(money_pattern, text, re.IGNORECASE)
                for match in matches:
                    entities['MONEY'].append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9
                    })
            
            # Remove duplicates and limit results
            for entity_type in entities:
                seen = set()
                unique_entities = []
                for entity in entities[entity_type]:
                    if entity['text'] not in seen:
                        seen.add(entity['text'])
                        unique_entities.append(entity)
                entities[entity_type] = unique_entities[:20]  # Limit to 20 per type
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return {"error": str(e)}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using simple pattern matching.
        """
        try:
            if not text:
                return {'sentiment': 'neutral', 'confidence': 0.0, 'score': 0.0}
            
            # Simple sentiment analysis using keyword counting
            positive_words = [
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'positive', 'beneficial', 'advantageous', 'profitable', 'successful',
                'improve', 'enhance', 'increase', 'growth', 'profit', 'benefit'
            ]
            
            negative_words = [
                'bad', 'terrible', 'awful', 'horrible', 'negative', 'harmful',
                'damaging', 'detrimental', 'loss', 'decrease', 'decline', 'failure',
                'problem', 'issue', 'concern', 'risk', 'danger', 'threat'
            ]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            # Calculate sentiment score
            total_words = len(text.split())
            if total_words == 0:
                return {'sentiment': 'neutral', 'confidence': 0.0, 'score': 0.0}
            
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
            
            if positive_score > negative_score:
                sentiment = 'positive'
                confidence = min(positive_score * 10, 1.0)
                score = positive_score - negative_score
            elif negative_score > positive_score:
                sentiment = 'negative'
                confidence = min(negative_score * 10, 1.0)
                score = negative_score - positive_score
            else:
                sentiment = 'neutral'
                confidence = 0.5
                score = 0.0
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'score': score,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'method': 'keyword_based'
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0, 'error': str(e)}
    
    async def classify_text(self, text: str, categories: List[str]) -> Dict[str, Any]:
        """
        Classify text into categories using keyword matching.
        """
        try:
            if not text or not categories:
                return {'category': 'unknown', 'confidence': 0.0, 'scores': {}}
            
            text_lower = text.lower()
            scores = {}
            
            # Define category keywords
            category_keywords = {
                'technology': ['technology', 'software', 'hardware', 'computer', 'digital', 'ai', 'machine learning'],
                'legal': ['legal', 'law', 'contract', 'agreement', 'regulation', 'compliance', 'court'],
                'business': ['business', 'company', 'corporate', 'management', 'strategy', 'market', 'finance'],
                'healthcare': ['health', 'medical', 'patient', 'treatment', 'hospital', 'doctor', 'medicine'],
                'education': ['education', 'learning', 'teaching', 'student', 'school', 'university', 'course'],
                'research': ['research', 'study', 'analysis', 'investigation', 'experiment', 'data', 'findings']
            }
            
            # Score each category
            for category in categories:
                if category in category_keywords:
                    keywords = category_keywords[category]
                    score = sum(1 for keyword in keywords if keyword in text_lower)
                    scores[category] = score
                else:
                    # Generic scoring for unknown categories
                    score = len([word for word in category.lower().split() if word in text_lower])
                    scores[category] = score
            
            # Find best category
            if not scores:
                return {'category': 'unknown', 'confidence': 0.0, 'scores': {}}
            
            best_category = max(scores.keys(), key=lambda x: scores[x])
            best_score = scores[best_category]
            
            # Normalize confidence
            total_keywords = sum(scores.values())
            confidence = best_score / total_keywords if total_keywords > 0 else 0.0
            
            return {
                'category': best_category,
                'confidence': confidence,
                'scores': scores,
                'method': 'keyword_based'
            }
            
        except Exception as e:
            logger.error(f"Text classification error: {e}")
            return {'category': 'unknown', 'confidence': 0.0, 'error': str(e)}
    
    async def generate_summary(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        """
        Generate text summary using extractive method.
        """
        try:
            if not text:
                return {'summary': '', 'length': 0, 'method': 'extractive'}
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return {'summary': '', 'length': 0, 'method': 'extractive'}
            
            # Simple scoring based on sentence length and position
            sentence_scores = []
            for i, sentence in enumerate(sentences):
                score = 0
                # Higher score for medium-length sentences
                if 20 <= len(sentence) <= 100:
                    score += 2
                # Higher score for early sentences
                score += max(0, 5 - i)
                # Bonus for sentences with key terms
                key_terms = ['research', 'study', 'analysis', 'findings', 'conclusion', 'summary']
                score += sum(1 for term in key_terms if term.lower() in sentence.lower())
                
                sentence_scores.append((sentence, score))
            
            # Sort by score and take top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Build summary
            summary_sentences = []
            current_length = 0
            
            for sentence, score in sentence_scores:
                if current_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            summary = '. '.join(summary_sentences) + '.'
            
            return {
                'summary': summary,
                'length': len(summary),
                'method': 'extractive',
                'original_length': len(text),
                'compression_ratio': len(summary) / len(text) if text else 0
            }
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return {'summary': '', 'length': 0, 'error': str(e)}
    
    async def generate_embeddings(self, text: str) -> Dict[str, Any]:
        """
        Generate text embeddings (simplified version).
        In production, use proper embedding models.
        """
        try:
            if not text:
                return {'embeddings': [], 'dimension': 0, 'method': 'simplified'}
            
            # Simple character-based "embedding" for demonstration
            # In production, use sentence-transformers or similar
            text_lower = text.lower()
            
            # Create a simple feature vector
            features = {
                'length': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(re.split(r'[.!?]+', text)),
                'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
                'digit_ratio': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
                'special_char_ratio': sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
            }
            
            # Convert to list
            embedding = list(features.values())
            
            return {
                'embeddings': embedding,
                'dimension': len(embedding),
                'method': 'simplified_features',
                'features': features
            }
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return {'embeddings': [], 'dimension': 0, 'error': str(e)}
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models."""
        return {
            'service': 'AI Models Service',
            'version': 'simplified',
            'available_models': [
                'translation (basic)',
                'entity_extraction (pattern_based)',
                'sentiment_analysis (keyword_based)',
                'text_classification (keyword_based)',
                'summarization (extractive)',
                'embeddings (simplified)'
            ],
            'note': 'This is a simplified version without heavy ML dependencies'
        } 