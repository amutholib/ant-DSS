from django.urls import path
from .views import Index, AnomData, DSupport, autocomplete_bustype, autocomplete_missionprimary, user_login, user_logout, generate_pdf

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('data/', AnomData.as_view(), name='anomdata'),
    path('analysis/', DSupport.as_view(), name='analysis'),
    path('pdf/', generate_pdf, name='pdf'),
    
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('autocomplete/bustype/', autocomplete_bustype, name='autocomplete_bustype'),
    path('autocomplete/missionprimary/', autocomplete_missionprimary, name='autocomplete_missionprimary'),
]