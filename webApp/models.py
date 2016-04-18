from django.db import models
from django.contrib.auth.models import User

class Search(models.Model):

	keywords=models.CharField(max_length=100)
	activateLocation=models.BooleanField(default=False)
	location=models.CharField(max_length=100,default='')
	locationRadius=models.CharField(max_length=5,default='0km')
	UserID=models.ForeignKey(User, on_delete=models.CASCADE,default=1)
	
	def __str__(self):

		if self.activateLocation:
			return 'Recherche de : '+self.keywords+' à '+self.location
		else:
			return 'Recherche de :' +self.keywords

class RawTweet(models.Model):
	SearchID=models.ForeignKey(Search, on_delete=models.CASCADE,default=1)
	tweetID = models.BigIntegerField(primary_key=True)
	date = models.CharField(max_length = 100)# a voir si y a possiblité d'utiliser DateTimefield
	text = models.TextField(max_length = 100)
	pseudo = models.CharField(max_length = 100)
	userLocation = models.CharField(max_length = 100)
	tweetLocation = models.CharField(max_length = 100, null=True)
	images = models.ImageField(upload_to = 'images/', blank=True)
	isretweeted = models.NullBooleanField()
	hashtags = models.CharField(max_length = 100)
	score=models.PositiveSmallIntegerField(default=0)


	def __str__(self):
		return self.pseudo+' le ' + self.date +' score '+ str(self.score)


	def getUrl(self):
		return ("https://twitter.com/{}/status/{}".format(self.pseudo,self.tweetID))




		
