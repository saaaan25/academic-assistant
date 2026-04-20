from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    pdf_name = models.CharField(max_length=255, unique=True)
    local_path = models.CharField(max_length=500)
    url = models.URLField(blank=True, null=True)
    version = models.CharField(max_length=50, default="1.0")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title