from django.contrib import admin
from .models import (
    Policy,
    PolicyEligibility,
    PolicyRegion,
    TrainingPolicyDetail,
    WelfarePolicyDetail,
)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'source',
        'category',
        'is_active',
        'application_start',
        'application_end',
    )
    list_filter = ('source', 'category', 'is_active')
    search_fields = ('title',)


@admin.register(PolicyEligibility)
class PolicyEligibilityAdmin(admin.ModelAdmin):
    list_display = (
        'policy',
        'min_age',
        'max_age',
        'employment_status',
        'education_level',
    )


@admin.register(PolicyRegion)
class PolicyRegionAdmin(admin.ModelAdmin):
    list_display = (
        'policy',
        'sido_name',
        'sigungu_name',
    )


admin.site.register(TrainingPolicyDetail)
admin.site.register(WelfarePolicyDetail)
