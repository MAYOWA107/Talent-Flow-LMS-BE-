from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    Course,
    Lesson,
    CourseReview,
    CourseProgress,
    Enrollment,
    Assignment,
    Submission,
)
from django.db.models import Avg


User = get_user_model()


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
        ]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video", "duration", "order"]


class CourseReviewSerilizer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ["id", "user", "course", "rating", "review_text", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    lessons = LessonSerializer(read_only=True, many=True)
    reviews = CourseReviewSerilizer(read_only=True, many=True)
    total_reviews = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_students = serializers.SerializerMethodField(method_name="get_total_students")

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor",
            "thumbnail",
            "duration",
            "total_students",
            "reviews",
            "lessons",
            "total_reviews",
            "average_rating",
            "created_at",
        ]

    def get_total_students(self, obj):
        return len(obj.enrolls.all())


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "course", "enrolled_at"]


class CourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseProgress
        fields = ["id", "course", "progress", "last_updated"]


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = [
            "id",
            "course",
            "lesson",
            "title",
            "description",
            "due_date",
            "max_score",
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "file",
            "text_answer",
            "score",
            "status",
            "submitted_at",
            "graded_at",
        ]


class SubmitAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["file", "text_answer"]

    def create(self, validated_data):
        user = self.context["request"].user
        assignment = self.context["assignment"]

        if assignment.due_date < timezone.now():
            raise ValidationError("Sorry!! Submission deadline has passed")

        if Submission.objects.filter(assignment=assignment, student=user).exists():
            raise ValidationError("You have already submitted this assignment")

        data = Submission.objects.create(
            student=user, assignment=assignment, **validated_data
        )
        return data
