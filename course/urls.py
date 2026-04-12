from django.urls import path
from . import views


urlpatterns = [
    path("my_submissions", views.view_submission, name="submissions"),
    path("my_courses", views.my_courses, name="my_courses"),
    path("", views.course_list, name="course_list"),  # all courses
    path("<uuid:course_id>", views.course_detail, name="detail"),
    path("create/", views.create_courses, name="create"),
    path("update/<uuid:course_id>/", views.update_course, name="update"),
    path("delete/<uuid:course_id>", views.delete_course, name="delete"),
    path("enroll/<uuid:course_id>/", views.enroll_course, name="enroll"),
    path("ass-create/<uuid:course_id>/", views.create_assignment, name="ass_create"),
    path(
        "my_course_ass/<uuid:course_id>", views.my_course_assignment, name="course_ass"
    ),
    path(
        "<str:assignment_id>/<uuid:course_id>/submit/",
        views.submit_assigment,
        name="submit_ass",
    ),
    path(
        "<uuid:course_id>/<int:assignment_id>/update",
        views.update_submitted_assignment,
        name="update_submitted_ass",
    ),
    path(
        "<uuid:course_id>/<int:assignment_id>/delete",
        views.delete_submitted_ass,
        name="delete",
    ),
    path("add_review/<uuid:course_id>/", views.add_review, name="add_review"),
    path(
        "update_review/<int:id>/<uuid:course_id>/",
        views.update_review,
        name="update_review",
    ),
    path(
        "delete_review/<int:id>/<uuid:course_id>/",
        views.delete_review,
        name="delete_review",
    ),
    path("search", views.search_course, name="search"),
]
