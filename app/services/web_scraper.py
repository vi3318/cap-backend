"""
Web Scraper Service - Simplified Version
Intelligently scrapes legal information from reliable sources while respecting ethical guidelines
"""

import logging
import asyncio
import aiohttp
import requests
from typing import Dict, Any, List, Optional, Set
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
import random
import hashlib
import os
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, settings):
        self.settings = settings
        
        # Simple user agent strings
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Legal source domains (trusted legal websites)
        self.trusted_domains = {
            'indiankanoon.org': 'Indian Legal Database',
            'legislature.gov.in': 'Indian Legislature',
            'supremecourtofindia.nic.in': 'Supreme Court of India',
            'highcourtchd.gov.in': 'Chandigarh High Court',
            'bombayhighcourt.nic.in': 'Bombay High Court',
            'delhihighcourt.nic.in': 'Delhi High Court',
            'karnatakajudiciary.kar.nic.in': 'Karnataka High Court',
            'tamilnadu.nic.in': 'Tamil Nadu Government',
            'maharashtra.gov.in': 'Maharashtra Government',
            'gujarat.gov.in': 'Gujarat Government',
            'westbengal.gov.in': 'West Bengal Government',
            'legalserviceindia.com': 'Legal Services India',
            'lawfinderlive.com': 'Law Finder Live',
            'manupatra.com': 'Manupatra Legal Database',
            'scconline.com': 'SCC Online',
            'lexisnexis.com': 'LexisNexis',
            'westlaw.com': 'Westlaw',
            'justia.com': 'Justia',
            'cornell.edu': 'Cornell Legal Information Institute',
            'harvard.edu': 'Harvard Law School',
            'stanford.edu': 'Stanford Law School'
        }
        
        # Rate limiting and ethical scraping
        self.request_delay = 2  # seconds between requests
        self.max_requests_per_domain = 10
        self.request_counts = {}
        self.last_request_time = {}
        
        # Cache for scraped data
        self.cache_dir = Path("cache/web_scraping")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Legal information patterns
        self.legal_patterns = {
            'case_law': [
                r'case\s+(?:no\.?|number)?\s*[:\-]?\s*([A-Za-z0-9\/\-]+)',
                r'(?:supreme court|high court|district court)\s+of\s+([A-Za-z\s]+)',
                r'judgment\s+dated\s+([A-Za-z\s0-9,]+)',
                r'petitioner[:\-]?\s*([A-Za-z\s]+)',
                r'respondent[:\-]?\s*([A-Za-z\s]+)'
            ],
            'statutes': [
                r'(?:act|statute|regulation|rule)\s+(?:no\.?|number)?\s*[:\-]?\s*([A-Za-z0-9\/\-]+)',
                r'section\s+([0-9]+[A-Za-z]*)',
                r'article\s+([0-9]+[A-Za-z]*)',
                r'subsection\s+\(([0-9]+[A-Za-z]*)\)'
            ],
            'legal_terms': [
                r'\b(?:jurisdiction|venue|governing\s+law|applicable\s+law)\b',
                r'\b(?:arbitration|mediation|litigation|dispute\s+resolution)\b',
                r'\b(?:liability|indemnification|force\s+majeure|termination)\b'
            ]
        }
        
        logger.info("WebScraper initialized successfully (simplified version)")
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        return random.choice(self.user_agents)
    
    def _extract_year(self, text: str) -> str:
        """Extract year from text"""
        import re
        year_match = re.search(r'(19|20)\d{2}', text)
        return year_match.group() if year_match else ""
    
    async def _search_arxiv_api(self, topic: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Search arXiv using their API (more reliable than web scraping)
        """
        try:
            import xml.etree.ElementTree as ET
            
            # Prepare API query
            query = topic.replace(' ', '+AND+')
            api_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
            
            logger.info(f"🔬 Calling arXiv API: {api_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=30) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        
                        # Parse XML response
                        root = ET.fromstring(xml_content)
                        papers = []
                        
                        # Define namespace
                        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
                        
                        for entry in root.findall('atom:entry', ns):
                            try:
                                title = entry.find('atom:title', ns).text.strip()
                                
                                # Extract authors
                                authors = []
                                for author in entry.findall('atom:author', ns):
                                    name = author.find('atom:name', ns)
                                    if name is not None:
                                        authors.append(name.text)
                                
                                # Extract abstract
                                abstract_elem = entry.find('atom:summary', ns)
                                abstract = abstract_elem.text.strip() if abstract_elem is not None else ""
                                
                                # Extract URL
                                url = entry.find('atom:id', ns).text
                                
                                # Extract arXiv ID
                                arxiv_id = url.split('/')[-1]
                                
                                # Extract published date
                                published_elem = entry.find('atom:published', ns)
                                published = published_elem.text[:4] if published_elem is not None else ""
                                
                                # Extract categories
                                categories = []
                                for category in entry.findall('atom:category', ns):
                                    term = category.get('term')
                                    if term:
                                        categories.append(term)
                                
                                paper_info = {
                                    'title': title,
                                    'authors': ', '.join(authors),
                                    'abstract': abstract,
                                    'url': url,
                                    'arxiv_id': arxiv_id,
                                    'year': published,
                                    'categories': ', '.join(categories),
                                    'source': 'arXiv',
                                    'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                                }
                                
                                papers.append(paper_info)
                                
                            except Exception as e:
                                logger.warning(f"Error parsing arXiv entry: {e}")
                                continue
                        
                        logger.info(f"✅ arXiv API returned {len(papers)} papers")
                        return papers
                    else:
                        logger.warning(f"arXiv API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.warning(f"arXiv API failed: {e}")
            return []
    

    
    async def scrape_legal_information(self, query: str, jurisdiction: Optional[str] = None, 
                                     document_type: Optional[str] = None) -> Dict[str, Any]:
        """Main method to scrape legal information based on query"""
        try:
            logger.info(f"Starting legal information scraping for query: {query}")
            
            # Validate query
            if not query or len(query.strip()) < 3:
                raise ValueError("Query must be at least 3 characters long")
            
            # Check cache first
            cache_key = self._generate_cache_key(query, jurisdiction, document_type)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info("Returning cached result")
                return cached_result
            
            # Prepare search queries
            search_queries = self._prepare_search_queries(query, jurisdiction, document_type)
            
            # Scrape from multiple sources
            scraped_data = []
            for search_query in search_queries:
                try:
                    # Respect rate limiting
                    await self._respect_rate_limits()
                    
                    # Scrape from trusted sources
                    source_data = await self._scrape_from_trusted_sources(search_query)
                    if source_data:
                        scraped_data.extend(source_data)
                    
                    # Scrape from general legal sources
                    general_data = await self._scrape_from_general_sources(search_query)
                    if general_data:
                        scraped_data.extend(general_data)
                        
                except Exception as e:
                    logger.warning(f"Error scraping for query '{search_query}': {str(e)}")
                    continue
            
            # Process and structure scraped data
            processed_data = self._process_scraped_data(scraped_data, query)
            
            # Cache the result
            self._cache_result(cache_key, processed_data)
            
            logger.info(f"Legal information scraping completed. Found {len(processed_data['sources'])} sources")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error in legal information scraping: {str(e)}")
            raise
    
    def _prepare_search_queries(self, query: str, jurisdiction: Optional[str], 
                               document_type: Optional[str]) -> List[str]:
        """Prepare optimized search queries"""
        queries = [query]
        
        # Add jurisdiction-specific queries
        if jurisdiction:
            queries.append(f"{query} {jurisdiction}")
            queries.append(f"{jurisdiction} {query}")
        
        # Add document type-specific queries
        if document_type:
            queries.append(f"{query} {document_type}")
            queries.append(f"{document_type} {query}")
        
        # Add legal context
        legal_contexts = ['case law', 'statute', 'regulation', 'precedent', 'judgment']
        for context in legal_contexts:
            queries.append(f"{query} {context}")
        
        return list(set(queries))  # Remove duplicates
    
    async def _scrape_from_trusted_sources(self, query: str) -> List[Dict[str, Any]]:
        """Scrape from trusted legal sources"""
        scraped_data = []
        
        for domain, description in self.trusted_domains.items():
            try:
                # Check rate limits
                if not self._can_make_request(domain):
                    continue
                
                # Construct search URL
                search_url = self._construct_search_url(domain, query)
                if not search_url:
                    continue
                
                # Scrape the source
                source_data = await self._scrape_single_source(search_url, domain, description)
                if source_data:
                    scraped_data.append(source_data)
                
                # Update request tracking
                self._update_request_tracking(domain)
                
            except Exception as e:
                logger.warning(f"Error scraping from {domain}: {str(e)}")
                continue
        
        return scraped_data
    
    async def _scrape_from_general_sources(self, query: str) -> List[Dict[str, Any]]:
        """Scrape from general legal sources using search engines"""
        scraped_data = []
        
        try:
            # Use Google Scholar for legal research
            scholar_data = await self._scrape_google_scholar(query)
            if scholar_data:
                scraped_data.append(scholar_data)
            
            # Use general search engines
            search_data = await self._scrape_search_engines(query)
            if search_data:
                scraped_data.extend(search_data)
                
        except Exception as e:
            logger.warning(f"Error scraping from general sources: {str(e)}")
        
        return scraped_data
    
    async def _scrape_single_source(self, url: str, domain: str, description: str) -> Optional[Dict[str, Any]]:
        """Scrape a single source URL"""
        try:
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            async with requests.Session() as session:
                response = await session.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    html_content = response.text
                    
                    # Parse HTML
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract relevant information
                    extracted_data = self._extract_legal_information(soup, domain)
                    
                    if extracted_data:
                        return {
                            'source_url': url,
                            'domain': domain,
                            'description': description,
                            'title': extracted_data.get('title', ''),
                            'content': extracted_data.get('content', ''),
                            'legal_entities': extracted_data.get('legal_entities', {}),
                            'scraped_at': datetime.utcnow().isoformat(),
                            'relevance_score': self._calculate_relevance_score(query, extracted_data)
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_legal_information(self, soup: BeautifulSoup, domain: str) -> Dict[str, Any]:
        """Extract legal information from HTML content"""
        extracted_data = {
            'title': '',
            'content': '',
            'legal_entities': {}
        }
        
        try:
            # Extract title
            title_selectors = ['h1', 'h2', '.title', '.heading', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    extracted_data['title'] = title_elem.get_text().strip()
                    break
            
            # Extract main content
            content_selectors = [
                '.content', '.main-content', '.article-content', '.post-content',
                '.entry-content', '.text-content', 'article', '.legal-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    content_text = content_elem.get_text(separator=' ', strip=True)
                    if len(content_text) > 100:  # Minimum content length
                        extracted_data['content'] = content_text
                        break
            
            # Extract legal entities
            if extracted_data['content']:
                extracted_data['legal_entities'] = self._extract_entities_from_text(
                    extracted_data['content']
                )
            
            return extracted_data
            
        except Exception as e:
            logger.warning(f"Error extracting information from {domain}: {str(e)}")
            return extracted_data
    
    def _extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract legal entities from text content"""
        entities = {
            'case_numbers': [],
            'statutes': [],
            'courts': [],
            'dates': [],
            'parties': []
        }
        
        try:
            # Extract case numbers
            case_patterns = self.legal_patterns['case_law']
            for pattern in case_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['case_numbers'].extend(matches)
            
            # Extract statutes
            statute_patterns = self.legal_patterns['statutes']
            for pattern in statute_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['statutes'].extend(matches)
            
            # Extract dates
            date_patterns = [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
            ]
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                entities['dates'].extend(matches)
            
            # Extract courts
            court_patterns = [
                r'(?:supreme court|high court|district court|consumer court)\s+of\s+([A-Za-z\s]+)',
                r'([A-Za-z\s]+)\s+(?:supreme court|high court|district court)'
            ]
            for pattern in court_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['courts'].extend(matches)
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.warning(f"Error extracting entities: {str(e)}")
            return entities
    
    async def _scrape_google_scholar(self, query: str) -> Optional[Dict[str, Any]]:
        """Scrape legal research from Google Scholar"""
        try:
            # Note: In production, you'd use Google Scholar API or structured data
            # For now, return mock data
            return {
                'source_url': f"https://scholar.google.com/scholar?q={query}",
                'domain': 'scholar.google.com',
                'description': 'Google Scholar Legal Research',
                'title': f'Legal Research Results for: {query}',
                'content': f'Academic and legal research papers related to {query}',
                'legal_entities': {},
                'scraped_at': datetime.utcnow().isoformat(),
                'relevance_score': 0.8
            }
        except Exception as e:
            logger.warning(f"Error scraping Google Scholar: {str(e)}")
            return None
    
    async def _scrape_search_engines(self, query: str) -> List[Dict[str, Any]]:
        """Scrape from general search engines"""
        # Note: In production, you'd implement actual search engine scraping
        # For now, return mock data
        return []
    
    def _construct_search_url(self, domain: str, query: str) -> Optional[str]:
        """Construct search URL for a domain"""
        try:
            if 'indiankanoon.org' in domain:
                return f"https://indiankanoon.org/search/?formInput={query}"
            elif 'legislature.gov.in' in domain:
                return f"https://legislature.gov.in/search?q={query}"
            elif 'supremecourtofindia.nic.in' in domain:
                return f"https://supremecourtofindia.nic.in/search?q={query}"
            else:
                # Generic search URL construction
                return f"https://{domain}/search?q={query}"
        except Exception as e:
            logger.warning(f"Error constructing search URL for {domain}: {str(e)}")
            return None
    
    def _can_make_request(self, domain: str) -> bool:
        """Check if we can make a request to a domain"""
        current_time = time.time()
        
        # Check request count
        if domain in self.request_counts and self.request_counts[domain] >= self.max_requests_per_domain:
            return False
        
        # Check time delay
        if domain in self.last_request_time:
            time_since_last = current_time - self.last_request_time[domain]
            if time_since_last < self.request_delay:
                return False
        
        return True
    
    def _update_request_tracking(self, domain: str):
        """Update request tracking for a domain"""
        current_time = time.time()
        
        if domain not in self.request_counts:
            self.request_counts[domain] = 0
        self.request_counts[domain] += 1
        
        self.last_request_time[domain] = current_time
    
    async def _respect_rate_limits(self):
        """Respect rate limiting between requests"""
        await asyncio.sleep(self.request_delay + random.uniform(0, 1))
    
    def _calculate_relevance_score(self, query: str, extracted_data: Dict[str, Any]) -> float:
        """Calculate relevance score for scraped data"""
        try:
            score = 0.0
            content = extracted_data.get('content', '').lower()
            title = extracted_data.get('title', '').lower()
            query_terms = query.lower().split()
            
            # Title relevance
            for term in query_terms:
                if term in title:
                    score += 0.3
                if term in content:
                    score += 0.1
            
            # Content length relevance
            if len(content) > 500:
                score += 0.2
            
            # Legal entity relevance
            legal_entities = extracted_data.get('legal_entities', {})
            if any(legal_entities.values()):
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating relevance score: {str(e)}")
            return 0.0
    
    def _generate_cache_key(self, query: str, jurisdiction: Optional[str], 
                           document_type: Optional[str]) -> str:
        """Generate cache key for query results"""
        cache_string = f"{query}_{jurisdiction or 'any'}_{document_type or 'any'}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                # Check if cache is expired (24 hours)
                file_age = time.time() - cache_file.stat().st_mtime
                if file_age < 86400:  # 24 hours
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache: {str(e)}")
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache the scraping result"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            logger.warning(f"Error caching result: {str(e)}")
    
    async def get_scraping_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics and metrics"""
        try:
            return {
                'total_requests': sum(self.request_counts.values()),
                'domains_scraped': len(self.request_counts),
                'cache_size': len(list(self.cache_dir.glob('*.json'))),
                'last_activity': max(self.last_request_time.values()) if self.last_request_time else None,
                'rate_limited_domains': [domain for domain, count in self.request_counts.items() 
                                       if count >= self.max_requests_per_domain]
            }
        except Exception as e:
            logger.error(f"Error getting scraping statistics: {str(e)}")
            return {} 

    async def search_google_scholar(self, topic: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        ADVANCED Google Scholar scraper with multiple fallback strategies.
        """
        try:
            logger.info(f"🔍 Starting Google Scholar search for: {topic}")
            
            async with async_playwright() as p:
                # Launch browser with stealth settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=VizDisplayCompositor',
                        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]
                )
                
                page = await browser.new_page()
                
                # Advanced stealth settings
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                
                # Navigate to Google Scholar
                search_url = f"https://scholar.google.com/scholar?q={topic.replace(' ', '+')}&hl=en"
                logger.info(f"📡 Navigating to: {search_url}")
                
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for results with multiple selectors as fallback
                try:
                    await page.wait_for_selector('.gs_r, .gs_ri, [data-lid]', timeout=15000)
                except:
                    logger.warning("Primary selectors not found, trying alternative approach")
                    await page.wait_for_timeout(3000)
                
                papers = []
                
                # Try multiple selector strategies
                selectors_to_try = ['.gs_r', '.gs_ri', '[data-lid]']
                paper_elements = []
                
                for selector in selectors_to_try:
                    paper_elements = await page.query_selector_all(selector)
                    if paper_elements:
                        logger.info(f"✅ Found {len(paper_elements)} papers using selector: {selector}")
                        break
                
                if not paper_elements:
                    logger.warning("No papers found with any selector")
                    await browser.close()
                    return []
                
                for i, element in enumerate(paper_elements[:max_results]):
                    try:
                        # Multiple strategies for title extraction
                        title_selectors = ['.gs_rt a', '.gs_rt', 'h3 a', 'h3']
                        title = ""
                        url = ""
                        
                        for title_selector in title_selectors:
                            title_element = await element.query_selector(title_selector)
                            if title_element:
                                title = await title_element.inner_text()
                                if 'a' in title_selector:
                                    url = await title_element.get_attribute('href') or ""
                                break
                        
                        if not title:
                            continue
                            
                        # Extract authors with fallbacks
                        authors_selectors = ['.gs_a', '.gs_gray', '.gs_metadata']
                        authors = ""
                        for auth_selector in authors_selectors:
                            authors_element = await element.query_selector(auth_selector)
                            if authors_element:
                                authors = await authors_element.inner_text()
                                break
                        
                        # Extract abstract with fallbacks
                        abstract_selectors = ['.gs_rs', '.gs_snippet', '.gs_abstract']
                        abstract = ""
                        for abs_selector in abstract_selectors:
                            abstract_element = await element.query_selector(abs_selector)
                            if abstract_element:
                                abstract = await abstract_element.inner_text()
                                break
                        
                        # Extract citations
                        citations = ""
                        citation_selectors = ['.gs_fl a', '.gs_nph a', '.gs_citedby']
                        for cit_selector in citation_selectors:
                            citations_element = await element.query_selector(cit_selector)
                            if citations_element:
                                citations_text = await citations_element.inner_text()
                                if "Cited by" in citations_text or "cited by" in citations_text.lower():
                                    citations = citations_text
                                    break
                        
                        # Extract PDF link
                        pdf_selectors = ['.gs_or_ggsm a', '.gs_ggsd a', '[href*=".pdf"]']
                        pdf_url = None
                        for pdf_selector in pdf_selectors:
                            pdf_element = await element.query_selector(pdf_selector)
                            if pdf_element:
                                pdf_url = await pdf_element.get_attribute('href')
                                break
                        
                        paper_info = {
                            'title': title.strip(),
                            'authors': authors.strip(),
                            'abstract': abstract.strip(),
                            'url': url,
                            'citations': citations,
                            'pdf_url': pdf_url,
                            'source': 'Google Scholar',
                            'year': self._extract_year(authors)
                        }
                        
                        papers.append(paper_info)
                        logger.info(f"✅ Extracted paper {i+1}: {title[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Error extracting paper {i}: {e}")
                        continue
                
                await browser.close()
                logger.info(f"🎉 Google Scholar search completed: {len(papers)} papers found")
                return papers
                
        except Exception as e:
            logger.error(f"❌ Error in Google Scholar search: {e}")
            return []
    
    async def search_arxiv(self, topic: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        ADVANCED arXiv scraper with API fallback and multiple strategies.
        """
        try:
            logger.info(f"🔬 Starting arXiv search for: {topic}")
            
            # First try the arXiv API (more reliable)
            papers = await self._search_arxiv_api(topic, max_results)
            if papers:
                logger.info(f"✅ arXiv API returned {len(papers)} papers")
                return papers
            
            # Fallback to web scraping
            logger.info("📡 Falling back to arXiv web scraping")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                page = await browser.new_page()
                
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Try multiple arXiv search strategies
                search_urls = [
                    f"https://arxiv.org/search/?query={topic.replace(' ', '+')}&searchtype=all&source=header&start=0&size={max_results}",
                    f"https://arxiv.org/search/cs?query={topic.replace(' ', '+')}&searchtype=all&source=header&start=0&size={max_results}",
                    f"https://arxiv.org/search/stat?query={topic.replace(' ', '+')}&searchtype=all&source=header&start=0&size={max_results}"
                ]
                
                papers = []
                for search_url in search_urls:
                    try:
                        logger.info(f"📡 Trying arXiv URL: {search_url}")
                        await page.goto(search_url, wait_until='networkidle', timeout=30000)
                        
                        # Wait for results with multiple selectors
                        selectors = ['.arxiv-result', 'li.arxiv-result', 'ol li', '.result-item']
                        paper_elements = []
                        
                        for selector in selectors:
                            try:
                                await page.wait_for_selector(selector, timeout=5000)
                                paper_elements = await page.query_selector_all(selector)
                                if paper_elements:
                                    logger.info(f"✅ Found {len(paper_elements)} papers using selector: {selector}")
                                    break
                            except:
                                continue
                        
                        if paper_elements:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to load {search_url}: {e}")
                        continue
                
                if not paper_elements:
                    logger.warning("No arXiv papers found with any strategy")
                    await browser.close()
                    return []
                
                for i, element in enumerate(paper_elements[:max_results]):
                    try:
                        # Multiple strategies for title extraction
                        title_selectors = ['p.title a', '.title a', 'h4 a', '.list-title a']
                        title = ""
                        url = ""
                        
                        for title_selector in title_selectors:
                            title_element = await element.query_selector(title_selector)
                            if title_element:
                                title = await title_element.inner_text()
                                url = await title_element.get_attribute('href')
                                if url and not url.startswith('http'):
                                    url = f"https://arxiv.org{url}"
                                break
                        
                        if not title:
                            continue
                        
                        # Clean title
                        title = title.replace('Title:', '').strip()
                        
                        # Extract authors with fallbacks
                        authors_selectors = ['p.authors', '.authors', '.list-authors']
                        authors = ""
                        for auth_selector in authors_selectors:
                            authors_element = await element.query_selector(auth_selector)
                            if authors_element:
                                authors = await authors_element.inner_text()
                                authors = authors.replace('Authors:', '').strip()
                                break
                        
                        # Extract abstract with fallbacks
                        abstract_selectors = ['span.abstract-full', '.abstract', 'p.abstract', '.list-abstract']
                        abstract = ""
                        for abs_selector in abstract_selectors:
                            abstract_element = await element.query_selector(abs_selector)
                            if abstract_element:
                                abstract = await abstract_element.inner_text()
                                abstract = abstract.replace('Abstract:', '').strip()
                                break
                        
                        # Extract arXiv ID from URL
                        arxiv_id = ""
                        if url:
                            import re
                            id_match = re.search(r'arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5})', url)
                            if id_match:
                                arxiv_id = id_match.group(1)
                        
                        # Extract subject/category
                        subject_selectors = ['.primary-subject', '.list-subject', '.tags']
                        subject = ""
                        for subj_selector in subject_selectors:
                            subject_element = await element.query_selector(subj_selector)
                            if subject_element:
                                subject = await subject_element.inner_text()
                                break
                        
                        paper_info = {
                            'title': title.strip(),
                            'authors': authors.strip(),
                            'abstract': abstract.strip(),
                            'url': url,
                            'arxiv_id': arxiv_id,
                            'subject': subject,
                            'source': 'arXiv',
                            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None
                        }
                        
                        papers.append(paper_info)
                        logger.info(f"✅ Extracted arXiv paper {i+1}: {title[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Error extracting arXiv paper {i}: {e}")
                        continue
                
                await browser.close()
                logger.info(f"🎉 arXiv search completed: {len(papers)} papers found")
                return papers
                
        except Exception as e:
            logger.error(f"❌ Error in arXiv search: {e}")
            return []
    
    async def search_pubmed(self, topic: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        RELIABLE PubMed search using their robust API - Perfect replacement for Semantic Scholar.
        """
        try:
            logger.info(f"🔬 Starting PubMed search for: {topic}")
            
            # PubMed E-utilities API (very reliable and free)
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            
            # Search for paper IDs
            search_params = {
                'db': 'pubmed',
                'term': topic,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance',
                'tool': 'ResearchDocAI',
                'email': 'research@example.com'
            }
            
            async with aiohttp.ClientSession() as session:
                # Get paper IDs
                async with session.get(search_url, params=search_params, timeout=30) as response:
                    if response.status != 200:
                        logger.warning(f"PubMed search failed with status {response.status}")
                        return []
                    
                    search_data = await response.json()
                    id_list = search_data.get('esearchresult', {}).get('idlist', [])
                    
                    if not id_list:
                        logger.warning("No PubMed papers found")
                        return []
                    
                    logger.info(f"📄 Found {len(id_list)} PubMed paper IDs")
                    
                    # Fetch paper details
                    fetch_params = {
                        'db': 'pubmed',
                        'id': ','.join(id_list),
                        'retmode': 'xml',
                        'rettype': 'abstract',
                        'tool': 'ResearchDocAI',
                        'email': 'research@example.com'
                    }
                    
                    async with session.get(fetch_url, params=fetch_params, timeout=30) as fetch_response:
                        if fetch_response.status != 200:
                            logger.warning(f"PubMed fetch failed with status {fetch_response.status}")
                            return []
                        
                        xml_content = await fetch_response.text()
                        papers = self._parse_pubmed_xml(xml_content)
                        
                        logger.info(f"✅ PubMed search completed: {len(papers)} papers found")
                        return papers
                        
        except Exception as e:
            logger.error(f"❌ Error in PubMed search: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, str]]:
        """Parse PubMed XML response into paper data"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            papers = []
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    # Extract title
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    # Extract authors
                    authors = []
                    author_list = article.find('.//AuthorList')
                    if author_list is not None:
                        for author in author_list.findall('.//Author'):
                            lastname = author.find('.//LastName')
                            forename = author.find('.//ForeName')
                            if lastname is not None:
                                name = lastname.text
                                if forename is not None:
                                    name = f"{forename.text} {name}"
                                authors.append(name)
                    
                    # Extract abstract
                    abstract_elem = article.find('.//Abstract/AbstractText')
                    abstract = abstract_elem.text if abstract_elem is not None else ""
                    
                    # Extract journal and year
                    journal_elem = article.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else ""
                    
                    year_elem = article.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else ""
                    
                    # Extract PMID for URL
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ""
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                    
                    # Extract DOI if available
                    doi = ""
                    for article_id in article.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'doi':
                            doi = article_id.text
                            break
                    
                    paper_info = {
                        'title': title.strip(),
                        'authors': ', '.join(authors),
                        'abstract': abstract.strip() if abstract else "",
                        'url': url,
                        'pmid': pmid,
                        'doi': doi,
                        'journal': journal,
                        'year': year,
                        'source': 'PubMed'
                    }
                    
                    papers.append(paper_info)
                    
                except Exception as e:
                    logger.warning(f"Error parsing PubMed article: {e}")
                    continue
            
            return papers
            
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            return []
    
    async def search_multiple_sources(self, topic: str, max_results_per_source: int = 5) -> Dict[str, List[Dict[str, str]]]:
        """
        ADVANCED multi-source search with intelligent error handling and performance optimization.
        """
        try:
            logger.info(f"🚀 Starting multi-source search for: {topic}")
            
            # Create tasks with timeout and retry logic
            async def safe_search(search_func, source_name, topic, max_results):
                """Wrapper function with retry logic and error handling"""
                max_retries = 2
                for attempt in range(max_retries + 1):
                    try:
                        logger.info(f"🔄 Attempt {attempt + 1} for {source_name}")
                        result = await asyncio.wait_for(
                            search_func(topic, max_results), 
                            timeout=45.0  # 45 second timeout per source
                        )
                        if result:
                            logger.info(f"✅ {source_name} successful: {len(result)} papers")
                            return result
                        else:
                            logger.warning(f"⚠️ {source_name} returned empty results")
                            if attempt < max_retries:
                                await asyncio.sleep(2)  # Wait before retry
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"⏰ {source_name} timed out on attempt {attempt + 1}")
                        if attempt < max_retries:
                            await asyncio.sleep(3)
                    except Exception as e:
                        logger.error(f"❌ {source_name} failed on attempt {attempt + 1}: {e}")
                        if attempt < max_retries:
                            await asyncio.sleep(2)
                
                logger.error(f"💥 {source_name} failed after all retries")
                return []
            
            # Run searches concurrently with intelligent scheduling
            tasks = [
                safe_search(self.search_google_scholar, "Google Scholar", topic, max_results_per_source),
                safe_search(self.search_arxiv, "arXiv", topic, max_results_per_source),
                safe_search(self.search_pubmed, "PubMed", topic, max_results_per_source)
            ]
            
            # Execute with overall timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=120.0  # 2 minute overall timeout
            )
            
            # Process results with detailed error tracking
            source_names = ['google_scholar', 'arxiv', 'pubmed']
            processed_results = {}
            successful_sources = 0
            error_details = {}
            
            for i, (source, result) in enumerate(zip(source_names, results)):
                if isinstance(result, Exception):
                    logger.error(f"❌ {source} failed with exception: {result}")
                    processed_results[source] = []
                    error_details[source] = str(result)
                elif isinstance(result, list) and len(result) > 0:
                    processed_results[source] = result
                    successful_sources += 1
                    logger.info(f"✅ {source} completed successfully: {len(result)} papers")
                else:
                    processed_results[source] = []
                    error_details[source] = "No results found"
                    logger.warning(f"⚠️ {source} returned no results")
            
            # Calculate comprehensive statistics
            total_papers = sum(len(papers) for papers in processed_results.values() if isinstance(papers, list))
            unique_titles = set()
            for papers in processed_results.values():
                if isinstance(papers, list):
                    for paper in papers:
                        if isinstance(paper, dict) and 'title' in paper:
                            unique_titles.add(paper['title'].lower().strip())
            
            # Add enhanced summary with performance metrics
            processed_results['summary'] = {
                'total_papers_found': total_papers,
                'unique_papers_estimate': len(unique_titles),
                'sources_searched': len(source_names),
                'sources_successful': successful_sources,
                'success_rate': f"{(successful_sources/len(source_names)*100):.1f}%",
                'search_topic': topic,
                'timestamp': time.time(),
                'search_quality': 'excellent' if successful_sources >= 3 else 'good' if successful_sources >= 2 else 'limited',
                'error_details': error_details if error_details else None
            }
            
            logger.info(f"🎉 Multi-source search completed: {total_papers} total papers, {successful_sources}/{len(source_names)} sources successful")
            return processed_results
            
        except asyncio.TimeoutError:
            logger.error("⏰ Multi-source search timed out")
            return {
                'google_scholar': [],
                'arxiv': [],
                'pubmed': [],
                'summary': {
                    'total_papers_found': 0,
                    'sources_searched': 3,
                    'sources_successful': 0,
                    'success_rate': '0%',
                    'search_topic': topic,
                    'timestamp': time.time(),
                    'search_quality': 'failed',
                    'error': 'Search operation timed out'
                }
            }
        except Exception as e:
            logger.error(f"💥 Critical error in multi-source search: {e}")
            return {
                'google_scholar': [],
                'arxiv': [],
                'pubmed': [],
                'summary': {
                    'total_papers_found': 0,
                    'sources_searched': 3,
                    'sources_successful': 0,
                    'success_rate': '0%',
                    'search_topic': topic,
                    'timestamp': time.time(),
                    'search_quality': 'failed',
                    'error': str(e)
                }
            }

    async def scrape_legal_info(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Scrape legal information from trusted sources.
        """
        # ... existing code ... 