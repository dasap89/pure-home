# -*- coding: utf-8 -*-

from fiber.views import FiberTemplateView
from django.views.generic import ListView
from django.db.models import Q
from fiber.models import Page, ContentItem, PageContentItem
from django.template.loader import get_template
from django.core.mail import EmailMessage, send_mail
from django.template import Context
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict

from pure_pagination.mixins import PaginationMixin
from fiber.mixins import FiberPageMixin


class IndexPage(FiberTemplateView):
    def get_context_data(self):
        data = super(IndexPage, self).get_context_data()
        data['catalog_pages'] = Page.objects.filter(parent__url='catalog').order_by('title')
        data['items_with_old_price'] = Page.objects.filter(old_price__isnull=False)[:8]
        data['best_sellers'] = Page.objects.filter(best_seller__gt=0).order_by('-best_seller')[:8]
        return data


class SearchPage(PaginationMixin, ListView):
    paginate_by = 5 #this variable is used for pagination
    template_name = 'search.html'
    
    def get_queryset(self):
                 
        search = self.request.GET.get('search', None)
        self.search = search
        if search:
            search_in_content = ContentItem.objects.filter(content_html__icontains=search).values('id')
            search_in_page_content = PageContentItem.objects.filter(content_item__in=search_in_content).values('page_id')
            objects = Page.objects.filter(
                Q(id__in=search_in_page_content) | Q(title__icontains=search)
                )
        else:
            objects = Page.objects.all()
        
        return objects
    
    def get_context_data(self, **kwargs):
        context = super(SearchPage, self).get_context_data(**kwargs)
        context['search'] = self.search
        return context

class CatalogPage(FiberPageMixin, PaginationMixin, ListView):
    paginate_by = 9 #this variable is used for pagination
    template_name = 'catalog.html'


    def get_fiber_page_url(self):
        return self.request.path_info

    def get_queryset(self):
        
        parent_url = self.request.path[9:-1]         
        if len(parent_url):
            objects = Page.objects.filter(parent__url=parent_url)
        else:
            objects = Page.objects.filter(parent__url='svet')
        print objects
        
        return objects
