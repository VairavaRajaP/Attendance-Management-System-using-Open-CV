from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from . import models, forms
# Register your models here.


class StaffAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'designation', 'department', 'time_slot', 'is_active')
    list_filter = ('department', 'time_slot', 'designation', 'is_active')


# class AttendAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'date')
#     list_filter = ('name', 'date')


class DateAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'remark')
    list_filter = ('date', 'remark')


class AttendListAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'staff', 'date', 'in_time', 'out_time', 'work_duration', 'forenoon_remarks', 'afternoon_remarks', 'total_remarks')
    list_filter = ('staff', 'date')



admin.site.register(models.Staff, StaffAdmin)
admin.site.register(models.Department)
admin.site.register(models.TimeSlot)
admin.site.register(models.FaceData)
admin.site.register(models.Designation)
admin.site.register(models.Date, DateAdmin)
# admin.site.register(models.Attendance, AttendAdmin)
admin.site.register(models.Attendance, AttendListAdmin)
