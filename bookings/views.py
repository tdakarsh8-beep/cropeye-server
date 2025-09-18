from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Booking, BookingComment, BookingAttachment
from .serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    BookingUpdateSerializer,
    BookingStatusUpdateSerializer,
    BookingCommentSerializer,
    BookingCommentCreateSerializer,
    BookingAttachmentSerializer,
    BookingAttachmentCreateSerializer
)
from .permissions import CanManageBookings, CanViewBookings

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [CanManageBookings()]
        elif self.action in ['update', 'partial_update']:
            return [CanManageBookings()]
        elif self.action == 'update_status':
            return [CanManageBookings()]
        return [CanViewBookings()]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin or user.is_manager:
            return Booking.objects.all()
        return Booking.objects.filter(
            Q(created_by=user) | Q(booking_type='public')
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(booking=booking, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingAttachmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(booking=booking, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            booking.status = serializer.validated_data['status']
            if booking.status in ['approved', 'rejected']:
                booking.approved_by = request.user
            booking.save()
            return Response(BookingSerializer(booking).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BookingCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingComment.objects.filter(booking_id=self.kwargs['booking_pk'])

    def perform_create(self, serializer):
        booking = get_object_or_404(Booking, pk=self.kwargs['booking_pk'])
        serializer.save(booking=booking, user=self.request.user)

class BookingAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = BookingAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BookingAttachment.objects.filter(booking_id=self.kwargs['booking_pk'])

    def perform_create(self, serializer):
        booking = get_object_or_404(Booking, pk=self.kwargs['booking_pk'])
        serializer.save(booking=booking, uploaded_by=self.request.user) 