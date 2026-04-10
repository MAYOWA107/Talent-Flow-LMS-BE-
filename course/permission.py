from rest_framework.permissions import BasePermission
from .models import Enrollment


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "instructor"


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsEnrolled(BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get("course_id")

        if not course_id:
            return False

        return Enrollment.objects.filter(
            user=request.user, course_id=course_id
        ).exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user
