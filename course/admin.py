from django.contrib import admin
from .models import Course, Enrollment, Assignment, Submission, CourseReview


admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(CourseReview)
