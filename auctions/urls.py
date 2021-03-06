from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:id>", views.category, name="category"),
    path("listings/<int:id>/", views.listings, name="listings"),
    path("comment/<id>", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="add"),
]
