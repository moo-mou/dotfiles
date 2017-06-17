import os

from m_base import Base
from util import (
    get_config_yml,
    get_gh_token,
    setup,
)


def compile_context(mk2, context):
    if isinstance(context, list):
        return [compile_context(mk2, item) for item in context]
    elif isinstance(context, dict):
        for k, v in context.items():
            if k.startswith('markdown_'):
                context[k] = mk2.markdown(v)
            else:
                context[k] = compile_context(mk2, v)

    return context


class WWW(Base):
    def __init__(self):
        super(WWW, self).__init__([
            'jinja2',
            'requests',
            'markdown2',
        ])

    @setup
    def compile_template(self):
        '''Find jinja2 template and build by using var in config.yaml'''
        jinja2 = self._modules['jinja2']
        markdown2 = self._modules['markdown2']

        config = get_config_yml()
        compile_config = config['compile']

        loader = jinja2.FileSystemLoader(
            './%s' % compile_config['src_dir'], followlinks=True)
        env = jinja2.Environment(loader=loader)

        context = config.get('context', {})
        context = compile_context(markdown2, context)

        for temp_name in env.list_templates(
            filter_func=lambda x: not x.startswith(
                '_') and x.endswith(compile_config['ext'])
        ):
            self.logger.info('Compiling %s...' % temp_name)
            temp = env.get_template(temp_name)

            out_dir = compile_config['out_dir']

            with open('./%s/%s' % (out_dir, temp_name), 'wb') as f:
                context['filename'] = os.path.splitext(
                    os.path.basename(temp_name))[0]
                f.write(temp.render(**context).encode('utf-8'))

    @setup
    def generate_release_from_gh(self):
        requests = self._modules['jinja2']
        gh_token = get_gh_token()

        # TODO
