"""Tools module for the vendor risk analysis agent."""

import os
import logging
import requests
import validators
import markdown
import tempfile
import uuid
import io
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from ..config import Config

# HTML generation imports
from jinja2 import Environment, FileSystemLoader

# Google Cloud Storage imports
from google.cloud import storage
from google.auth import default

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Create MCP toolset with proper configuration for HTTP connection
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=configs.MCP_SERVER_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        timeout=30
    )
)

def scrape_and_extract_vendor_data(url: str) -> Dict[str, Any]:
    """Scrapes a vendor's website and returns the raw content for LLM analysis.
    
    Args:
        url: URL of the vendor's website to analyze
        
    Returns:
        Dict[str, Any]: Raw content for the LLM to analyze
    """
    logger.info(f"Scraping vendor website from {url}")
    
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        website_text = soup.get_text(separator='\n', strip=True)
        
        # Return the raw text for the LLM to analyze
        result = {
            "url": url,
            "website_text": website_text,
            "status": "success"
        }
        
        logger.info("Successfully scraped vendor website")
        return result
        
    except Exception as e:
        logger.error(f"Error scraping vendor website: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "status": "error"
        }

def get_valid_references(urls: List[str]) -> Dict[str, Any]:
    """
    Validates a list of URLs and returns only the valid ones.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Dict[str, Any]: Results containing valid URLs, invalid URLs, and validation details
    """
    logger.info(f"Validating {len(urls)} URLs")
    
    valid_urls = []
    invalid_urls = []
    validation_details = {}
    
    # Process each URL in the list
    for url in urls:
        # Skip empty URLs
        if not url or not url.strip():
            continue
            
        # Validate the URL
        validation_result = validate_url(url)
        
        # Store the validation details
        validation_details[url] = validation_result
        
        # Add to appropriate list based on validation result
        if validation_result.get("is_valid", False):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    return {
        "status": "success",
        "valid_urls": valid_urls,
        "invalid_urls": invalid_urls,
        "validation_details": validation_details,
        "total_urls": len(urls),
        "valid_count": len(valid_urls),
        "invalid_count": len(invalid_urls)
    }

def validate_url(url: str) -> Dict[str, Any]:
    """
    Validates if a URL is properly formatted and accessible.

    Args:
        url: URL to validate
        
    Returns:
        Dict[str, Any]: Validation results including status and details
    """
    logger.info(f"Validating URL: {url}")
    
    result = {
        "url": url,
        "is_valid": False,
        "status": "error",
        "details": ""
    }
    
    # Check if URL format is valid
    if not validators.url(url):
        result["details"] = "Invalid URL format. Please provide a complete URL including http:// or https://"
        return result
    
    # Check if domain exists and URL is accessible
    try:
        # Parse URL to get domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Attempt to connect to the URL
        response = requests.head(url, timeout=10)
        
        # Check if response is successful
        if response.status_code < 400:
            result["is_valid"] = True
            result["status"] = "success"
            result["details"] = f"URL is valid and accessible. Status code: {response.status_code}"
            result["domain"] = domain
        else:
            result["details"] = f"URL exists but returned an error. Status code: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        result["details"] = "Could not connect to the URL. Please check if the domain exists and is accessible."
    except requests.exceptions.Timeout:
        result["details"] = "Connection timed out. The server might be slow or unavailable."
    except requests.exceptions.RequestException as e:
        result["details"] = f"An error occurred while accessing the URL: {str(e)}"
    
    logger.info(f"URL validation result: {result['status']} - {result['details']}")
    return result

# The MCP toolset automatically provides access to all tools exposed by the MCP server
# For example: mcp_toolset.get_risk_questions(), mcp_toolset.search_web(), etc.

def generate_html_report(report_content: str, vendor_name: str) -> Dict[str, Any]:
    """
    Generates a beautifully formatted HTML report from markdown content and uploads it to Google Cloud Storage.
    
    Args:
        report_content: The markdown content of the report
        vendor_name: The name of the vendor for the report title
        
    Returns:
        Dict[str, Any]: Information about the generated HTML report including the public download URL
    """
    logger.info(f"Generating HTML report for {vendor_name}")
    
    try:
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Create a basic HTML template for the PDF
        template_path = os.path.join(templates_dir, 'report_template.html')
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write('''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{{ title }}</title>
                    <style>
                        @page {
                            margin: 1cm;
                            @top-center {
                                content: "Vendor Risk Assessment Report";
                                font-family: Arial, sans-serif;
                                font-size: 10pt;
                            }
                            @bottom-center {
                                content: "Page " counter(page) " of " counter(pages);
                                font-family: Arial, sans-serif;
                                font-size: 10pt;
                            }
                        }
                        body {
                            font-family: Arial, sans-serif;
                            font-size: 12pt;
                            line-height: 1.5;
                            color: #333;
                        }
                        h1 {
                            color: #2c3e50;
                            font-size: 24pt;
                            text-align: center;
                            margin-top: 20pt;
                            margin-bottom: 20pt;
                            border-bottom: 1pt solid #2c3e50;
                            padding-bottom: 10pt;
                        }
                        h2 {
                            color: #2980b9;
                            font-size: 18pt;
                            margin-top: 15pt;
                            margin-bottom: 10pt;
                            border-bottom: 0.5pt solid #bdc3c7;
                            padding-bottom: 5pt;
                        }
                        h3 {
                            color: #3498db;
                            font-size: 14pt;
                            margin-top: 10pt;
                            margin-bottom: 5pt;
                        }
                        p {
                            margin-bottom: 10pt;
                        }
                        ul, ol {
                            margin-bottom: 10pt;
                        }
                        table {
                            width: 100%;
                            border-collapse: collapse;
                            margin-bottom: 15pt;
                        }
                        th, td {
                            border: 1pt solid #bdc3c7;
                            padding: 8pt;
                            text-align: left;
                        }
                        th {
                            background-color: #f2f2f2;
                        }
                        .executive-summary {
                            background-color: #f8f9fa;
                            padding: 10pt;
                            border-left: 4pt solid #2980b9;
                            margin-bottom: 15pt;
                        }
                        .recommendations {
                            background-color: #f8f9fa;
                            padding: 10pt;
                            border-left: 4pt solid #27ae60;
                            margin-bottom: 15pt;
                        }
                        .references {
                            font-size: 10pt;
                            line-height: 1.3;
                        }
                        .header {
                            text-align: center;
                            margin-bottom: 20pt;
                        }
                        .header img {
                            max-width: 150pt;
                            margin-bottom: 10pt;
                        }
                        .date {
                            color: #7f8c8d;
                            font-size: 10pt;
                            text-align: right;
                            margin-bottom: 20pt;
                        }
                        .footer {
                            text-align: center;
                            font-size: 10pt;
                            color: #7f8c8d;
                            margin-top: 30pt;
                            border-top: 0.5pt solid #bdc3c7;
                            padding-top: 10pt;
                        }
                        a {
                            color: #3498db;
                            text-decoration: underline;
                            word-wrap: break-word;
                        }
                        a:hover {
                            color: #2980b9;
                            text-decoration: underline;
                        }
                        .references-section {
                            margin-top: 20pt;
                        }
                        .reference-item {
                            margin-bottom: 8pt;
                            padding-left: 10pt;
                        }
                        .reference-link, .external-link {
                            color: #2980b9;
                            text-decoration: underline;
                            word-break: break-all;
                            max-width: 100%;
                            font-weight: 500;
                        }
                        .reference-link:hover, .external-link:hover {
                            color: #3498db;
                            text-decoration: underline;
                        }
                        .validated {
                            color: #27ae60;
                            font-weight: bold;
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{{ title }}</h1>
                    </div>
                    
                    <div class="date">
                        Generated on: {{ date }}
                    </div>
                    
                    <div class="content">
                        {{ content|safe }}
                    </div>
                    
                    <div class="footer">
                        This report was automatically generated by the Vendor Risk Analysis System.
                        <br>
                        Confidential - For internal use only.
                    </div>
                </body>
                </html>
                ''')
        
        # Convert markdown to HTML with enhanced link handling
        html_content = markdown.markdown(
            report_content, 
            extensions=[
                'tables', 
                'fenced_code',
                'markdown.extensions.extra',  # Includes many useful extensions
                'markdown.extensions.attr_list',  # Allows adding attributes to elements
                'markdown.extensions.smarty'  # Smart quotes, dashes, etc.
            ]
        )
        
        # Post-process HTML to ensure reference links are properly formatted and remove duplicate title
        import re
        
        # Remove the title from the markdown content to prevent duplication
        # The title is already included in the HTML template header
        title_pattern = rf'^# Vendor Risk Assessment Report: {re.escape(vendor_name)}\s*\n'
        report_content = re.sub(title_pattern, '', report_content, flags=re.MULTILINE)
        
        # First, ensure all URLs in the markdown are properly formatted as links
        # Look for patterns like [title](url) that might be missing
        url_pattern = r'(\[.*?\]:\s*)(https?://[^\s]+)'
        report_content = re.sub(url_pattern, r'\1[\2](\2)', report_content)
        
        # Also look for plain URLs that should be links
        plain_url_pattern = r'(?<!\()(?<!\[)(https?://[^\s\)]+)(?!\))(?!\])'
        report_content = re.sub(plain_url_pattern, r'[\1](\1)', report_content)
        
        # Now convert to HTML with enhanced link handling
        html_content = markdown.markdown(
            report_content, 
            extensions=[
                'tables', 
                'fenced_code',
                'markdown.extensions.extra',  # Includes many useful extensions
                'markdown.extensions.attr_list',  # Allows adding attributes to elements
                'markdown.extensions.smarty',  # Smart quotes, dashes, etc.
                'markdown.extensions.nl2br',  # Convert newlines to <br>
                'markdown.extensions.sane_lists'  # Better list handling
            ]
        )
        
        # Additional post-processing with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove the first H1 tag if it contains the vendor name to prevent duplicate title
        first_h1 = soup.find('h1')
        if first_h1 and vendor_name in first_h1.text and 'Vendor Risk Assessment Report' in first_h1.text:
            first_h1.decompose()
        
        # Find the references section
        references_section = None
        for h2 in soup.find_all('h2'):
            if 'Validated References' in h2.text or 'References' in h2.text:
                references_section = h2
                break
        
        if references_section:
            # Add a special class to the references section
            references_div = soup.new_tag('div')
            references_div['class'] = 'references-section'
            references_section.wrap(references_div)
            
            # Process all paragraphs after the references heading
            current = references_section.find_next()
            while current and (current.name != 'h2'):
                if current.name == 'p':
                    # Check if this paragraph contains a reference
                    if current.text and ('[' in current.text or 'http' in current.text):
                        # Add a references class to this paragraph
                        current['class'] = current.get('class', []) + ['reference-item']
                        
                        # Find URLs that aren't already in anchor tags
                        for text_node in current.find_all(text=True):
                            if 'http' in text_node:
                                # Find all URLs in this text node
                                urls = re.findall(r'https?://[^\s\)\]]+', text_node)
                                if urls:
                                    # Replace the text node with new content
                                    new_content = text_node
                                    for url in urls:
                                        # Only replace if not already in an anchor
                                        if not any(url in str(a) for a in current.find_all('a')):
                                            link = soup.new_tag('a')
                                            link['href'] = url
                                            link['target'] = '_blank'  # Open in new tab
                                            link['class'] = 'reference-link'
                                            link.string = url
                                            new_content = new_content.replace(url, str(link))
                                    # Replace the text node
                                    if new_content != text_node:
                                        new_soup = BeautifulSoup(new_content, 'html.parser')
                                        text_node.replace_with(new_soup)
                
                current = current.find_next()
        
        # Ensure all links have target="_blank" and proper styling
        for a in soup.find_all('a'):
            a['target'] = '_blank'
            if 'class' not in a.attrs or 'reference-link' not in a['class']:
                a['class'] = a.get('class', []) + ['external-link']
        
        # Convert back to HTML string
        html_content = str(soup)
        
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('report_template.html')
        
        # Render the template with our content
        rendered_html = template.render(
            title=f"Vendor Risk Assessment Report: {vendor_name}",
            date=datetime.now().strftime("%B %d, %Y"),
            content=html_content
        )
        
        # Create a unique filename for the HTML report
        report_id = str(uuid.uuid4())[:8]
        sanitized_vendor_name = vendor_name.replace(' ', '_').replace('/', '_').lower()
        html_filename = f"{sanitized_vendor_name}_{report_id}_risk_assessment.html"
        
        # First create a local temporary file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_file:
            temp_html_path = temp_file.name
            
        # Write the HTML to the temporary file
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        # Upload to Google Cloud Storage
        try:
            # Initialize GCS client
            storage_client = storage.Client(project=configs.GCP_PROJECT or configs.CLOUD_PROJECT)
            
            # Get the bucket
            bucket_name = configs.GCS_BUCKET_NAME
            try:
                bucket = storage_client.get_bucket(bucket_name)
            except Exception as e:
                logger.info(f"Bucket {bucket_name} does not exist, creating it...")
                bucket = storage_client.create_bucket(bucket_name, location=configs.CLOUD_LOCATION)
            
            # Define the path in the bucket
            gcs_folder = configs.GCS_PDF_FOLDER  # Reusing the same folder config
            gcs_path = f"{gcs_folder}/{html_filename}" if gcs_folder else html_filename
            
            # Upload the file
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(temp_html_path)
            
            # Set the content type to HTML
            blob.content_type = 'text/html'
            
            # Make the file publicly accessible
            blob.make_public()
            
            # Get the public URL
            public_url = blob.public_url
            
            # Clean up the temporary file
            os.unlink(temp_html_path)
            
            logger.info(f"Successfully uploaded HTML report to GCS: {public_url}")
            
            # Format the URL using the template from config if available
            if configs.GCS_PDF_PUBLIC_URL:  # Reusing the same config
                public_url = configs.GCS_PDF_PUBLIC_URL.format(
                    bucket_name=bucket_name,
                    folder=gcs_folder,
                    filename=html_filename
                )
            
            return {
                "status": "success",
                "filename": html_filename,
                "report_id": report_id,
                "bucket_name": bucket_name,
                "gcs_path": gcs_path,
                "download_url": public_url,
                "message": "HTML report generated and uploaded to Google Cloud Storage"
            }
            
        except Exception as gcs_error:
            logger.error(f"Error uploading to GCS: {str(gcs_error)}")
            
            # Fall back to local storage if GCS upload fails
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
            os.makedirs(output_dir, exist_ok=True)
            
            html_path = os.path.join(output_dir, html_filename)
            os.rename(temp_html_path, html_path)
            
            logger.info(f"Fallback: Generated HTML report locally at {html_path}")
            return {
                "status": "partial_success",
                "html_path": html_path,
                "filename": html_filename,
                "report_id": report_id,
                "download_url": f"file://{html_path}",
                "message": "HTML report generated locally (GCS upload failed)",
                "error": str(gcs_error)
            }
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "details": "Failed to generate HTML report"
        }
