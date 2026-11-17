import jwt
from datetime import datetime, timedelta

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class IssueSSOTokenAPIView(APIView):
    """
    POST /api/sso/issue-token/
    Requires a normal authenticated request (existing long-lived JWT in
    the Authorization header). Returns a short-lived, single-purpose
    token for the SSO redirect flow -- NOT the same as the caller's
    own long-lived token.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        sso_token = jwt.encode(
            {
                "user_id": user.id,
                "purpose": "sso",
                "exp": datetime.utcnow() + timedelta(seconds=60),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        redirect_url = f"/sso-login/?token={sso_token}"

        return Response(
            {"redirect_url": redirect_url},
            status=status.HTTP_200_OK,
        )