from django.conf.urls import url , include
from . import views
urlpatterns=[
	url(r'^$',views.Search_view,name='Search'),
	url(r'^recherche/(?P<pk>\d+)/$',views.Result_view,name='Result'),
	url(r'^login', views.user_login_view, name='login'),
	url(r'^logout', views.user_logout_view, name='logout'),
	url(r'^deleteTweet',views.deleteTweet_view,name='deleteTweet'),
	url(r'^deleteSearch',views.deleteSearch_view,name='deleteSearch'),

]