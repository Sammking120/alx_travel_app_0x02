from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated 
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from drf_yasg.utils import swagger_auto_schema
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import uuid
from .models import Payment, Booking, Listing
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .tasks import send_booking_confirmation_email



class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="List all listings or create a new listing",
        responses={200: ListingSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all bookings or create a new booking",
        responses={200: BookingSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Save booking with the current authenticated user as guest
        booking = serializer.save(guest=self.request.user)

        # Prepare email data
        email = booking.guest.email
        details = f"Location: {booking.location}\nDate: {booking.date}"

        # Send async email
        send_booking_confirmation_email(email, details)
        
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
  
class InitiatePaymentView(APIView):
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    def post(self, request):
        # data = request.data
        email = str(request.data.get("email", "")).strip()
        amount = str(request.data.get('amount', "")).strip()
        first_name = str(request.data.get('first_name', "")).strip()
        last_name = str(request.data.get('last_name', "")).strip()
        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address"}, status=400)

        if not all([email, amount, first_name, last_name]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Create unique transaction reference
        tx_ref = str(uuid.uuid4())

        payload = {
            "amount": str(amount),  # Ensure amount is a string",
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": "https://yourdomain.com/payment/callback/",
            "return_url": "https://yourdomain.com/payment/success/",
            "customization": {
                "title": "Booking payment"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        chapa_url = "https://api.chapa.co/v1/transaction/initialize"

        try:
            chapa_response = requests.post(chapa_url, json=payload, headers=headers)
            chapa_data = chapa_response.json()
            print("Response from Chapa:", chapa_response.json())  # Debugging line
            if chapa_response.status_code == 200 and chapa_data['status'] == 'success':
                checkout_url = chapa_data['data']['checkout_url']
                transaction_id = chapa_data['data']['tx_ref']

                # Save to database
                Payment.objects.create(
                    booking_reference=tx_ref,
                    amount=amount,
                    currency="ETB",
                    email=email,
                    transaction_id=transaction_id,
                    status="pending",
                )

                return Response({"checkout_url": checkout_url}, status=status.HTTP_200_OK)

            return Response({"error": "Failed to initialize payment", "details": chapa_data}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(chapa_response.text)
        
class VerifyPaymentView(APIView):
    def get(self, request):
        tx_ref = request.query_params.get('tx_ref')

        if not tx_ref:
            return Response({'error': 'Transaction reference (tx_ref) is required'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        try:
            response = requests.get(verify_url, headers=headers)
            result = response.json()

            if response.status_code == 200 and result['status'] == 'success':
                status_from_chapa = result['data']['status']  # Can be "success", "pending", or "failed"

                # Update your Payment model
                try:
                    payment = Payment.objects.get(booking_reference=tx_ref)
                    if status_from_chapa == "success":
                        payment.status = "success"
                    elif status_from_chapa == "failed":
                        payment.status = "failed"
                    else:
                        payment.status = "pending"
                    payment.save()
                except Payment.DoesNotExist:
                    return Response({"error": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

                return Response({
                    "message": "Payment verification completed",
                    "status": payment.status,
                    "transaction_id": payment.transaction_id,
                    "booking_reference": tx_ref
                })

            return Response({"error": "Verification failed", "details": result}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, Payment
import uuid, requests
from django.conf import settings

class CreateBookingView(APIView):
    def post(self, request):
        # Assume required booking data is in request.data
        # Save booking
        booking = Booking.objects.create(
            user=request.user,
            service=request.data['service'],
            date=request.data['date'],
            # other fields...
        )

        tx_ref = str(uuid.uuid4())
        amount = request.data['amount']  # get or calculate amount
        email = request.user.email

        chapa_payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "tx_ref": tx_ref,
            "callback_url": f"https://yourdomain.com/api/payment-callback/",
            "return_url": f"https://yourdomain.com/payment/success/",
            "customization[title]": "Booking Payment"
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=chapa_payload, headers=headers)
        result = response.json()

        if result.get('status') == 'success':
            # Save payment
            Payment.objects.create(
                booking_reference=tx_ref,
                amount=amount,
                email=email,
                transaction_id=result['data']['tx_ref'],
                status="pending"
            )
            return Response({'checkout_url': result['data']['checkout_url']})
        else:
            return Response({'error': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)
from .tasks import send_payment_confirmation_email

class ChapaCallbackView(APIView):
    def post(self, request):
        tx_ref = request.data.get('tx_ref')

        if not tx_ref:
            return Response({'error': 'Missing tx_ref'}, status=400)

        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        verify_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        try:
            response = requests.get(verify_url, headers=headers).json()

            if response['status'] == 'success':
                chapa_status = response['data']['status']
                payment = Payment.objects.get(booking_reference=tx_ref)

                if chapa_status == 'success':
                    payment.status = 'success'
                    payment.save()
                    # Call Celery email task
                    send_payment_confirmation_email(payment.email, payment.booking_reference)
                elif chapa_status == 'failed':
                    payment.status = 'failed'
                    payment.save()

                return Response({'message': 'Payment status updated'})
            else:
                return Response({'error': 'Chapa verification failed'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
