"""
Reference validation tool for vendor risk analysis agent.
"""

import logging
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup

from .tools import validate_url, scrape_and_extract_vendor_data

logger = logging.getLogger(__name__)

def validate_reference(url: str, research_intent: str) -> Dict[str, Any]:
    """
    Validates a reference URL, extracts its content, and calculates relevance to research intent.
    
    Args:
        url: URL to validate and analyze
        research_intent: Description of the research topic to calculate relevance against
        
    Returns:
        Dict[str, Any]: Validation results including content extraction and relevance score
    """
    logger.info(f"Validating reference: {url} for research intent: {research_intent}")
    
    # Step 1: Validate the URL
    validation_result = validate_url(url)
    
    # If URL is not valid, return early with validation result
    if not validation_result.get("is_valid", False):
        validation_result["relevance_score"] = 0.0
        validation_result["content_summary"] = ""
        return validation_result
    
    # Step 2: Extract content if URL is valid
    try:
        # Get the full content
        content_result = scrape_and_extract_vendor_data(url)
        
        # Extract the main content from the result
        if content_result.get("status") == "success":
            raw_content = content_result.get("content", "")
            title = content_result.get("title", "")
            
            # Step 3: Calculate relevance score based on content and research intent
            relevance_score = calculate_relevance_score(raw_content, research_intent)
            
            # Create a summary of the content (first 500 characters)
            content_summary = raw_content[:500] + "..." if len(raw_content) > 500 else raw_content
            
            # Return the combined result
            return {
                "url": url,
                "is_valid": True,
                "status": "success",
                "title": title,
                "relevance_score": relevance_score,
                "content_summary": content_summary,
                "details": "URL is valid and content was successfully extracted"
            }
        else:
            # Content extraction failed
            return {
                "url": url,
                "is_valid": True,
                "status": "partial_success",
                "relevance_score": 0.0,
                "content_summary": "",
                "details": f"URL is valid but content extraction failed: {content_result.get('error', 'Unknown error')}"
            }
    except Exception as e:
        # Handle any exceptions during content extraction
        return {
            "url": url,
            "is_valid": True,
            "status": "partial_success",
            "relevance_score": 0.0,
            "content_summary": "",
            "details": f"URL is valid but an error occurred during content analysis: {str(e)}"
        }

def calculate_relevance_score(content: str, research_intent: str) -> float:
    """
    Calculates a relevance score between the content and research intent using cosine similarity.
    
    Args:
        content: The extracted content from the URL
        research_intent: Description of the research topic
        
    Returns:
        float: Relevance score between 0.0 and 1.0
    """
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Handle empty content
    if not content or not research_intent:
        return 0.0
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the content and research intent
    # We need to provide a list of documents to the vectorizer
    tfidf_matrix = vectorizer.fit_transform([content, research_intent])
    
    # Calculate cosine similarity between the content and research intent
    # The result is a 2x2 matrix, we want the similarity between the two documents
    # which is at position [0, 1] or [1, 0]
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Ensure the score is between 0 and 1
    similarity = max(0.0, min(1.0, similarity))
    
    # Adjust the score to give more weight to longer, more comprehensive content
    # but only if the similarity is already decent
    if similarity > 0.3:
        # Length factor: longer content gets a bonus, up to a point
        length_factor = min(1.0, len(content) / 5000)  # Normalize by expected length
        
        # Combine similarity with length factor (80% similarity, 20% length)
        combined_score = (similarity * 0.8) + (length_factor * 0.2)
    else:
        # For low similarity content, don't give length bonuses
        combined_score = similarity
    
    return round(combined_score, 2)  # Round to 2 decimal places

def validate_references_batch(urls: List[str], research_intent: str) -> Dict[str, Any]:
    """
    Validates multiple reference URLs in batch, extracting content and calculating relevance.
    
    Args:
        urls: List of URLs to validate and analyze
        research_intent: Description of the research topic to calculate relevance against
        
    Returns:
        Dict[str, Any]: Results containing valid references, invalid references, and validation details
    """
    logger.info(f"Validating {len(urls)} references for research intent: {research_intent}")
    
    valid_references = []
    invalid_references = []
    validation_details = {}
    
    # Process each URL in the list
    for url in urls:
        # Skip empty URLs
        if not url or not url.strip():
            continue
            
        # Validate the reference
        validation_result = validate_reference(url, research_intent)
        
        # Store the validation details
        validation_details[url] = validation_result
        
        # Add to appropriate list based on validation result
        if validation_result.get("is_valid", False):
            valid_references.append({
                "url": url,
                "title": validation_result.get("title", ""),
                "relevance_score": validation_result.get("relevance_score", 0.0),
                "content_summary": validation_result.get("content_summary", "")
            })
        else:
            invalid_references.append({
                "url": url,
                "details": validation_result.get("details", "Unknown error")
            })
    
    return {
        "status": "success",
        "valid_references": valid_references,
        "invalid_references": invalid_references,
        "validation_details": validation_details,
        "total_urls": len(urls),
        "valid_count": len(valid_references),
        "invalid_count": len(invalid_references)
    }
