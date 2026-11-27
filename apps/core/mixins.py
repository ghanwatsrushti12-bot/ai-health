"""Reusable class-based-view mixins shared across apps."""

from __future__ import annotations

from django.contrib.auth.mixins import UserPassesTestMixin


class StaffOrAdminRequiredMixin(UserPassesTestMixin):
    """Restricts a view to front-desk staff or administrators."""

    raise_exception = False  # redirect to login instead of a bare 403

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff_role or user.is_superuser)


class AdminRequiredMixin(UserPassesTestMixin):
    """Restricts a view to administrators only."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.role == "admin" or user.is_superuser
        )


class DoctorRequiredMixin(UserPassesTestMixin):
    """Restricts a view to the doctor role."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_doctor_role
