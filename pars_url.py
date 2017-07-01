import sys
sys.path.append('/usr/lib/python2.7/dist-packages')

import requests
import re
a = 'https://stepic.org/media/attachments/lesson/24472/sample0.html'
b = 'http://meteo.paraplan.net/forecast/summary.html?place=3148'

res = requests.get(b)
#patt = r'href=\"(.+?)"'
patt = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

url_in_c= re.findall(patt, res.text)
for i in url_in_c:
	print(i)
#Изменения