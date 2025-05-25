import os
from src.core.interfaces import TemplateInterface
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, TemplateNotFound, pass_context

class JinjaTemplateEngine(TemplateInterface):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        includes = os.path.join(root_dir, 'includes')
        loader = ChoiceLoader([FileSystemLoader(root_dir), FileSystemLoader(includes)])
        self.env = Environment(loader=loader, variable_start_string='[[',
                               variable_end_string=']]', block_start_string='[%',
                               block_end_string='%]', trim_blocks=True, lstrip_blocks=True)
        try:
            helpers = self.env.get_template('_helpers.tpl').module
            self.env.globals['_'] = helpers
        except TemplateNotFound:
            self.env.globals['_'] = None
        @pass_context
        def include(ctx, name, **kwargs):
            new_ctx = dict(ctx); new_ctx.update(kwargs)
            return self.env.get_template(name).render(new_ctx)
        self.env.globals['include'] = include

    def list_templates(self, template_dir: str):
        return [f for f in os.listdir(self.root_dir)
                if f.endswith('.j2') and os.path.isfile(os.path.join(self.root_dir, f))]

    def render(self, template_name: str, vars: dict) -> str:
        tmpl = self.env.get_template(template_name)
        return tmpl.render(vars)
