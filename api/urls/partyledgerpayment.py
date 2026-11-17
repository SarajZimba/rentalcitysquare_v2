# urls.py
# path('api/create_party_payment_journal/', PartyPaymentJournalAPIView.as_view()),


from django.urls import path
from api.views.partyledgerpayment import PartyPaymentJournalAPIView

urlpatterns = [
    # Your other URL patterns
    path('create_party_payment_journal/', PartyPaymentJournalAPIView.as_view()),
]