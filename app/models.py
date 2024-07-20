from django.db import models

# Create your models here.
class userdata(models.Model):
    Name = models.CharField(max_length=20,null=False)
    Phone = models.CharField(max_length=50,null=False)
    Password = models.CharField(max_length=50,null=False)
    Email = models.EmailField(max_length=50,blank=True,default='')
    Identity = models.BooleanField(null=False,default=False)
    
    def __str__(self):
        return self.Name



