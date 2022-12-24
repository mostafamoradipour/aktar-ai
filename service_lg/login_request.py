import requests


client = requests.session()

# Retrieve the CSRF token first
client.get("https://api.kachrobotics.com/api/user/set_csrf_cookie/")  # sets cookie
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']
else:
    # older versions
    csrftoken = client.cookies['csrf']

loginRes = client.post(url="https://api.kachrobotics.com/api/user/login/", headers= {"Referer": "https://api.kachrobotics.com"},
                        data= {"csrfmiddlewaretoken":csrftoken,  "email":"mostafa.moradipoor73@gmail.com", "password":"O64o4oo389"},)
print(loginRes.status_code)
print(loginRes.json())


# get( "https://api.kachrobotics.com/api/user/set_csrf_cookie/", { withCredentials: true } ) 
# ---> res
# post ("https://api.kachrobotics.com/api/user/login/",
#           data: { "csrfmiddlewaretoken" : res.data["csrfmiddlewaretoken"] ,  "email" : "esi3@gmail.com" ,  "password"  :  "Eb123456789" },
#           headers: { "Content-Type": "multipart/form-data" },
#           withCredentials: true )
# get( "https://api.kachrobotics.com/api/user/get_vspace_data/",
#           data: { "csrfmiddlewaretoken" : res.data["csrfmiddlewaretoken"] },
#           headers: { "Content-Type": "multipart/form-data" },
#           withCredentials: true  )
# ----> response

# const url = "wss://api.kachrobotics.com/ws/user/?uuid=" + response.data["uuid"];

# const socket = new WebSocket(url);
