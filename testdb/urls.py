from django.urls import path
from .views import home, article_list, federal_wanted_list, delete_federal_wanted,local_criminals_list, add_local_criminal, add_panishment, archive_panishment, reports_view

urlpatterns = [
    path('', home, name='home'),
    path('articles/', article_list, name='article_list'),
    path('federal-wanted/', federal_wanted_list, name='federal_wanted_list'),
    path('federal-wanted/delete/<int:fi>/', delete_federal_wanted, name='delete_federal_wanted'),
    path("local-criminals/", local_criminals_list, name="local_criminals_list"),
    path("add-local-criminal/", add_local_criminal, name="add_local_criminal"),
    path("add-panishment/", add_panishment, name="add_panishment"),
    path("archive-panishment/", archive_panishment, name="archive_panishment"),
    path('reports/', reports_view, name='reports')
]
