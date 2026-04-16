from django.db import models

class Alert(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)

    def __clstr__(self):
        return f"{self.file_path} - {self.message}"