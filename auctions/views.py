from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max

from .models import *


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings})


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



@login_required
def new_listing(request):
    if request.method == 'POST':
        new_listing_form = NewListingForm(request.POST)
        if new_listing_form.is_valid():
            new_listing = Listing(
                title = new_listing_form.cleaned_data['title'],
                description = new_listing_form.cleaned_data['description'],
                starting_bid = new_listing_form.cleaned_data['starting_bid'],
                image_URL = new_listing_form.cleaned_data['image_URL'],
                category = new_listing_form.cleaned_data['category'],
                closed = False,
                seller = request.user
                )
            new_listing.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        new_listing_form = NewListingForm()
    return render(request, "auctions/new_listing.html", {
        "new_listing_form": new_listing_form
    })



class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"placeholder":"Add a title for your item", "class": "form-control"}))
    description = forms.CharField(label="Item Description", widget=forms.Textarea(attrs={"placeholder":"Describe your item", "class": "form-control"}))
    starting_bid = forms.DecimalField(label="Starting bid (£)", max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={"placeholder":"00.00", "class": "form-control"}))
    image_URL = forms.URLField(label="Image URL", max_length=500, required=False, widget=forms.URLInput(attrs={"placeholder":"https://imageURL.com", "class": "form-control"}))
    category = forms.ChoiceField(label="Category", choices=item_categories, required=False, initial='', widget=forms.Select({"class": "form-control"}))



def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == "POST":
        new_bid = Bid(
            listing = Listing.objects.get(pk=listing_id),
            bidder = request.user,
            value = request.POST["new_bid"]
            )
        new_bid.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    return render(request, "auctions/listing.html", {
        "listing": listing,
    })



def manage_watchlist(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.user not in listing.watched_by.all():
        listing.watched_by.add(request.user)
    else:
        listing.watched_by.remove(request.user)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



def close_auction(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.closed = True
    listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



def add_comment(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comment = Comment(
            listing = Listing.objects.get(id=listing_id),
            commenter = request.user,
            content = request.POST.get("new_comment", False)
            )
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))



@login_required
def watchlist(request):
    listings = Listing.objects.filter(watched_by=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": listings})



def categories(request):
    return render(request, "auctions/categories.html", {
        "categories":item_categories
        })



def listings_by_category(request, category_str):
    category = ('NO', 'None')
    for cat in item_categories:
        if cat[1] == category_str:
            category = cat
    listings = Listing.objects.filter(category=category[0])
    return render(request, "auctions/index.html", {
        "listings": listings,
        "category_filter": category
        })