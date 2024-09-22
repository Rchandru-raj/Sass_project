from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import  models
from rest_framework import status
from django.conf import settings
from .models import User, Organization, Role, Member
from .serializers import UserSerializer, OrganizationSerializer
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


class SignUpView(APIView):
    def post(self, request):
        user_data = request.data.get('user')
        org_data = request.data.get('organization')

        # Validate and create user
        
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            
            # Validate and create organization
            org_serializer = OrganizationSerializer(data=org_data)
            if org_serializer.is_valid():
                org = org_serializer.save()


                # Assign the "Owner" role to the user
                owner_role, created = Role.objects.get_or_create(name='Owner', org=org)

                # Create the Member with the Role instance
                Member.objects.create(user=user, org=org, role=owner_role)

                # Send a welcome email
                subject = 'Welcome to the Organization'
                message = 'You have been assigned the Owner role for the organization you created.'
                from_email = settings.DEFAULT_FROM_EMAIL  # Use your default email from settings
                recipient_list = [user.email]

                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )

                return Response({
                    'user': user_serializer.data,
                    'organization': org_serializer.data
                }, status=status.HTTP_201_CREATED)

        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)

            # Send confirmation email
            subject = 'Sign-In Successful'
            message = f'Hello {user.email}, you have successfully signed in.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            # Send reset email
            subject = 'Password Reset'
            message = f'Use the following token to reset your password: {token}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class InviteMemberView(APIView):
    def post(self, request):
        user_data = request.data.get('user')
        org_id = request.data.get('org_id')
        role_name = request.data.get('role_name')

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            org = get_object_or_404(Organization, id=org_id)
            try:
                role, created = Role.objects.get_or_create(name=role_name, org=org)
            except Role.DoesNotExist:
                return Response({'error': 'Role does not exist for this organization'}, status=status.HTTP_400_BAD_REQUEST)

            Member.objects.create(user=user, org=org, role=role)

            send_mail(
                'You have been invited to join an organization',
                'Please accept your invite.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response({"message": "User invited"}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class DeleteMemberView(APIView):
    def delete(self, request, member_id):
        print("memberid",member_id)
        member = Member.objects.filter(id=member_id).first()
        if member:
            member.delete()
            return Response({"message": "Member deleted successfully"})
        return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

class UpdateMemberRoleView(APIView):
    def patch(self, request, member_id):
        member = Member.objects.filter(id=member_id).first()
        if member:
            role_name = request.data.get('role_name')
            role = Role.objects.filter(name=role_name, org=member.org).first()
            if role:
                member.role = role
                member.save()
                return Response({"message": "Member role updated"})
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)




class RoleWiseUserCountView(APIView):
    def get(self, request):
        role_counts = Member.objects.values('role__name').annotate(count=models.Count('user')).order_by('role__name')
        return Response(role_counts, status=status.HTTP_200_OK)

class OrganizationWiseMemberCountView(APIView):
    def get(self, request):
        org_counts = Member.objects.values('org__name').annotate(count=models.Count('user')).order_by('org__name')
        return Response(org_counts, status=status.HTTP_200_OK)

class OrganizationRoleWiseUserCountView(APIView):
    def get(self, request):
        org_role_counts = Member.objects.values('org__name', 'role__name').annotate(count=models.Count('user')).order_by('org__name', 'role__name')
        return Response(org_role_counts, status=status.HTTP_200_OK)

class OrganizationRoleWiseUserCountWithFiltersView(APIView):
    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        status_filter = request.query_params.get('status')

        if from_date:
            from_date = datetime.fromisoformat(from_date)
        if to_date:
            to_date = datetime.fromisoformat(to_date)

        queryset = Member.objects.all()

        if from_date and to_date:
            queryset = queryset.filter(created_at__range=(from_date, to_date))
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        org_role_counts = queryset.values('org__name', 'role__name').annotate(count=models.Count('user')).order_by('org__name', 'role__name')
        return Response(org_role_counts, status=status.HTTP_200_OK)
