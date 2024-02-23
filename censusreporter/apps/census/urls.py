from django.conf import settings
from django.contrib import admin
from django.urls import reverse_lazy, path, re_path
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView, RedirectView
from django.views.decorators.csrf import csrf_exempt

from .views import (
    DataView,
    ExampleView,
    GeographyDetailView,
    HealthcheckView,
    HomepageView,
    MakeJSONView,
    SearchResultsView,
    SitemapTopicsView,
    TableDetailView,
    TopicView,
    UserGeographyDetailView,
    Census2020View,
    robots
)

STANDARD_CACHE_TIME = 60 * 60 * 24 * 7  # 1 week cache
COMPARISON_FORMATS = 'map|table|distribution'
BLOCK_ROBOTS = getattr(settings, 'BLOCK_ROBOTS', False)

urlpatterns = [
    path('', cache_page(STANDARD_CACHE_TIME)(HomepageView.as_view()), name='homepage'),
    re_path(r'^profiles/(?P<fragment>[a-zA-Z0-9\-]+)/$', cache_page(STANDARD_CACHE_TIME)(GeographyDetailView.as_view()), name='geography_detail'),
    path('profiles/', RedirectView.as_view(url=reverse_lazy('search')), name='geography_search_redirect'),
    path('make-json/charts/', csrf_exempt(MakeJSONView.as_view()), name='make_json_charts'),
    re_path(r'^tables/B23002/$', RedirectView.as_view(url=reverse_lazy('table_detail', kwargs={'table': 'B23002A'})), name='redirect_B23002'),
    re_path(r'^tables/C23002/$', RedirectView.as_view(url=reverse_lazy('table_detail', kwargs={'table': 'C23002A'})), name='redirect_C23002'),
    re_path(r'^tables/(?P<table>[a-zA-Z0-9]+)/$', cache_page(STANDARD_CACHE_TIME)(TableDetailView.as_view()), name='table_detail'),
    path('tables/', RedirectView.as_view(url=reverse_lazy('search')), name='table_search'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('data/', RedirectView.as_view(url=reverse_lazy('table_search')), name='table_search_redirect'),
    re_path(r'^data/(?P<format>%s)/$' % COMPARISON_FORMATS, cache_page(STANDARD_CACHE_TIME)(DataView.as_view()), name='data_detail'),
    path('topics/', cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()), name='topic_list'),
    path('topics/race-latino/', RedirectView.as_view(url=reverse_lazy('topic_detail', kwargs={'topic_slug': 'race-hispanic'})), name='topic_latino_redirect'),
    re_path(r'^topics/(?P<topic_slug>[-\w]+)/$', cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()), name='topic_detail'),
    re_path(r'^examples/(?P<example_slug>[-\w]+)/$', cache_page(STANDARD_CACHE_TIME)(ExampleView.as_view()), name='example_detail'),
    path('glossary/', cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="glossary.html")), name='glossary'),
    path('about/', cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="about.html")), name='about'),
    path('2020/', cache_page(60 * 5)(Census2020View.as_view(template_name="2020.html")), name='2020'),
    path('acs-2020-update/', cache_page(60 * 5)(Census2020View.as_view(template_name="acs-2020-update.html")), name='acs-2020-update'),
    path('locate/', cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="locate/locate.html")), name='locate'),
    path('user_geo/', cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="user_geo/index.html")), name='user_geo'),
    re_path(r'^user_geo/(?P<hash_digest>[A-Fa-f0-9]{32})/$', UserGeographyDetailView.as_view(template_name="user_geo/detail.html"), name='user_geo_detail'),
    path('healthcheck', HealthcheckView.as_view(), name='healthcheck'),
    path('robots.txt', robots),
    path('topics/sitemap.xml', SitemapTopicsView.as_view(), name='sitemap_topics'),
]
