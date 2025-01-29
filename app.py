# from flask import Flask, render_template, request, redirect, url_for
# import rdflib
# import os

# app = Flask(__name__)

# # Path to the upload folder
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Parse TTL file and extract its contents
# def parse_ttl(file_path):
#     g = rdflib.Graph()
#     try:
#         g.parse(file_path, format="ttl")
#     except Exception as e:
#         return None, None, None  # Handle the error appropriately

#     nodes = []
#     links = []
#     node_set = set()

#     # Extract namespaces from the graph
#     namespaces = dict(g.namespaces())

#     # Function to replace full URIs with shorthand prefixes
#     def shorten_uri(uri):
#         for prefix, namespace in namespaces.items():
#             if uri.startswith(namespace):
#                 return uri.replace(namespace, f"{prefix}:")
#         return uri  # Return the original URI if no prefix matches

#     # Collect nodes and edges
#     for subject in g.subjects():
#         subject_str = shorten_uri(str(subject))
#         if subject_str not in node_set:
#             nodes.append({"id": subject_str, "label": subject_str})
#             node_set.add(subject_str)

#         for predicate, obj in g.predicate_objects(subject):
#             predicate_str = shorten_uri(str(predicate))
#             object_str = shorten_uri(str(obj))

#             if object_str not in node_set:
#                 nodes.append({"id": object_str, "label": object_str})
#                 node_set.add(object_str)

#             links.append({"source": subject_str, "target": object_str, "label": predicate_str})

#     return nodes, links, namespaces

# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return redirect(request.url)
    
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
    
#     if file and file.filename.endswith('.ttl'):
#         filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filename)
#         return redirect(url_for('show_file', filename=file.filename))
    
#     return "Invalid file type. Please upload a .ttl file.", 400


# @app.route('/show_file/<filename>')
# def show_file(filename):
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     nodes, links, namespaces = parse_ttl(file_path)
#     return render_template('show_file.html', filename=filename, nodes=nodes, links=links, namespaces=namespaces)


# @app.route('/insights')
# def insights():
#     return render_template('insights.html')


# @app.route('/visualize/<filename>')
# def visualize(filename):
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     nodes, links, _ = parse_ttl(file_path)
#     return render_template('visualize.html', filename=filename, nodes=nodes, links=links)


# if __name__ == '__main__':
#     app.run(debug=True)

# NEW CODE HERE:"
from flask import Flask, render_template, request, redirect, url_for, jsonify
import rdflib
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to parse TTL file and extract its contents
def parse_ttl(file_path):
    g = rdflib.Graph()
    try:
        g.parse(file_path, format="ttl")
    except Exception as e:
        return None, None, None  # Handle parsing errors

    nodes = []
    links = []
    node_set = set()
    namespaces = dict(g.namespaces())

    def shorten_uri(uri):
        for prefix, namespace in namespaces.items():
            if uri.startswith(namespace):
                return uri.replace(namespace, f"{prefix}:")
        return uri  

    for subject in g.subjects():
        subject_str = shorten_uri(str(subject))
        if subject_str not in node_set:
            nodes.append({"id": subject_str, "label": subject_str})
            node_set.add(subject_str)

        for predicate, obj in g.predicate_objects(subject):
            predicate_str = shorten_uri(str(predicate))
            object_str = shorten_uri(str(obj))

            if object_str not in node_set:
                nodes.append({"id": object_str, "label": object_str})
                node_set.add(object_str)

            links.append({"source": subject_str, "target": object_str, "label": predicate_str})

    return nodes, links, namespaces

# Function to load TTL file into RDF graph
def load_graph(file_path):
    g = rdflib.Graph()
    try:
        g.parse(file_path, format="ttl")
    except Exception as e:
        print(f"Error parsing TTL file: {e}")
        return None
    return g

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.ttl'):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return redirect(url_for('show_file', filename=file.filename))
    
    return "Invalid file type. Please upload a .ttl file.", 400

@app.route('/show_file/<filename>')
def show_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    nodes, links, namespaces = parse_ttl(file_path)
    return render_template('show_file.html', filename=filename, nodes=nodes, links=links, namespaces=namespaces)

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/visualize/<filename>')
def visualize(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    nodes, links, _ = parse_ttl(file_path)
    return render_template('visualize.html', filename=filename, nodes=nodes, links=links)

# New Route: SPARQL Query Interface
@app.route('/sparql_query/<filename>', methods=['GET', 'POST'])
def sparql_query(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    g = rdflib.Graph()
    g.parse(file_path, format="ttl")

    results = None

    if request.method == 'POST':
        query = request.form['query']
        try:
            results = g.query(query)
        except Exception as e:
            return f"SPARQL Query Error: {str(e)}", 400

    return render_template('sparql.html', filename=filename, results=results)


# New Route: Execute SPARQL Queries
@app.route('/run_sparql/<filename>', methods=['POST'])
def run_sparql(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    graph = load_graph(file_path)

    if not graph:
        return jsonify({"error": "Failed to load the TTL file"}), 500

    query = request.json.get("query", "")

    if not query:
        return jsonify({"error": "No SPARQL query provided"}), 400

    try:
        results = graph.query(query)
        data = []
        for row in results:
            data.append([str(cell) for cell in row])

        return jsonify({"data": data, "columns": results.vars})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
