from jinja2 import Template

def load_template(path, variables={}):
    with open(path) as f:
        template = Template(f.read())
    return template.render(**variables)
