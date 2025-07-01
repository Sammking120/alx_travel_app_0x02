from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Listing(models.Model):
    """
    Model to represent a property listing.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

class Booking(models.Model):
    """
    Model to represent a booking for a listing.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['check_in', 'check_out']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_after_check_in'
            ),
        ]

    def __str__(self):
        return f"Booking {self.pk} for {self.listing.title} by {self.guest.username}"

class Review(models.Model):
    """
    Model to represent a review for a listing.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['listing', 'created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'reviewer'],
                name='unique_review_per_user_per_listing'
            ),
        ]

    def __str__(self):
        return f"Review for {self.listing.title} by {self.reviewer.username}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    booking_reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='ETB')
    email = models.EmailField()
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.status}"
