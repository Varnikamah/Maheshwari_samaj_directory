from django.contrib import admin
from .models import Member, FamilyMember, Area

class FamilyMemberInline(admin.TabularInline):
    model = FamilyMember
    extra = 0
    readonly_fields = ['display_age', 'display_spouse_age']
    fields = ['name', 'phone', 'dob', 'display_age', 'marital_status', 'spouse_name', 'display_spouse_age']

    def display_age(self, obj):
        return f"{obj.age} Yrs" if obj.age else "--"
    display_age.short_description = 'Member Age'

    def display_spouse_age(self, obj):
        return f"{obj.spouse_age} Yrs" if obj.spouse_age else "--"
    display_spouse_age.short_description = 'Spouse Age'

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['registration_no','name', 'phone_number', 'get_head_age', 'area', 'gotra']
    ordering = ['registration_no']
    readonly_fields = ['registration_no', 'get_head_age', 'get_head_spouse_age']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone_number', 'dob', 'get_head_age', 'marital_status', 'pin', 'is_head')
        }),
        ('Spouse Details', {
            'fields': ('spouse_name', 'spouse_phone', 'spouse_dob', 'get_head_spouse_age')
        }),
        ('Address & Location', {
            'fields': ('gotra', 'area', 'detailed_address')
        }),
    )
    
    inlines = [FamilyMemberInline]

    def get_head_age(self, obj):
        return f"{obj.age} Yrs" if obj.age else "--"
    get_head_age.short_description = 'Age'

    def get_head_spouse_age(self, obj):
        return f"{obj.head_spouse_age} Yrs" if obj.head_spouse_age else "--"
    get_head_spouse_age.short_description = 'Spouse Age'

admin.site.register(Area)