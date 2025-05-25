import os
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, TemplateNotFound
from jinja2 import pass_context 


def get_environment(root_dir):
    includes_dir = os.path.join(root_dir, 'includes')

    loader = ChoiceLoader([
        FileSystemLoader(root_dir),
        FileSystemLoader(includes_dir),
    ])

    env = Environment(
        loader=loader,
        variable_start_string='[[',
        variable_end_string=']]',
        block_start_string='[%',  # for block tags
        block_end_string='%]',
        trim_blocks=True,
        lstrip_blocks=True,
    )

    try:
        helpers = env.get_template('_helpers.tpl').module
        env.globals['_'] = helpers
    except TemplateNotFound:
        env.globals['_'] = None

    # Define include that receives current context automatically
    @pass_context
    def inline_include(context, template_name, **kwargs):
        # Merge current context with kwargs; kwargs override context keys
        new_context = dict(context)
        new_context.update(kwargs)
        tmpl = env.get_template(template_name)
        return tmpl.render(new_context)

    env.globals['include'] = inline_include

    return env


def load_template(template_path, vars):
    root_dir = os.path.dirname(template_path)
    filename = os.path.basename(template_path)

    env = get_environment(root_dir)
    template = env.get_template(filename)
    return template.render(vars)
