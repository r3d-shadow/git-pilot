import os
from jinja2 import Environment, FileSystemLoader, ChoiceLoader

def get_environment(root_dir):
    """
    root_dir: The directory containing the top-level workflow templates,
              assumed to contain 'includes/' subdirectory for partials/helpers.
    """

    includes_dir = os.path.join(root_dir, 'includes')

    # Use ChoiceLoader to look for templates in both root_dir and includes_dir
    loader = ChoiceLoader([
        FileSystemLoader(root_dir),      # root templates
        FileSystemLoader(includes_dir),  # includes/_helpers.tpl, includes/units/hello-world.j2 etc.
    ])

    env = Environment(
        loader=loader,
        variable_start_string='[[',
        variable_end_string=']]',
        block_start_string='[%',
        block_end_string='%]',
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Load _helpers.tpl from includes/ and inject globally as '_'
    helpers = env.get_template('_helpers.tpl').module
    env.globals['_'] = helpers

    return env


def load_template(template_path, vars):
    """
    template_path: full path to the top-level template to render
    vars: dict of variables for rendering
    """

    root_dir = os.path.dirname(template_path)
    filename = os.path.basename(template_path)

    env = get_environment(root_dir)
    template = env.get_template(filename)
    return template.render(vars)
