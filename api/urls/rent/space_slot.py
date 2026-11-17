from django.urls import path
from api.views.rent.space_slot import SpaceSlotListCreateView, SpaceSlotDetailView, SpaceSlotAvailableView, SpaceSlotOccupiedView, SpaceSlotOccupyView, SpaceSlotVacateView, SpaceSlotBulkCreateView, SpaceSlotStatsView, SpaceSlotExcelBulkCreateView

urlpatterns = [
    # CRUD operations
    path('spaces/', SpaceSlotListCreateView.as_view(), name='space-list-create'),
    path('spaces/<int:pk>/', SpaceSlotDetailView.as_view(), name='space-detail'),
    
    # Custom actions
    path('spaces/available/', SpaceSlotAvailableView.as_view(), name='space-available'),
    path('spaces/occupied/', SpaceSlotOccupiedView.as_view(), name='space-occupied'),
    path('spaces/<int:pk>/occupy/', SpaceSlotOccupyView.as_view(), name='space-occupy'),
    path('spaces/<int:pk>/vacate/', SpaceSlotVacateView.as_view(), name='space-vacate'),
    
    # Bulk operations and stats
    path('spaces/bulk-create/', SpaceSlotBulkCreateView.as_view(), name='space-bulk-create'),
    path('spaces/stats/', SpaceSlotStatsView.as_view(), name='space-stats'),
    path('spaces/bulk-create/excel', SpaceSlotExcelBulkCreateView.as_view(), name='space-bulk-create-excel'),

]