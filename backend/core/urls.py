"""
URL configuration for core project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.scoreImagePage, name="scoreImagePage"),
    path("predictImage", views.predictImage, name="predictImage"),
    path("uploadModel", views.uploadModel, name="uploadModel"),
    path("mlflowModels", views.uploadModelFromMLflow, name="uploadModelFromMLflow"),
    path("api/mlflow-runs", views.get_mlflow_runs_api, name="mlflow_runs_api"),
    path("api/mlflow-download", views.download_mlflow_model_api, name="mlflow_download_api"),
    path("api/models", views.get_models_api, name="models_api"),
]

# Отдавать медиа файлы через S3 не нужно - они уже доступны по прямому URL
# Static() используется только для локального режима (USE_S3=False)
if not getattr(settings, "USE_S3", False):
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
