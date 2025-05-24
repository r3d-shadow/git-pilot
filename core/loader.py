from jinja2 import Environment, BaseLoader

def load_template(path, variables={}):
    with open(path) as f:
        content = f.read()

    env = Environment(
        loader=BaseLoader(),
        variable_start_string='[[',
        variable_end_string=']]'
    )
    template = env.from_string(content)
    return template.render(**variables)
