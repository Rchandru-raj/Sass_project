from django.urls import path
from .views import SignUpView, SignInView, ResetPasswordView, InviteMemberView,DeleteMemberView,UpdateMemberRoleView,RoleWiseUserCountView,OrganizationWiseMemberCountView,OrganizationRoleWiseUserCountView,OrganizationRoleWiseUserCountWithFiltersView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('resetpassword/', ResetPasswordView.as_view(), name='resetpassword'),
    path('invite_member/', InviteMemberView.as_view(), name='invite-member'),
    path('members/<int:member_id>/', DeleteMemberView.as_view(), name='delete-member'),
    path('members/update_role/<int:member_id>/', UpdateMemberRoleView.as_view(), name='update-member-role'),

     path('stats/role-wise-user-count/', RoleWiseUserCountView.as_view(), name='role-wise-user-count'),
    path('stats/org-wise-member-count/', OrganizationWiseMemberCountView.as_view(), name='org-wise-member-count'),
    path('stats/org-role-wise-user-count/', OrganizationRoleWiseUserCountView.as_view(), name='org-role-wise-user-count'),
    path('stats/org-role-wise-user-count-with-filters/', OrganizationRoleWiseUserCountWithFiltersView.as_view(), name='org-role-wise-user-count-with-filters'),
]
