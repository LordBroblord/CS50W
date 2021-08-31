from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


item_categories = [('', 'None'), ('IT', 'Items'), ('PB', 'Poké Balls'), ('ME', 'Medicine'), ('TM', 'TMs & HMs'), ('BE', 'Berries'), ('KI', 'Key Items')]


class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="objects_listed")
    image_URL = models.URLField(max_length=500, blank=True)
    category = models.CharField(max_length=2, choices=item_categories, blank=True, default='')
    closed = models.BooleanField(default=False)
    watched_by = models.ManyToManyField(User, related_name="watchlist", blank=True)

    def __str__(self):
        return f"{self.title}, sold by {self.seller} for {self.starting_bid}£"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="current_bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bid: {self.value}£ for the item '{self.listing}' by {self.bidder}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.commenter} on the item '{self.listing}'"