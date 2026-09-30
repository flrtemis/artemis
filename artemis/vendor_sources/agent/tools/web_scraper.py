import requests
from bs4 import BeautifulSoup
import time

def execute(**kwargs):
    url = kwargs.get('url')
    selectors = kwargs.get('selectors', [])
    timeout = kwargs.get('timeout', 10)
    
    try:
        # Send GET request to the URL
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # If no specific selectors are provided, return the entire text
        if not selectors:
            return {
                'status': 'success',
                'url': url,
                'content': soup.get_text()
            }
        
        # Extract content based on selectors
        extracted_data = {}
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                extracted_data[selector] = [elem.get_text(strip=True) for elem in elements]
            else:
                extracted_data[selector] = []
        
        return {
            'status': 'success',
            'url': url,
            'extracted_data': extracted_data
        }
        
    except requests.RequestException as e:
        return {
            'status': 'error',
            'url': url,
            'error': f'Request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'url': url,
            'error': f'Parsing failed: {str(e)}'
        }