from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import *
from django.contrib.auth.decorators import login_required

class CreateListing(forms.Form):
    title = forms.CharField(max_length=50, label="Listing")
    description = forms.CharField(widget=forms.Textarea)
    url = forms.CharField(max_length=100, label="Image URL")
    price = forms.IntegerField(label="Price", min_value=0)
    CATEGORIES = [(0, "")]
    cat = Categories.objects.all()
    for c in cat:
        category = (c.id, c.category)
        CATEGORIES.append(category)
    category = forms.ChoiceField(label="Category", choices=CATEGORIES)

def index(request):
    return render(request, "auctions/index.html",{
        "auctions": Auctions.objects.all(),
        "name": "Active Listings",
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




@login_required()
def create(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            url = form.cleaned_data["url"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            category=Categories.objects.get(id=category)
            user_id = request.user.id
            user_id = User.objects.get(id=user_id)
            auction = Auctions(title=title, description=description, url=url, price=price, offer=price, category_id=category, available=True , created_by=user_id)
            auction.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html",{
            "form": form
            })

    return render(request, "auctions/create.html",{
        "form": CreateListing()
    })


def categories(request):
    return render(request, "auctions/categories.html",{
        "categories": Categories.objects.all()
    })


def category(request, id):
    cat = Categories.objects.get(id=id)
    print(cat.category)
    return render(request, "auctions/index.html",{
        "name": "Category:",
        "auctions": cat.auction_category.all(),
        "category": cat.category
    })


def listings(request, id):
    if request.method == "POST":
        form = request.POST 
        offer = int(form["bid"])
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        auction = Auctions.objects.get(id=id)
        if auction.offer >= offer:
            return render(request, "auctions/listing.html",{
            "auction": Auctions.objects.get(id=id),
            "name": "Active Listings",
            "comments": Comments.objects.filter(product_id=id),
            "bids": Bids.objects.filter(product_id=id),
            "message": "The offer must be greater than the previous ones"
        })

        bid = Bids(product_id=auction, offer=offer, user_id=user)
        bid.save()
        auction = Auctions.objects.filter(id=id)
        auction.update(offer=offer)
        return render(request, "auctions/listing.html",{
            "auction": Auctions.objects.get(id=id),
            "name": "Active Listings",
            "comments": Comments.objects.filter(product_id=id),
            "bids": Bids.objects.filter(product_id=id)
        })


    try:
        bids= Bids.objects.get(product_id=id, winner=True) 
    except Bids.DoesNotExist:
        print("siguio esta ruta")
        return render(request, "auctions/listing.html",{
                    "auction": Auctions.objects.get(id=id),
                    "name": "Active Listings",
                    "comments": Comments.objects.filter(product_id=id),
                    "bids": "No bids"
                })
        
    return render(request, "auctions/listing.html",{
        "auction": Auctions.objects.get(id=id),
        "name": "Active Listings",
        "comments": Comments.objects.filter(product_id=id),
        "bids": Bids.objects.get(product_id=id, winner=True)
    })



@login_required
def comment(request, id):
    if request.method == "POST":
        form = request.POST
        comment = form["comment"]
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        auction = Auctions.objects.get(id=id)
        new_comment = Comments(comment=comment, user_id=user, product_id=auction)
        new_comment.save()
        return HttpResponseRedirect(reverse("listings", args=(id)))
    else:
        producto = Auctions.objects.filter(id=id)
        producto.update(available=False)
        producto=Auctions.objects.get(id=id)
        oferta_final = producto.offer
        ganador = Bids.objects.filter(product_id=producto, offer=oferta_final)
        ganador.update(winner=True) 
        return HttpResponseRedirect(reverse("listings", args=(id)))


@login_required
def watchlist(request):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    return render(request, "auctions/watchlist.html",{
        "auctions": user.user_watchlist.all(),
        "name": "Watchlist",
    })

@login_required
def addwatchlist(request, id):
    user_id = request.user.id
    user = User.objects.get(id=user_id)
    auction = Auctions.objects.get(id=id)
    print(auction)
    try:
        watchlist = Watchlist.objects.get(user_id=user, auction_id=auction)
        print(watchlist)
    except:
        new = Watchlist(user_id=user, auction_id=auction)
        new.save()
        return HttpResponseRedirect(reverse("watchlist"))
    
    watchlist.delete()
    return HttpResponseRedirect(reverse("watchlist"))