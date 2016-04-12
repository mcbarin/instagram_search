import json

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from instadjango import settings
from .forms import HashtagForm


def index(request):
    print("#### INDEX ####")
    insta_url = 'https://api.instagram.com/oauth/authorize/?client_id=' + settings.client_id + '&redirect_uri=' + \
                settings.redirect_url + '&response_type=code&scope=public_content'
    return render(request, 'instagram/index.html', {"insta_url": insta_url})


def login(request):
    print("######LOGIN######")
    code = request.GET.getlist('code')[0]
    if code is not False:
        payload = {'client_id': settings.client_id, 'client_secret': settings.client_secret,
                   'redirect_uri': settings.redirect_url, 'code': code, 'grant_type': 'authorization_code'}
        req = requests.post('https://api.instagram.com/oauth/access_token', data=payload)
        body_unicode = req.text
        data = json.loads(body_unicode)
        user = data['user']
        user_dict = {
            'access_token': data.get('access_token'),
            'insta_id': user.get('id', ''),
            'username': user.get('username', ''),
            'picture': user.get('profile_picture', ''),
            'website': user.get('website', ''),
            'bio': user.get('bio', ''),
            'full_name': user.get('full_name', '')}
        # if User.objects.filter(username=user_dict['username']).exists():
        #     u = User.objects.get(username=user_dict['username'])
        #     u.access_token = user_dict['access_token']
        #     u.save()
        # else:
        #     User.objects.create(**user_dict)
        request.session['access_token'] = user_dict['access_token']

        return HttpResponseRedirect('/instagram/search/')

    error = request.query_params.get('error', False)
    if error is not False:
        error_reason = request.query_params.get('error_reason', False)
        error_description = request.query_params.get('error_description', False)
        return HttpResponse(error + error_reason + error_description)
    return HttpResponse('oldu la')


def search(request):
    if request.method == 'GET':
        form = HashtagForm()
        return render(request, 'instagram/search.html', {'form': form})
    elif request.method == 'POST':
        access_token = request.session['access_token']
        form = HashtagForm(request.POST)
        if form.is_valid():
            hashtag = form.cleaned_data['search_box']
            hashtag_clean = hashtag.replace('#', '')
            return HttpResponseRedirect("/instagram/results?search=" + hashtag_clean)
        else:
            return form.errors


def results(request):
    hashtag = request.GET.getlist('search')[0]
    access_token = request.session['access_token']
    print(access_token)
    hashtag_url = 'https://api.instagram.com/v1/tags/'+hashtag
    params = {"access_token": access_token}
    req = requests.get(hashtag_url, params=params)


    return render(request, 'instagram/results.html', context=None)

# https://api.instagram.com/oauth/authorize/?client_id=CLIENT-ID&redirect_uri=REDIRECT-URI&response_type=code
# http://your-redirect-uri?code=CODE
# error:
# http://your-redirect-uri?error=access_denied&error_reason=user_denied&error_description=The+user+denied+your+request
# make request

# curl -F 'client_id=CLIENT_ID' \
#     -F 'client_secret=CLIENT_SECRET' \
#     -F 'grant_type=authorization_code' \
#     -F 'redirect_uri=AUTHORIZATION_REDIRECT_URI' \
#     -F 'code=CODE' \
#     https://api.instagram.com/oauth/access_token

# response
# {
#     "access_token": "fb2e77d.47a0479900504cb3ab4a1f626d174d2d",
#     "user": {
#         "id": "1574083",
#         "username": "snoopdogg",
#         "full_name": "Snoop Dogg",
#         "profile_picture": "..."
#     }
# }


#  example input

# '{"access_token":"1623444880.c59cb53.7139b07541a04cea8a9ef6319be724a2","user":{"username":"cagataybarin","bio":"Ko\\u00e7 University\\nMolocate","website":"http:\\/\\/molocateapp.com","profile_picture":"https:\\/\\/scontent.cdninstagram.com\\/t51.2885-19\\/891501_1590738227813177_1006586560_a.jpg","full_name":"Mehmet \\u00c7a\\u011fatay Bar\\u0131n","id":"1623444880"}}'
