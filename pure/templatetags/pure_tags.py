import json
import operator
from copy import copy

from django import template
from django.contrib.auth.models import AnonymousUser
from django.template import TemplateSyntaxError
from django.utils.html import escape
from django.db.models import Q
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

import pure
import fiber
from fiber.models import Page, ContentItem
from helpdesk.models import Queue

# from fiber.utils.urls import get_admin_change_url
# from fiber.app_settings import PERMISSION_CLASS, AUTO_CREATE_CONTENT_ITEMS
# from fiber.utils.import_util import load_class


# PERMISSIONS = load_class(PERMISSION_CLASS)

register = template.Library()

class MenuHelper(object):
    """
    Helper class for show_menu tag, for convenience/clarity
    """
    def __init__(self, context, menu_name, min_level=1, max_level=999, expand=None):
        self.context = copy(context)
        self.menu_name = menu_name
        self.min_level = min_level
        self.max_level = max_level
        self.expand = expand
        self.menu_parent = None
    
    def filter_min_level(self, tree):
        """
        Remove pages that are below the minimum_level
        """
        return (p for p in tree if p.level >= self.min_level)

    def filter_for_user(self, tree):
        """
        Remove pages that shouldn't be in the menu for the current user
        """
        user = self.context.get('user', AnonymousUser())
        return (p for p in tree if (p.is_public_for_user(user) and p.show_in_menu))

    def get_context_data(self):
        return {
            'Page': Page,
            'fiber_menu_pages': self.get_menu(),
            'fiber_menu_parent_page': self.menu_parent,
            'fiber_menu_args': {
                'menu_name': self.menu_name,
                'min_level': self.min_level,
                'max_level': self.max_level,
                'expand': self.expand
            }
        }

    def get_root(self):
        """
        Get the root page for this menu
        """
        try:
            return Page.objects.get(title=self.menu_name, parent=None)
        except Page.DoesNotExist:
            raise Page.DoesNotExist("Menu does not exist.\nNo top-level page found with the title '%s'." % self.menu_name)

    def get_tree(self, root):
        """
        Get a page tree from the root page, limited to max_level
        """
        # Page.get_absolute_url() accesses self.parent recursively to build URLs (assuming relative URLs).
        # To render any menu item, we need all the ancestors up to the root.
        # Therefore it's more efficient to fetch the entire tree, and apply min_level manually later.
        return root.get_descendants(include_self=True).filter(level__lte=self.max_level)

    def get_tree_for_page(self, root, page):
        """
        Get a tree, taking a specific page into account
        """
        if not page or not page.is_child_of(root):
            if self.min_level == 1:
                # The current page is not part of the menu tree.
                # Only show first level menus.
                return self.get_tree(root).filter(level__lte=1)
            else:
                # The current page is not part of the menu tree, so it can't have a sub menu
                return []
        if page.level + 1 < self.min_level:
            return []  # The current page is below the threshold, so no menu should be shown
        else:
            tree = self.get_tree(root)

            # We need the 'route' to the current page, the 'sibling' nodes and the children
            route = tree.filter(lft__lt=page.lft, rght__gt=page.rght)

            # We show any siblings of anything in the route to the current page.
            # The logic here is that if the user drills down, menu items
            # shown previously should not disappear.

            # The following assumes that accessing .parent is cheap, which
            # it can be if current_page was loaded correctly.
            p = page
            sibling_qs = []
            while p.parent_id is not None:
                sibling_qs.append(tree.filter(level=p.level, lft__gt=p.parent.lft, rght__lt=p.parent.rght))
                p = p.parent
            route_siblings = reduce(operator.or_, sibling_qs)

            children = tree.filter(lft__gt=page.lft, rght__lt=page.rght)
            if self.expand != 'all_descendants':
                # only want immediate children:
                children = children.filter(level=page.level + 1)

            return route | route_siblings | children

    def get_menu(self):
        """
        Get the menu tree
        """
        root = self.get_root()
        current = self.context.get('fiber_page')
        if self.expand == 'all':
            # Unfiltered sitemap like tree
            tree = self.get_tree(root)
        else:
            # (sub) menus, expanding/collapsing based on current page
            tree = self.get_tree_for_page(root, current)

        tree = Page.objects.link_parent_objects(tree)
        tree = self.filter_min_level(tree)
        tree = self.filter_for_user(tree)

        # Order menu_pages for use with tree_info template tag.
        tree = sorted(tree, key=operator.attrgetter('lft'))

        self.menu_parent = None
        if tree and self.min_level > 1:
            self.menu_parent = tree[0].parent
        elif self.min_level == 1:
            self.menu_parent = root
        return tree

@register.inclusion_tag('snippets/content_items.html', takes_context=True)
def show_pure_page_content(context, page_or_block_name, block_name=None):
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

@register.inclusion_tag('snippets/pure_menu.html', takes_context=True)
def show_pure_menu(context, menu_name, min_level, max_level, expand=None):
    context = copy(context)
    context.update(MenuHelper(context, menu_name, min_level, max_level, expand).get_context_data())
    return context

@register.simple_tag
def get_page_by_title(object):
    """
    Get page by its title or url
    
    Usage:
        {% get_page_by_title obj %}
    """
    
    title_of_page = object
    
    return Page.objects.filter(
        Q(title__icontains=title_of_page)|Q(url__icontains=title_of_page)
    ).first()

 
@register.filter
def my_currency(currency):
    if currency:
        currency = round(float(currency), 2)
        # print intcomma(int(currency))
        # curr = str(int(currency))
        # curr = curr[::-1]
        # a = curr.split("curr", 3)
        # # print a[1]
        # print " ".join(a)
        # print currency.join(" ")
        return "%s%s" % (intcomma(int(currency)), ("%0.2f" % currency)[-3:])
    else:
        return ''

@register.inclusion_tag('snippets/content_item_raw.html', takes_context=True)
def show_raw_page_content(context, page_or_block_name, block_name=None):
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
