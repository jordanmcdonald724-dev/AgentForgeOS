from research.internet_scanner import perform_web_search

try:
    results = perform_web_search('python programming', 3)
    print(f'Internet scanner test: Found {len(results)} results')
    if results:
        print(f'First result: {results[0].get("title", "No title")}')
except Exception as e:
    print(f'Internet scanner test failed: {e}')
