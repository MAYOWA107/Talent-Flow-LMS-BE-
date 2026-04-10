from django.db import models
import uuid
from django.conf import settings


class Course(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to="course_videos/")
    duration = models.DurationField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class CourseReview(models.Model):
    RATING_CHOICES = [
        (1, "1 = Poor"),
        (2, "2 = fair"),
        (3, "3 = Good"),
        (4, "4 = Very Good"),
        (5, "5 = Excellent"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=1)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name}'s review on {self.course.title}"

    class Meta:
        unique_together = ["user", "course"]
        ordering = ["-created_at"]


class CourseRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="rating"
    )
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.average_rating} - {self.total_reviews} reviews"


# Track all enrolled student
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolls")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "course"]  # only one user can enroll in a course.

    def __str__(self):
        return f"{self.course}- Enrolled"


class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "course"]


# Asignment


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="assignments",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_score = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Submission
class Submission(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("submitted", "Submitted"),
        ("graded", "Graded"),
    ]
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    file = models.FileField(upload_to="submissions/", null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True)
    score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.assignment}"

    class Meta:
        unique_together = ["assignment", "student"]
