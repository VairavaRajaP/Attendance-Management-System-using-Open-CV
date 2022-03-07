import os
import json
from django.db import models
from django.db.models.signals import class_prepared
# from ..source import add_new_user_database

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'


class TimeSlot(models.Model):
    time_slot_in = models.TimeField()
    time_slot_out = models.TimeField()
    time_slot_mid = models.TimeField()

    def __str__(self):
        return f'{self.time_slot_in} & {self.time_slot_out}'

    # def __str__(self):
    #     return f'{self.time_slot_in}'

    class Meta:
        unique_together = ('time_slot_in', 'time_slot_out')

class Designation(models.Model):
    name = models.CharField(max_length=64)
    time_slot_mid = models.ForeignKey(TimeSlot, db_column='time_slot_mid', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'





class Staff(models.Model):
    staff_id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=200)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    is_active = models.BooleanField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    # salary = models.FloatField()
    # teaching_since = models.DateField()

    def __str__(self):
        return f'{self.name} - {self.designation}, {self.department}'


class FaceData(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, primary_key=True)
    left_data = models.TextField()
    right_data = models.TextField()
    center_data = models.TextField()

    def __str__(self):
        return f'{self.staff}'


class Date(models.Model):
    remarks = (
        ('working_day', 'Working Day'),
        ('holiday', 'Holiday'),
        ('half_day', 'Half Day'),
        ('function_day', 'Function Day/Special Day'),
    )
    date = models.DateField()
    remark = models.CharField(max_length=64, choices=remarks)

    def __str__(self):
        return f'{self.date} - {self.remark}'


class Attendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.ForeignKey(Date, on_delete=models.CASCADE)

    in_time = models.TimeField(null=True)
    out_time = models.TimeField(null=True)
    work_duration = models.CharField(max_length=64, null=True)
    forenoon_remarks = models.CharField(max_length=64, null=True)
    afternoon_remarks = models.CharField(max_length=64, null=True)
    total_remarks = models.CharField(max_length=64, null=True)

    def __str__(self):
        return f'{self.staff.name} & {self.date}'

    class Meta:
        unique_together = ('staff', 'date')


