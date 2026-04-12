from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from .permission import IsInstructor, IsStudent, IsEnrolled
from django.db.models import Q
from rest_framework.pagination import LimitOffsetPagination

from .models import (
    Course,
    Enrollment,
    CourseProgress,
    Assignment,
    Submission,
    CourseReview,
)

from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    AssignmentSerializer,
    CourseProgressSerializer,
    SubmissionSerializer,
    SubmitAssignmentSerializer,
    CourseReviewSerilizer,
    # CourseRatingSerializer,
)


# list all courses
@api_view(["GET"])
def course_list(request):
    courses = (
        Course.objects.select_related("instructor")
        .prefetch_related("lessons", "reviews__user", "enrolls")
        .annotate(
            average_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
            total_reviews=Count("reviews"),
        )
    )

    query = request.query_params.get("query")
    if query:
        courses = courses.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(instructor__full_name__icontains=query)
        )
    paginator = LimitOffsetPagination()
    paginator.default_limit = 4
    result_page = paginator.paginate_queryset(courses, request)
    serializer = CourseSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


# course detail
@api_view(["GET"])
def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related("instructor")
        .prefetch_related("lessons", "reviews__user", "enrolls")
        .annotate(
            average_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
            total_reviews=Count("reviews"),
        ),
        id=course_id,
    )
    serializer = CourseSerializer(course)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_courses(request):
    serializer = CourseSerializer(data=request.data)
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    if serializer.is_valid():
        serializer.save(instructor=request.user)
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsInstructor])
def update_course(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    title = request.data.get("title", course.title)
    description = request.data.get("description", course.description)
    thumbnail = request.data.get("thumbnail", course.thumbnail)
    duration = request.data.get("duration", course.duration)

    if course.instructor != user:
        return Response(
            {"message": "You are not allowed to update this course"},
            status=status.HTTP_403_FORBIDDEN,
        )

    course.title = title
    course.description = description
    course.thumbnail = thumbnail
    course.duration = duration

    course.save()

    serializer = CourseSerializer(course)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_course(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return Response(
            {"message": "You are not allowed to delete this course"},
            status=status.HTTP_403_FORBIDDEN,
        )
    course.delete()
    return Response({"message": "course deleted successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def enroll_course(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)

    # avoid duplicate enrollment
    if Enrollment.objects.filter(user=user, course=course).exists():
        return Response(
            {"message": "This user has already enrolled."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    Enrollment.objects.create(user=user, course=course)
    CourseProgress.objects.create(user=user, course=course)

    return Response(
        {"message": "Enrolled Successfully"}, status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_courses(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related(
        "course__instructor"
    )
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)


# get your progress
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_progress(request):
    user = request.user
    progress = CourseProgress.objects.filter(user=user).select_related(
        "course__instructor"
    )
    serializer = CourseProgressSerializer(progress, many=True)
    return Response(serializer.data)


# create assignment
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_assignment(request, course_id):
    user = request.user

    course = get_object_or_404(Course, id=course_id)

    if course.instructor != user:
        return Response(
            {"message": "You are not allowed to add assignment to this course"},
            status=403,
        )

    serializer = AssignmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# list assignments for a course
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnrolled])
def my_course_assignment(request, course_id):
    assignments = Assignment.objects.filter(course_id=course_id)
    a = Assignment.objects.get(id=1)
    print(a.course_id)

    serializer = AssignmentSerializer(assignments, many=True)
    return Response(serializer.data)


# submit assignment
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEnrolled])
def submit_assigment(request, assignment_id, course_id):

    assignment = get_object_or_404(Assignment, id=assignment_id, course_id=course_id)
    serializer = SubmitAssignmentSerializer(
        data=request.data, context={"request": request, "assignment": assignment}
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            {"message": "Assignment submitted successfully"},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsStudent])
def update_submitted_assignment(request, course_id, assignment_id):
    user = request.user
    assignment = get_object_or_404(Assignment, course_id=course_id, id=assignment_id)
    submitted_ass = get_object_or_404(Submission, student=user, assignment=assignment)

    if assignment.due_date < timezone.now():
        return Response(
            {
                "message": "oops!! This assignment does not accept any response again. The due date has elapsed."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    submitted_ass.file = request.data.get("file", submitted_ass.file)
    submitted_ass.text_answer = request.data.get(
        "text_answer", submitted_ass.text_answer
    )
    submitted_ass.save()

    serializer = SubmitAssignmentSerializer(submitted_ass)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsStudent])
def delete_submitted_ass(request, course_id, assignment_id):
    user = request.user
    assignment = get_object_or_404(Assignment, course_id=course_id, id=assignment_id)
    submission = get_object_or_404(Submission, assignment=assignment, student=user)

    if assignment.due_date < timezone.now():
        return Response(
            {
                "message": "Sorry!! Due date has passed. Assignment cannot be deleted again."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    submission.delete()
    return Response(
        {"message": "Your ungraded assignment has been deleted successfully."}
    )


# view your submission
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_submission(request):
    user = request.user
    submissions = Submission.objects.filter(student=user).select_related(
        "assignment__course"
    )
    serializer = SubmissionSerializer(submissions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def add_review(request, course_id):
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    rating = request.data.get("rating")
    review_text = request.data.get("review_text")

    # avoid duplicate reviews

    if CourseReview.objects.filter(user=user, course_id=course_id).exists():
        return Response(
            {"message": "oops!! You have already dropped a review"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    review = CourseReview.objects.create(
        user=user, course=course, rating=rating, review_text=review_text
    )

    serializer = CourseReviewSerilizer(review)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsStudent])
def update_review(request, id, course_id):
    user = request.user
    review = get_object_or_404(CourseReview, id=id, course_id=course_id)
    rating = request.data.get("rating", review.rating)
    review_text = request.data.get("review_text", review.review_text)

    if review.user != user:
        return Response(
            {"message": "You are not allowed to update this review"},
            status=status.HTTP_403_FORBIDDEN,
        )

    review.rating = rating
    review.review_text = review_text
    review.save()

    serializer = CourseReviewSerilizer(review)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsStudent])
def delete_review(request, id, course_id):
    user = request.user
    review = get_object_or_404(CourseReview, id=id, course_id=course_id)

    if review.user != user:
        return Response(
            {"message": "You are not allowed to delete this review"},
            status=status.HTTP_403_FORBIDDEN,
        )
    review.delete()

    return Response({"message": "review deleted succesfully."})


@api_view(["GET"])
def search_course(request):
    query = request.query_params.get("query")
    if not query:
        return Response(
            {"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    courses = Course.objects.filter(
        Q(title__icontains=query)
        | Q(description__icontains=query)
        | Q(instructor__full_name__icontains=query)
    )

    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)
