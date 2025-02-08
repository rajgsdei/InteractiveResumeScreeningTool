from djongo import models
import uuid

class Resume(models.Model):
    resume_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    skills = models.JSONField()
    experience = models.FloatField(null=True, blank=True)
    current_ctc = models.FloatField(null=True, default=0)
    expected_ctc = models.FloatField(null=True, default=0)
    education = models.TextField()
    resume_file = models.FileField(upload_to='uploaded/resumes/')  # Store resumes
    applied_for = models.CharField(max_length=255, blank=True, null=True)  # Job role
    hiring_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Hired", "Hired"), ("Rejected", "Rejected")],
        default="Pending",
    )  # Track candidate status
    recruiter_feedback = models.TextField(blank=True, null=True)  # Comments from recruiter
    score = models.FloatField(blank=True, null=True)  # AI-generated score

    def __str__(self):
        return f"{self.name} - {self.applied_for} - {self.hiring_status}"
