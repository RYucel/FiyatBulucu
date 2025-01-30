from flask import Flask, request, render_template_string, jsonify
import csv

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Price Finder</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .container { max-width: 800px; margin-top: 30px; }
        .search-box { position: relative; }
        .autocomplete-items {
            position: absolute;
            z-index: 99;
            width: 100%;
            max-height: 200px;
            overflow-y: auto;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 0 0 4px 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .autocomplete-item {
            padding: 8px 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .autocomplete-item:hover {
            background-color: #f1f1f1;
        }
        .product-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="mb-4 text-primary">Product Price Checker</h2>
        
        <div class="search-box mb-4">
            <form method="POST" id="searchForm">
                <div class="input-group">
                    <input type="text" 
                           id="searchInput"
                           name="product_name" 
                           class="form-control form-control-lg" 
                           placeholder="Start typing product name..."
                           autocomplete="off"
                           required>
                    <button type="submit" class="btn btn-primary btn-lg">Search</button>
                </div>
                <div id="autocompleteList" class="autocomplete-items"></div>
            </form>
        </div>

        {% if product %}
        <div class="product-card">
            <h4 class="mb-3">{{ product.ProductName }}</h4>
            <div class="row align-items-center">
                <div class="col-md-6">
                    <p class="lead mb-0">Last Month's Price: <strong>{{ product.LastMonthPrice }} TL</strong></p>
                    <p class="text-muted mb-0">Weight: {{ product.weight }} kg</p>
                </div>
                <div class="col-md-6 text-end">
                    <form method="POST" action="/confirm" class="d-inline">
                        <input type="hidden" name="product_name" value="{{ product.ProductName }}">
                        <button type="submit" class="btn btn-success btn-lg">Confirm</button>
                    </form>
                    <button onclick="window.location.href='/'" class="btn btn-outline-secondary btn-lg">New Search</button>
                </div>
            </div>
        </div>
        {% elif product == None and request.method == 'POST' %}
        <div class="alert alert-warning mt-3">
            Product not found. Please try another name.
        </div>
        {% endif %}
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const autocompleteList = document.getElementById('autocompleteList');
        
        function debounce(func, timeout = 200) {
            let timer;
            return (...args) => {
                clearTimeout(timer);
                timer = setTimeout(() => func.apply(this, args), timeout);
            };
        }

        async function fetchSuggestions(query) {
            try {
                const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const products = await response.json();
                showSuggestions(products);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        function showSuggestions(products) {
            autocompleteList.innerHTML = '';
            products.forEach(product => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.innerHTML = `
                    <div>${highlightMatch(product.ProductName, searchInput.value)}</div>
                    <small class="text-muted">${product.LastMonthPrice} TL</small>
                `;
                div.onclick = () => {
                    searchInput.value = product.ProductName;
                    document.getElementById('searchForm').requestSubmit();
                };
                autocompleteList.appendChild(div);
            });
        }

        function highlightMatch(text, match) {
            const regex = new RegExp(`(${match})`, 'gi');
            return text.replace(regex, '<mark>$1</mark>');
        }

        searchInput.addEventListener('input', debounce(e => {
            const query = e.target.value.trim();
            autocompleteList.innerHTML = query.length > 0 ? '' : '';
            if (query.length > 1) fetchSuggestions(query);
        }));

        document.addEventListener('click', e => {
            if (!e.target.closest('.search-box')) {
                autocompleteList.innerHTML = '';
            }
        });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

def load_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        data = list(csv.DictReader(file, skipinitialspace=True))
        required_columns = {'ProductName', 'LastMonthPrice', 'weight'}
        if not data or not required_columns.issubset(data[0].keys()):
            raise ValueError("CSV must contain: ProductName, LastMonthPrice, weight")
        return data

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, product=None)

@app.route('/search')
def autocomplete():
    query = request.args.get('q', '').lower().strip()
    data = load_csv('Python\data.csv')
    matches = []
    
    for product in data:
        product_name = product['ProductName'].lower()
        if query in product_name:
            matches.append({
                'ProductName': product['ProductName'],
                'LastMonthPrice': product['LastMonthPrice'],
                'weight': product['weight']
            })
    
    return jsonify(matches[:8])

@app.route('/', methods=['POST'])
def search():
    try:
        data = load_csv('Python\data.csv')
        product_name = request.form['product_name'].strip().lower()
        product = next((p for p in data if p['ProductName'].lower() == product_name), None)
        return render_template_string(HTML_TEMPLATE, product=product)
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/confirm', methods=['POST'])
def confirm():
    return f"Confirmation received for: {request.form['product_name']}"

if __name__ == '__main__':
    app.run(debug=True)