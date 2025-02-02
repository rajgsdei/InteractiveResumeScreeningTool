from djongo import models

class Resume(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    skills = models.JSONField()
    experience = models.FloatField(null=True, blank=True)
    education = models.TextField()
    resume_file = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.name
