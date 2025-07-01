from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create users
        users = []
        for i in range(5):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'password': 'password123'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Created or retrieved {len(users)} users'))

        # Create listings
        listings = []
        cities = ['New York', 'London', 'Tokyo', 'Paris', 'Sydney']
        for i in range(10):
            listing, created = Listing.objects.get_or_create(
                title=f'Cozy Apartment {i+1}',
                defaults={
                    'owner': random.choice(users),
                    'description': f'Description for apartment {i+1}',
                    'address': f'{random.randint(100, 999)} Main St',
                    'city': random.choice(cities),
                    'country': 'Country',
                    'price_per_night': Decimal(random.uniform(50, 200)).quantize(Decimal('0.01')),
                    'max_guests': random.randint(1, 6),
                    'bedrooms': random.randint(1, 3),
                    'bathrooms': random.randint(1, 2)
                }
            )
            listings.append(listing)
        self.stdout.write(self.style.SUCCESS(f'Created or retrieved {len(listings)} listings'))

        # Create bookings
        bookings = []
        for i in range(20):
            check_in = timezone.now().date() + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 7))
            listing = random.choice(listings)
            nights = (check_out - check_in).days
            booking, created = Booking.objects.get_or_create(
                listing=listing,
                guest=random.choice(users),
                check_in=check_in,
                check_out=check_out,
                defaults={
                    'total_price': listing.price_per_night * nights,
                    'status': random.choice(['PENDING', 'CONFIRMED', 'CANCELLED'])
                }
            )
            bookings.append(booking)
        self.stdout.write(self.style.SUCCESS(f'Created or retrieved {len(bookings)} bookings'))

        # Create reviews
        reviews = []
        for i in range(15):
            listing = random.choice(listings)
            reviewer = random.choice(users)
            if reviewer != listing.owner:
                review, created = Review.objects.get_or_create(
                    listing=listing,
                    reviewer=reviewer,
                    defaults={
                        'rating': random.randint(1, 5),
                        'comment': f'Review comment {i+1}'
                    }
                )
                if created:
                    reviews.append(review)
        self.stdout.write(self.style.SUCCESS(f'Created {len(reviews)} reviews'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))