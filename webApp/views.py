from django.shortcuts import render, get_object_or_404 , redirect
from .models import Search,RawTweet
from .forms import SearchForm

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
				return render(request, 'webApp/search.html', {'form': form,'user':user,'searches':searches})
			
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
	tweets=selectTweets(alltweets,20)

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
			print ("Invalid login details")
			return render(request, 'webApp/login.html')
	else:
		return render(request, 'webApp/login.html', {})
@login_required
def user_logout_view(request):

	logout(request)

	return redirect('login')
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
	MyRe=re.compile(r"(\w+)((\s|\sOR\s|\sor\s|\s-)(\w+))?$")
	MyMatch=MyRe.match(KeywordsFieldValue)
	if MyMatch:
		subStrings=MyMatch.groups()
		if subStrings[3]!=None:
			Keywords=[subStrings[0],subStrings[3]]
			operator=subStrings[2]
		else:
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
	#------------------------------------SERCH-------------------------------
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
		#---------- All the conditions 
		if operator!=None:
			if operator!=' -':
				if text.find(Keywords[3])!=-1:
					score-=5
			elif operator!=' or 'or operator!=' OR ' :
				if text.find(Keywords[0])!=-1 or text.find(Keywords[0])!=-1:
					score+=5
			else :
				if text.find(Keywords[0])!=-1 and text.find(Keywords[0])!=-1:
					score+=10
		else:
			if text.find(Keywords[0])!=-1:
				score+=5

		pseudo=tweet['user']['screen_name']
		userLocation=tweet['user']['location']
		date=tweet['created_at']
		tweetLocation=tweet['coordinates']
		hashtags=[]
		for hashtag in tweet['entities']['hashtags']:
			hashtags.append(hashtag['text'])
		hashtags=' '.join(hashtags)
		images=[]
		if 'media' in tweet['entities']:
			for media in tweet['entities']['media']:
				images.append(media['media_url'])
			images = ' '.join(images)
			score+=4
		else:
			images = 'No image'
		isretweeted = tweet['retweeted']
		if isretweeted:
			score-=2

		t=RawTweet(SearchID=search,tweetID=tweetID,date =date , text=text, pseudo=pseudo, userLocation=userLocation,tweetLocation=tweetLocation, images=images,isretweeted=isretweeted,hashtags=hashtags,score=score)
		t.save()
def selectTweets(allTweets,nbOfTweetsToReturn):
	if len(allTweets)==0:
		return ('no tweet fond')
	else:	
		if nbOfTweetsToReturn>len(allTweets):
			nbOfTweetsToReturn=len(allTweets)-1

		tweets = []
		tweets.append(allTweets[0])
		nbOfTweets=1
		i=1
		maxi=len(allTweets)

		while nbOfTweets<nbOfTweetsToReturn and i<maxi:
			for t in tweets:
				if t.images==allTweets[i].images :
					isInSet=True
					break
				else:
					isInSet=False
			if not isInSet:
				tweets.append(allTweets[i])
				nbOfTweets=len(tweets)
				i=i+1
			else:
				i=i+1
		return (tweets)












