from django.db import models
from django.utils import timezone


class Url(models.Model):
    name = models.CharField(max_length=500, unique=True)
    expected_title = models.TextField()
    expected_response_by_http = models.IntegerField()
    expected_response_by_https = models.IntegerField()
    expected_text = models.TextField()
    check_details = models.TextField(default='ok')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Check(models.Model):
    url_name = models.ForeignKey('Url', on_delete=models.CASCADE)
    has_expected_title = models.BooleanField()
    actual_response_by_http = models.IntegerField()
    actual_response_by_https = models.IntegerField()
    has_expected_text = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.created_at


class LastParse(models.Model):
    parse_data = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.parse_data

    def save(self, *args, **kwargs):
        LastParse.objects.all().delete()
        super(LastParse, self).save(*args, **kwargs)


class TextCheckData(models.Model):
    text_check_data = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text_check_data

    def save(self, *args, **kwargs):
        TextCheckData.objects.all().delete()
        super(TextCheckData, self).save(*args, **kwargs)
