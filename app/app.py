import os
import requests
from flask import Flask, jsonify, request, render_template
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__, template_folder='templates', static_folder='static')

# Metrics
REQUEST_COUNT = Counter('api_request_count', 'Total API requests', ['method','endpoint','http_status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['endpoint'])

# Calendarific settings
CALENDARIFIC_API_KEY = os.environ.get('CALENDARIFIC_API_KEY', '')
CALENDARIFIC_URL = 'https://calendarific.com/api/v2/holidays'

def record_metrics(endpoint, method, status, latency):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)


@app.route('/')
def index():
    # Minimal list of countries (can be extended)
    countries = {
        'US': 'United States',
        'IN': 'India',
        'GB': 'United Kingdom',
        'CA': 'Canada',
        'AU': 'Australia'
    }
    return render_template('index.html', countries=countries)


@app.route('/api/countries')
def countries():
    # In production, fetch from an authoritative source or cache
    data = [
        {'code': 'US', 'name': 'United States'},
        {'code': 'IN', 'name': 'India'},
        {'code': 'GB', 'name': 'United Kingdom'},
        {'code': 'CA', 'name': 'Canada'},
        {'code': 'AU', 'name': 'Australia'},
    ]
    return jsonify(data)


@app.route('/api/holidays')
def holidays():
    import time
    start = time.time()
    country = request.args.get('country')
    year = request.args.get('year')

    if not country or not year:
        status = 400
        record_metrics('/api/holidays', request.method, status, time.time()-start)
        return jsonify({'error': 'country and year query parameters are required'}), 400

    # Optionally use S3 or local cache - omitted for brevity
    params = {
        'api_key': CALENDARIFIC_API_KEY,
        'country': country,
        'year': year
    }

    if not CALENDARIFIC_API_KEY:
        # Return a helpful error if API key missing
        status = 500
        record_metrics('/api/holidays', request.method, status, time.time()-start)
        return jsonify({'error': 'Calendarific API key not configured in CALENDARIFIC_API_KEY env var'}), 500

    resp = requests.get(CALENDARIFIC_URL, params=params, timeout=10)
    if resp.status_code != 200:
        status = resp.status_code
        record_metrics('/api/holidays', request.method, status, time.time()-start)
        return jsonify({'error': 'Calendarific API error', 'details': resp.text}), resp.status_code

    payload = resp.json()
    holidays = payload.get('response', {}).get('holidays', [])

    # Simplify data returned
    simplified = []
    for h in holidays:
        simplified.append({
            'name': h.get('name'),
            'description': h.get('description'),
            'date': h.get('date', {}).get('iso'),
            'type': h.get('type')
        })

    status = 200
    record_metrics('/api/holidays', request.method, status, time.time()-start)
    return jsonify(simplified)


# Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


if __name__ == '__main__':
    # For local testing
    app.run(host='0.0.0.0', port=5000)
