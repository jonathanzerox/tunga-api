from django.contrib import admin

from tunga_tasks.models import Task, Application, Participation, TaskRequest, SavedTask, ProgressEvent, ProgressReport, \
    Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'closed', 'created_at')


class ParticipationInline(admin.TabularInline):
    model = Participation
    exclude = ('created_by',)
    extra = 1

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('summary', 'user', 'closed', 'skills_list', 'created_at')
    list_filter = ('closed', 'apply')
    inlines = (ParticipationInline,)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.created_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'responded', 'accepted', 'created_at')
    list_filter = ('accepted',)


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'responded', 'accepted', 'share', 'created_at')
    list_filter = ('accepted',)


@admin.register(TaskRequest)
class TaskRequestAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'type', 'created_at')


@admin.register(SavedTask)
class SavedTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')


@admin.register(ProgressEvent)
class ProgressEventAdmin(admin.ModelAdmin):
    list_display = ('task', 'title', 'type', 'due_at')
    list_filter = ('type', 'due_at')


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'percentage', 'created_at')
    list_filter = ('status', 'created_at')
