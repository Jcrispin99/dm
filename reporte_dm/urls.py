from django.urls import path
from django.views.generic import RedirectView

from descansos.admin_site import reporte_admin_site

urlpatterns = [
    path('admin/', reporte_admin_site.urls),
    path('', RedirectView.as_view(url='/admin/dashboard/', permanent=False)),
]
