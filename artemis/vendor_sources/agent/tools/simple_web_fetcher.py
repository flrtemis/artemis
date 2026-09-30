import urllib.request

def execute(**kwargs):
    url = kwargs.get('url')
    if not url:
        return "Error: No URL provided."
    
    try:
        # Using raw.githubusercontent if the user provided a github blob URL
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            # Return a portion of the content to avoid overwhelming the system
            return content[:5000] 
    except Exception as e:
        return f"Error fetching URL: {str(e)}"
