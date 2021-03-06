from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from ckeditor.fields import RichTextField

# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=50, unique=True)
    #content = models.TextField()
    content = RichTextField(blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        if len(self.content) >= 25:
            return f"{self.content[:25]}..."
        return self.content


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.body
