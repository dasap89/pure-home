import json
import operator
from copy import copy

from django import template
from django.contrib.auth.models import AnonymousUser
from django.template import TemplateSyntaxError
from django.utils.html import escape

import pure
import fiber
from fiber.models import Page, ContentItem
from helpdesk.models import Queue
# from fiber.utils.urls import get_admin_change_url
# from fiber.app_settings import PERMISSION_CLASS, AUTO_CREATE_CONTENT_ITEMS
# from fiber.utils.import_util import load_class


# PERMISSIONS = load_class(PERMISSION_CLASS)

register = template.Library()

# @register.inclusion_tag('pure/templates/snippets/content_items.html', takes_context=True)
@register.inclusion_tag('snippets/content_items.html', takes_context=True)
def my_show_page_content(context, page_or_block_name, block_name=None):
    """
    Fetch and render named content items for the current fiber page, or a given fiber page.
    {% show_page_content "block_name" %}              use fiber_page in context for content items lookup
    {% show_page_content other_page "block_name" %}   use other_page for content items lookup
    """
    
    page_or_block_name = page_or_block_name or None
    if isinstance(page_or_block_name, basestring) and block_name is None:
        # Single argument e.g. {% show_page_content 'main' %}
        block_name = page_or_block_name
        try:
            page = context['fiber_page']
        except KeyError:
            page = None
    elif (page_or_block_name is None or isinstance(page_or_block_name, Page)) and block_name:
        # Two arguments e.g. {% show_page_content other_page 'main' %}
        page = page_or_block_name
    else:
        # Bad arguments
        raise TemplateSyntaxError("'show_page_content' received invalid arguments")

    if page and block_name:
        page_content_items = page.page_content_items.filter(block_name=block_name).order_by('sort').select_related('content_item')
        
        content_items = []
        for page_content_item in page_content_items:
            content_item = page_content_item.content_item
            content_item.page_content_item = page_content_item
            content_items.append(content_item)
        
        context = copy(context)
        
        context.update({
            'fiber_page': page,
            'ContentItem': ContentItem,
            'fiber_block_name': block_name,
            'fiber_content_items': content_items
        })
       
        return context

@register.simple_tag
def get_image_url_from_html(object):
    """
    Usage:
        {% get_image_url_from_html obj %}
    """
    
    text = object
    start = text.find("src=") + 5
    end = text.find("\"", start)
    
    return text[start:end]

@register.simple_tag
def get_queue_for_page(object):
    """
    Usage:
        {% get_queue_for_page obj as var %}
    """
    
    title_of_page = object.title
    
    return Queue.objects.get(title=title_of_page).id