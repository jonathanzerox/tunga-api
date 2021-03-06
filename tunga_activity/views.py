from actstream.models import Action

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from tunga_activity.filters import ActionFilter
from tunga_activity.serializers import ActivitySerializer


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Activity Resource
    """
    queryset = Action.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAdminUser]
    filter_class = ActionFilter
