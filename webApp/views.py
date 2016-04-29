from django.shortcuts import render, get_object_or_404 , redirect
from .models import Search,RawTweet,SelectedTweets
from .forms import SearchForm
from django.http import HttpResponse

from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream


#------------------------------------Views-------------------------------------
@login_required 
def Search_view(request):
	#-----------Get the loged in user--------------
	userName=request.user
	user=User.objects.get(username=userName)
	#-----------Get all the previous searches made by the user--------------
	searches=Search.objects.filter(UserID=user).order_by("-id")[:10]
	#-----------Commit the current search--------------
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			search = form.save(commit=False)
			search.UserID=user
			search.save()
			#-----------Location activated --------------
			if request.POST.get('activatelocation'):
				search.activateLocation=request.POST.get('activatelocation')
				search.location=request.POST.get('location')
				search.save()
			#------------------Check if the search was ok----------------	
			s=searchTweets(search)
			if s!="Search don't match MyRegEx":
				return redirect('Result',pk=search.pk)
			else:
				form = SearchForm()
				Search.objects.filter(UserID=user).order_by("-id")[0].delete()
				return render(request, 'webApp/search.html', {'form': form,'user':user,'searches':searches,'RegExError':True})
			
	else:
		form = SearchForm()
		return render(request, 'webApp/search.html', {'form': form,'user':user,'searches':searches})
@login_required 	
def Result_view(request,pk):

	search=Search.objects.get(pk=pk)
	#__________get the user______________________________________________
	user=search.UserID
	#____________get the last searches________________________________
	searches=Search.objects.filter(UserID=user).order_by("-id")[:10]
	#_____________get the tweets associated with the last search___________________
	alltweets=RawTweet.objects.filter(SearchID=search).order_by("-score")
	selectTweets(alltweets,50)
	tweets=SelectedTweets.objects.filter(SearchID=search).order_by("-score")
	return render(request,'webApp/result.html',{'tweets':tweets,'user':user,'searches':searches})
def user_login_view(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
				login(request, user)
				return redirect('Search')
		else:
			return render(request, 'webApp/login.html', {'loginError':True})
	else:
		return render(request, 'webApp/login.html', {})
@login_required
def user_logout_view(request):

	logout(request)

	return redirect('login')
@login_required
def deleteTweet_view(request):
	if request.method =='POST':
		tweetIDStr=request.POST['tweet']
		tweetID=int(tweetIDStr)
		SelectedTweets.objects.get(tweetID=tweetID).delete()
	return HttpResponse(status = 200)
@login_required	
def deleteSearch_view(request):
	if request.method =='POST':
		searchIDStr=request.POST['searchPK']
		searchID=int(searchIDStr)
		Search.objects.get(pk=searchID).delete()
	return HttpResponse(status = 200)

def error_view(request):
	return render(request, 'webApp/error.html', {})
#------------------------------------Algos-------------------------
def searchTweets(search):
	# Import the necessary methods from "twitter" library
	from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
	import geocoder,re

	#---------------------Get the serch of the user -----------------------
	q=Search.objects.all().order_by("-id")[0]
	#'''we can have a conflit her so we have to select the searches of a user and order them'''
	KeywordsFieldValue=q.keywords
	#-----------------------------RegEx--------------------------------
	MyRe=re.compile(r"([A-Z]?[a-z\d\@\#\'\s]+)+(\s|\sOR\s|\s-)?([A-Z]?[a-z\d\s\@\#\']+)?$")

	MyMatch=MyRe.match(KeywordsFieldValue)

	if MyMatch:
		subStrings=MyMatch.groups()

		if subStrings[2]!=None:
			Keywords=[subStrings[0],subStrings[2]]
			operator=subStrings[1]
		else:
			Keywords=[subStrings[0]]
			operator=None
	else:
		MyCapRe=re.compile(r"([A-Z]+$)")
		MyCapMatch=MyCapRe.match(KeywordsFieldValue)
		if MyCapMatch:
			subStrings=MyCapMatch.groups()
			Keywords=[subStrings[0]]
			operator=None
		else:
			return ("Search don't match MyRegEx")

	#---------------------SEARCH-API connection------------------------------
	ACCESS_TOKEN = '2732579483-CG9MLjyB6b51dPO8sG15H2ORJ1WcqxG7NBV6wON'
	ACCESS_SECRET = '4nDPSz76MFAfZvYuy2JbsxbZ1NpcjEfQVYsfIMIBr56Xj'
	CONSUMER_KEY = 'u1ZDxwGdAlkVDFGroEDDObQ3m'
	CONSUMER_SECRET = 'vwYqK8F9neS0NV516wsrYBsf4nunynhrjAljMVmjCDE7KnAw1A'

	oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

	twitter = Twitter(auth=oauth)
	#------------------------------------SEARCH-------------------------------
	if search.activateLocation:
		geo=geocoder.google(search.location).latlng
		geocode=str(geo[0])+','+str(geo[0])+','+search.locationRadius
		Tweets=twitter.search.tweets(q=KeywordsFieldValue,lang='fr',count=100,geocode=geocode)
	else:
		Tweets=twitter.search.tweets(q=KeywordsFieldValue,lang='fr',count=100)

	for tweet in Tweets["statuses"]:
		score=0
		tweetID=int(tweet['id_str'])
		text=tweet['text']
		pseudo=tweet['user']['screen_name']
		userLocation=tweet['user']['location']
		date=tweet['created_at']
		tweetLocation=tweet['coordinates']
		hashtags=[]
		for hashtag in tweet['entities']['hashtags']:
			hashtags.append(hashtag['text'])
		hashtags=' '.join(hashtags)
		images=[]
		isretweeted = tweet['retweeted']
		if 'media' in tweet['entities']:
			for media in tweet['entities']['media']:
				images.append(media['media_url'])
			images = ' '.join(images)
		else:
			images = 'No image'
	
		#---------- Scoring the tweets 
		if operator!=None :
			if operator==' -':
				if text.find(Keywords[1])==-1 and text.find(Keywords[0])!=-1 :
					score+=7
			elif operator==' OR ':
				if text.find(Keywords[0])!=-1 or text.find(Keywords[1])!=-1 :
					score+=7
			else :
				if text.find(Keywords[0])!=-1 and text.find(Keywords[1])!=-1:
					score+=7
				if text.find(Keywords[0])==-1 or text.find(Keywords[1])==-1:
					score+=4
		else:
			if text.find(Keywords[0])!=-1:
				score+=7
		if isretweeted == False and tweetLocation != None :
			score+=10
		if images!= 'No image':
			score+=3
		#------------Save tweet in database like an object
		t=RawTweet(SearchID=search,tweetID=tweetID,date =date , text=text, pseudo=pseudo, userLocation=userLocation,tweetLocation=tweetLocation, images=images,isretweeted=isretweeted,hashtags=hashtags,score=score)
		t.save()


def selectTweets(allTweets,nbOfTweetsToReturn):
	if len(allTweets)==0:
		return ('no tweet found')
	else:	
		if nbOfTweetsToReturn>len(allTweets):
			nbOfTweetsToReturn=len(allTweets)-1

		tweets = []
		tweets.append(allTweets[0])
		t=SelectedTweets(SearchID=allTweets[0].SearchID,tweetID=allTweets[0].tweetID,pseudo=allTweets[0].pseudo)
		t.save()
		nbOfTweets=1
		i=1
		maxi=len(allTweets)

		while nbOfTweets<nbOfTweetsToReturn and i<maxi:
			for t in tweets:
				if t.images==allTweets[i].images and t.score==allTweets[i].score :
					isInSet=True
					break
				else:
					isInSet=False
			if not isInSet:
				tweets.append(allTweets[i])
				t=SelectedTweets(SearchID=allTweets[i].SearchID,tweetID=allTweets[i].tweetID,pseudo=allTweets[i].pseudo)
				t.save()
				nbOfTweets=len(tweets)
				i=i+1
			else:
				i=i+1
		RawTweet.objects.filter(SearchID=allTweets[0].SearchID).delete()
		tweets=[]

















