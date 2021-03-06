from actstream.models import Action
from django.contrib.auth import get_user_model
from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from tunga_comments.models import Comment
from tunga_comments.serializers import CommentSerializer
from tunga_profiles.models import Connection
from tunga_profiles.serializers import ConnectionSerializer
from tunga_tasks.models import Task, Application, Participation, TaskRequest, Integration, ProgressEvent, ProgressReport, \
    IntegrationActivity
from tunga_tasks.serializers import ApplicationSerializer, ParticipationSerializer, \
    TaskRequestSerializer, SimpleTaskSerializer, SimpleIntegrationSerializer, SimpleProgressEventSerializer, \
    SimpleProgressReportSerializer, SimpleIntegrationActivitySerializer
from tunga_utils.serializers import SimpleUserSerializer


class SimpleActivitySerializer(serializers.ModelSerializer):
    action = serializers.CharField(source='verb')
    activity_type = serializers.SerializerMethodField()
    activity = GenericRelatedField({
        get_user_model(): SimpleUserSerializer(),
        Comment: CommentSerializer(),
        Connection: ConnectionSerializer(),
        Task: SimpleTaskSerializer(),
        Application: ApplicationSerializer(),
        Participation: ParticipationSerializer(),
        TaskRequest: TaskRequestSerializer(),
        ProgressEvent: SimpleProgressEventSerializer(),
        ProgressReport: SimpleProgressReportSerializer(),
        Integration: SimpleIntegrationSerializer(),
        IntegrationActivity: SimpleIntegrationActivitySerializer()
    }, source='action_object')

    class Meta:
        model = Action
        exclude = (
            'verb', 'actor_object_id', 'actor_content_type', 'action_object_object_id', 'action_object_content_type',
            'target_object_id', 'target_content_type'
        )

    def get_activity_type(self, obj):
        return get_instance_type(obj.action_object)


class ActivitySerializer(SimpleActivitySerializer):
    actor_type = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    actor = GenericRelatedField({
        get_user_model(): SimpleUserSerializer(),
        Integration: SimpleIntegrationSerializer()
    })
    target = GenericRelatedField({
        get_user_model(): SimpleUserSerializer(),
        Comment: CommentSerializer(),
        Connection: ConnectionSerializer(),
        Task: SimpleTaskSerializer(),
        Application: ApplicationSerializer(),
        Participation: ParticipationSerializer(),
        TaskRequest: TaskRequestSerializer(),
        ProgressEvent: SimpleProgressEventSerializer(),
        ProgressReport: SimpleProgressReportSerializer(),
        Integration: SimpleIntegrationSerializer(),
        IntegrationActivity: SimpleIntegrationActivitySerializer()
    })

    class Meta(SimpleActivitySerializer.Meta):
        pass

    def get_actor_type(self, obj):
        return get_instance_type(obj.actor)

    def get_target_type(self, obj):
        return get_instance_type(obj.target)


def get_instance_type(instance):
    if instance:
        return to_snake_case(str(type(instance).__name__))
    return None


def to_snake_case(components):
    return (components[0] + "".join(x.isupper() and '_{}'.format(x) or x for x in components[1:])).lower()
