from django.urls import path
from .import views
urlpatterns=[
    path("",views.home,name="home"),
    path("heatmap",views.heatmap_analysis,name="heatmap"),
    path('filter_data/', views.filter_data, name='filter_data'),


]