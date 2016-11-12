from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active(context, url):
    current_path = context.request.get_full_path()
    if current_path.startswith(url):
        return 'active'
    return ''
