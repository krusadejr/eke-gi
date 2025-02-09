Made by Ayush Kumar for the final project in the course "Enterprise Knowledge Engineering". 
Technische Hochschule Brandenburg, Brandenburg an der Havel, BRB 14770


```markdown
# Project Setup Guide

Here are the consolidated steps to get the app running. If there are any doubts/issues, you can be contacted without any delays under ayush.kumar@th-brandenburg.de.

## Steps:

1. Install Python 3.x from [python.org](https://www.python.org/downloads/).
2. Create a virtual environment.
3. Activate the virtual environment.
4. Install dependencies.
5. Run the application.
6. Access the app in your browser at `http://127.0.0.1:5000/`.

## Command Sheet:

### Create virtual environment:
```bash
python -m venv venv
```

### Activate virtual environment:
- **On Windows:**
  ```bash
  .\venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### Install dependencies:
```bash
pip install Flask rdflib pyshacl
```

### Run the application:
```bash
flask run
```

### Deactivate virtual environment:
```bash
deactivate
```

## Contact Information:

For any issues or further questions, feel free to contact me at:  
**Email**: ayush.kumar@th-brandenburg.de
```
