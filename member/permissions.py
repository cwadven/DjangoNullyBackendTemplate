from member.exceptions import LoginRequiredException
from rest_framework.permissions import BasePermission


class IsMemberLogin(BasePermission):

    def has_permission(self, request, view):
        if bool(request.member and request.member.is_authenticated):
            return True
        raise LoginRequiredException()
