import datetime
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Avg
from django.db.models.query_utils import Q
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import TokenSerializer, PasswordResetSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tunga_auth.models import USER_TYPE_CHOICES, USER_TYPE_DEVELOPER
from tunga_profiles.models import Connection, DeveloperApplication, UserProfile
from tunga_utils.mixins import GetCurrentUserAnnotatedSerializerMixin
from tunga_utils.serializers import SimpleProfileSerializer, SimpleUserSerializer, SimpleWorkSerializer, \
    SimpleEducationSerializer, SimpleConnectionSerializer


class UserSerializer(SimpleUserSerializer, GetCurrentUserAnnotatedSerializerMixin):
    display_name = serializers.CharField(read_only=True, required=False)
    display_type = serializers.CharField(read_only=True, required=False)
    is_developer = serializers.BooleanField(read_only=True, required=False)
    is_project_owner = serializers.BooleanField(read_only=True, required=False)
    profile = SimpleProfileSerializer(read_only=True, required=False, source='userprofile')
    work = SimpleWorkSerializer(many=True, source='work_set', read_only=True, required=False)
    education = SimpleEducationSerializer(many=True, source='education_set', read_only=True, required=False)
    can_connect = serializers.SerializerMethodField(read_only=True, required=False)
    request = serializers.SerializerMethodField(read_only=True, required=False)
    connection = serializers.SerializerMethodField(read_only=True, required=False)
    tasks_created = serializers.SerializerMethodField(read_only=True, required=False)
    tasks_completed = serializers.SerializerMethodField(read_only=True, required=False)
    satisfaction = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = get_user_model()
        exclude = ('password', 'is_superuser', 'groups', 'user_permissions', 'is_active')
        read_only_fields = (
            'username', 'email', 'date_joined', 'last_login', 'is_staff'
        )

    def get_can_connect(self, obj):
        current_user = self.get_current_user()
        if current_user:
            if not current_user.is_developer and not obj.is_developer or current_user.pending:
                return False
            has_requested = obj.connections_initiated.filter(to_user=current_user).count()
            if has_requested:
                return False
            has_accepted_or_been_requested = obj.connection_requests.filter(
                Q(accepted=True) | Q(responded=False), from_user=current_user).count() > 0
            return not has_accepted_or_been_requested
        return False

    def get_request(self, obj):
        current_user = self.get_current_user()
        if current_user:
            try:
                connection = obj.connections_initiated.get(to_user=current_user, responded=False)
                return connection.id
            except:
                pass
        return None

    def get_connection(self, obj):
        current_user = self.get_current_user()
        if current_user:
            try:
                connection = Connection.objects.filter(
                    (Q(to_user=current_user) & Q(from_user=obj)) | (Q(to_user=obj) & Q(from_user=current_user))
                ).latest('created_at')
                return SimpleConnectionSerializer(connection).data
            except:
                pass
        return None

    def get_tasks_created(self, obj):
        return obj.tasks_created.count()

    def get_tasks_completed(self, obj):
        return obj.participation_set.filter(task__closed=True, accepted=True).count()

    def get_satisfaction(self, obj):
        score = None
        if obj.type == USER_TYPE_DEVELOPER:
            score = obj.participation_set.filter(
                task__closed=True, accepted=True
            ).aggregate(satisfaction=Avg('task__satisfaction'))['satisfaction']
            if score:
                score = '{:0,.0f}%'.format(score*10)
        return score


class AccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'type', 'image')

    def validate(self, attrs):
        super(AccountInfoSerializer, self).validate(attrs)

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user:
            raise serializers.ValidationError('Something went wrong')

        password = self.initial_data.get('password', None)
        if not password or not user.check_password(password):
            raise serializers.ValidationError({'password': 'Wrong password'})
        return attrs


class TungaRegisterSerializer(RegisterSerializer):
    type = serializers.ChoiceField(required=True, choices=USER_TYPE_CHOICES, allow_blank=False, allow_null=False)
    first_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    last_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    key = serializers.CharField(required=False, write_only=True, allow_blank=True, allow_null=True)

    def save(self, request):
        user_type = self.initial_data.get('type', None)
        confirm_key = self.initial_data.get('key', None)
        application = None
        if user_type == USER_TYPE_DEVELOPER:
            try:
                application = DeveloperApplication.objects.get(confirmation_key=confirm_key, used=False)
            except:
                raise ValidationError({'key': 'Invalid key'})
        user = super(TungaRegisterSerializer, self).save(request)
        user.type = user_type
        user.first_name = self.initial_data['first_name']
        user.last_name = self.initial_data['last_name']
        user.save()
        if application:
            application.used = True
            application.used_at = datetime.datetime.utcnow()
            application.save()

            profile = UserProfile(user=user, phone_number=application.phone_number, country=application.country)
            profile.city = application.city
            profile.save()
        return user


class TungaTokenSerializer(TokenSerializer):
    user = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = TokenSerializer.Meta.model
        fields = ('key', 'user')

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data


class TungaPasswordResetSerializer(PasswordResetSerializer):

    def get_email_options(self):
        return {
            "email_template_name": "registration/password_reset_email.txt",
            "html_email_template_name": "registration/password_reset_email.html"
        }

