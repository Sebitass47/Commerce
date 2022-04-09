from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id} {self.category}"

class Auctions(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    offer = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    category_id = models.ForeignKey(Categories, null=True, on_delete=models.SET_NULL, related_name="auction_category")
    available = models.BooleanField()

    def __str__(self):
        return f"{self.title}: {self.description}"

class Bids(models.Model):
    product_id = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction_bids")
    offer = models.PositiveIntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids", null=True)
    winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product_id}: {self.offer}"

class Comments(models.Model):
    comment = models.CharField(max_length=250)
    product_id = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction_comments")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments", null=True)

    def __str__(self):
        return f"{self.product_id}: {self.comment}"


class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_watchlist")
    auction_id = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="auction_watchlist")
    
    def __str__(self):
        return f"{self.user_id.id}: {self.auction_id.description}"