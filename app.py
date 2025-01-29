from flask import Flask, render_template, request, redirect, url_for, jsonify
import rdflib
import os
from pyshacl import validate
import tempfile  # For temporary files

app = Flask(__name__)

# Use temp directories to avoid permission issues and simplify cleanup
UPLOAD_FOLDER = tempfile.mkdtemp(prefix="rdf_uploads_")
SHACL_UPLOAD_FOLDER = tempfile.mkdtemp(prefix="shacl_uploads_")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SHACL_UPLOAD_FOLDER'] = SHACL_UPLOAD_FOLDER

# Ensure SHACL upload folder exists
if not os.path.exists(SHACL_UPLOAD_FOLDER):
    os.makedirs(SHACL_UPLOAD_FOLDER)



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

# Function to load graph into RDF
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

# New Route: SHACL validation and similar stuff--------------------------------------------------------
@app.route('/shacl-validation', methods=['GET', 'POST'])
def shacl_validation():
    rdf_file_path = None
    shacl_file_path = None
    results_text = None
    is_valid = None

    if request.method == 'POST':
        rdf_file = request.files.get('rdf_file')
        shacl_file = request.files.get('shacl_file')

        if rdf_file and rdf_file.filename.endswith('.ttl'):
            rdf_file_path = os.path.join(app.config['UPLOAD_FOLDER'], rdf_file.filename)
            rdf_file.save(rdf_file_path)

        if shacl_file and shacl_file.filename.endswith('.ttl'):
            shacl_file_path = os.path.join(app.config['SHACL_UPLOAD_FOLDER'], shacl_file.filename)
            shacl_file.save(shacl_file_path)

        if rdf_file_path and shacl_file_path:
            try:
                is_valid, results_text = validate_rdf_with_shacl(rdf_file_path, shacl_file_path)
            except Exception as e:
                results_text = f"An unexpected error occurred: {str(e)}"
                is_valid = False

    return render_template('shacl_validation.html', is_valid=is_valid, results_text=results_text)


def validate_rdf_with_shacl(rdf_file, shacl_file):
    try:
        rdf_graph = rdflib.Graph()
        rdf_graph.parse(rdf_file, format="ttl")

        shacl_graph = rdflib.Graph()
        shacl_graph.parse(shacl_file, format="ttl")

        conforms, results_graph, results_text = validate(
            rdf_graph,
            shacl_graph=shacl_graph,
            inference='rdfs',
            abort_on_error=False
        )

        return conforms, results_text  # Return results_text directly

    except Exception as e:
        return False, str(e)  # Return the exception message

if __name__ == '__main__':
    app.run(debug=True)
