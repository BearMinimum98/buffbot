from data import *
from kol.Session import Session
from kol.request.SendMessageRequest import SendMessageRequest
from kol.request.SearchPlayerRequest import SearchPlayerRequest
from google.appengine.api import memcache
import urllib2
import cookielib
import webapp2
import logging


class WebBuff(webapp2.RequestHandler):
	def get(self):
		WebBuff.post(self)

	def post(self):
		s = Session()
		try:
			c1 = cookielib.Cookie(None, "PHPSESSID", memcache.get("PHPSESSID"), None, False, memcache.get("domain0"), True, False, memcache.get("path0"), True, False, None, False, None, False, None, False)
			jar = cookielib.CookieJar()
			jar.set_cookie(c1)
			c2 = cookielib.Cookie(None, "appserver", memcache.get("appserver"), None, False, memcache.get("domain1"), True, False, memcache.get("path1"), True, False, None, False, None, False, None, False)
			jar.set_cookie(c2)
			s.cj = jar

			s.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(s.cj))
			s.isConnected = memcache.get("isConnected")
			s.userId = memcache.get("userId")
			s.userName = memcache.get("userName")
			s.userPasswordHash = memcache.get("userPasswordHash")
			s.serverURL = memcache.get("serverURL")
			s.pwd = memcache.get("pwd")
			s.rollover = memcache.get("rollover")
		except:
			logging.error("some memcache keys were deleted, logging in manually and setting memcache keys")
			s.login(Data.USERNAME, Data.PASSWORD)

			memcache.add(key="isConnected", value=bool(s.isConnected))
			memcache.add(key="userId", value=int(s.userId))
			memcache.add(key="userName", value=str(s.userName))
			memcache.add(key="userPasswordHash", value=str(s.userPasswordHash))
			memcache.add(key="serverURL", value=str(s.serverURL))
			memcache.add(key="pwd", value=str(s.pwd))
			memcache.add(key="rollover", value=int(s.rollover))

			i = 0
			for cookie in s.cj:
				logging.info("%s=%s" % (cookie.name, cookie.value))
				memcache.add(key=cookie.name,value=str(cookie.value))
				memcache.add(key="domain%d" % i, value=str(cookie.domain))
				memcache.add(key="path%d" % i, value=str(cookie.path))
				i += 1

		# START DOING CRAP
		username = self.request.get("username")
		search = SearchPlayerRequest(s, username)
		uid = None
		try:
			uid = search.doRequest()['players'][0]["userId"]
		except:
			logging.error("dc'ed from server")
			s.login(Data.USERNAME, Data.PASSWORD)

			memcache.add(key="isConnected", value=bool(s.isConnected))
			memcache.add(key="userId", value=int(s.userId))
			memcache.add(key="userName", value=str(s.userName))
			memcache.add(key="userPasswordHash", value=str(s.userPasswordHash))
			memcache.add(key="serverURL", value=str(s.serverURL))
			memcache.add(key="pwd", value=str(s.pwd))
			memcache.add(key="rollover", value=int(s.rollover))

			i = 0
			for cookie in s.cj:
				logging.info("%s=%s" % (cookie.name, cookie.value))
				memcache.add(key=cookie.name,value=str(cookie.value))
				memcache.add(key="domain%d" % i, value=str(cookie.domain))
				memcache.add(key="path%d" % i, value=str(cookie.path))
				i += 1

			uid = search.doRequest()['players'][0]["userId"]

		logging.info("Player: {0}, Buffs: {1}".format(username, self.request.get("buffs")))
		splitBuffs = self.request.get("buffs").split("\n")

		msg = {
			"userId": s.userId,
			"text": ""
		}
		for buff in splitBuffs:
			msg["text"] += "%s %s %s\n" % (Data.secretKey, uid, buff)

		send = SendMessageRequest(s, msg)
		send.doRequest()

		self.response.out.write("Buff request received. Your buffs will arrive shortly. Redirecting to web buff page in 5 seconds.")
		self.response.out.write('''<script type="text/javascript">setTimeout("window.location='/web/'", 5000)</script>''')

app = webapp2.WSGIApplication([("/web/buff/", WebBuff)])