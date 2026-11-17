from api.views.review_logintoken import TokenVerifyView
from django.urls import path

urlpatterns = []

urlpatterns += [
    # urls.py
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]