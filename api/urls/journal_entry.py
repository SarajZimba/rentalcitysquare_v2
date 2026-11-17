# from django.urls import path
# from api.views.journal_entry import JournalEntryAPIView, JournalEntryDetailAPIView

# urlpatterns = [
#     # Your other URL patterns
#     path('create_journal_entry/', JournalEntryAPIView.as_view(), name='create_journal_entry_api'),
#     path('journal_entry_detail/<int:pk>/', JournalEntryDetailAPIView.as_view(), name='journal_entry_detail'),
# ]

from django.urls import path
# from api.views.journal_entry import JournalEntryAPIView, JournalEntryDetailAPIView
from api.views.journal_entry import JournalEntryAPIView

urlpatterns = [
    # Your other URL patterns
    path('create_journal_entry/', JournalEntryAPIView.as_view(), name='create_journal_entry_api'),
    # path('journal_entry_detail/<int:pk>/', JournalEntryDetailAPIView.as_view(), name='journal_entry_detail'),
]