from flask import Flask, render_template, request, redirect, url_for
import rdflib
import os

app = Flask(__name__)

# Path to the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Parse TTL file and extract its contents
def parse_ttl(file_path):
    g = rdflib.Graph()
    try:
        g.parse(file_path, format="ttl")
    except Exception as e:
        return None, None, None  # Handle the error appropriately

    nodes = []
    links = []
    node_set = set()

    # Extract namespaces from the graph
    namespaces = dict(g.namespaces())

    # Function to replace full URIs with shorthand prefixes
    def shorten_uri(uri):
        for prefix, namespace in namespaces.items():
            if uri.startswith(namespace):
                return uri.replace(namespace, f"{prefix}:")
        return uri  # Return the original URI if no prefix matches

    # Collect nodes and edges
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


if __name__ == '__main__':
    app.run(debug=True)
