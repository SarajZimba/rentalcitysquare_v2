from api.views.sso_login import IssueSSOTokenAPIView
from django.urls import path

urlpatterns = []

urlpatterns += [
    # urls.py
    path("sso/issue-token/", IssueSSOTokenAPIView.as_view(), name="issue-sso-token"),
]


