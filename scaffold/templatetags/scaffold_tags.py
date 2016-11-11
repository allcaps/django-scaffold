from django.template import Node
from django.template.defaultfilters import register


class EmptyLineLessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        data = []
        lines = self.nodelist.render(context)
        for line in lines.split('\n'):
            if line.strip() != u"":
                data.append(line)
        return "\n".join(data)


@register.tag
def emptylineless(parser, token):
    nodelist = parser.parse(('endemptylineless',))
    parser.delete_first_token()
    return EmptyLineLessNode(nodelist)
