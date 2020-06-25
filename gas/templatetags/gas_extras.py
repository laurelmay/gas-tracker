from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def nav_active(context, item):
    """
    Returns 'active' if item is the active nav bar item, and '' otherwise.
    """

    default = ''
    try:
        url_name = context['request'].resolver_match.url_name
    except:
        return default

    if url_name == item:
        return 'active'
    
    return default
