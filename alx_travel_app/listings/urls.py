from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet
from .views import InitiatePaymentView
router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)
from .views import InitiatePaymentView, VerifyPaymentView, CreateBookingView, ChapaCallbackView
urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('api/verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('api/bookings/', CreateBookingView.as_view(), name='create-booking'),
    path('api/payment-callback/', ChapaCallbackView.as_view(), name='payment-callback'),

]
