from kol.Session import Session
from kol.request.UseSkillRequest import UseSkillRequest
from kol.request.GetMessagesRequest import GetMessagesRequest
from kol.request.DeleteMessagesRequest import DeleteMessagesRequest
from kol.request.SendMessageRequest import SendMessageRequest
from kol.request.CharpaneRequest import CharpaneRequest
from kol.request.StoreRequest import StoreRequest
from kol.request.UseItemRequest import UseItemRequest
from kol.database.SkillDatabase import getSkillFromId
import logging
import math
import webapp2
import urllib2
import time
import cookielib
from google.appengine.api import memcache
from data import Data


def doStuff():
	logging.debug("doStuff()")
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
		logging.error("some memcache keys were deleted")

	m = None
	messages = None

	try:
		m = GetMessagesRequest(s)
		messages = m.doRequest()
	except:
		logging.warn("Not logged in, logging in")
		memcache.flush_all()
		s = Session()
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

		m = GetMessagesRequest(s)
		messages = m.doRequest()

	for kmail in messages["kmails"]:
		logging.info("%s sent kmail with text %s" % (kmail["userName"], kmail["text"]))

		msg = kmail["text"].split("\n")
		totalMP = 0
		totalCost = 0
		buffsCast = []

		for randomBuff in msg:
			specialCase = False
			specialUID = None
			info = randomBuff.split(" ")
			buff = ""
			duration = 0

			if not info[0].isdigit():
				if info[0] == Data.secretKey:
					specialCase = True
					specialUID = int(info[1])
				else:
					logging.info("No duration set")
					buff = " ".join(info)
					logging.info("Need to interpret %s" % buff)
					duration = 50
			else:
				logging.info("Duration set for %d" % int(info[0]))
				buff = " ".join(info)[len(info[0]) + 1:]
				logging.info("Need to interpret %s" % buff)

				duration = int(info[0]) if int(info[0]) < Data.MAXLENGTH else Data.MAXLENGTH

			if specialCase:
				if len(info) >= 3:
					if not info[2].isdigit():
						logging.info("No duration set")
						buff = " ".join(info)[len(info[0]) + len(info[1]) + 2:]
						logging.info("Need to interpret %s" % buff)
						duration = 50
					else:
						logging.info("Duration set for %d" % int(info[2]))
						buff = " ".join(info)[len(info[0]) + len(info[1]) + len(info[2]) + 3:]
						logging.info("Need to interpret %s" % buff)

						duration = int(info[2]) if int(info[2]) < Data.MAXLENGTH else Data.MAXLENGTH

			theBuff = None
			for key in Data.buffs.keys():
				if buff.lower() in key.lower():
					theBuff = Data.buffs[key]
					logging.info("keyword '{0}' matched for {1}".format(buff, key))

			if theBuff is not None and buff != "":
				shouldBuff = True
				c = CharpaneRequest(s)
				charData = c.doRequest()

				currentMP = charData["currentMP"]
				timesNeeded = int(math.ceil(float(duration)/float(Data.ACCORDION_DURATION)))

				logging.info("Current: MP: {0}, meat: {1}".format(currentMP, charData["meat"]))
				logging.info("Current MP: {0}, Need: {1}".format(currentMP, (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded))

				if "once" not in theBuff:
					while currentMP < (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded < charData["maxMP"]:
						if currentMP > (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded:
							logging.error("Should not be here!")
							break
						if charData["meat"] > 94:
							logging.warn("Out of MP. Buying mystery juice")
							store = StoreRequest(s, 2, 518)
							try:
								store.doRequest()
							except:
								logging.error("dc'ed from server")
								s = Session()
								memcache.flush_all()
								s.login(Data.USERNAME, Data.PASSWORD)
								store.doRequest()
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

							u = UseItemRequest(s, 518)
							u.doRequest()
							totalCost += 95
							currentMP = c.doRequest()["currentMP"]
						else:
							logging.error("No meat or MP, stopping")
							shouldBuff = False
							break
				else:
					while currentMP < (theBuff["mp"] - Data.MPCOSTREDUCTION) < charData["maxMP"]:
						if currentMP > (theBuff["mp"] - Data.MPCOSTREDUCTION):
							logging.error("Should not be here!")
							break
						if charData["meat"] > 94:
							logging.warn("Out of MP. Buying mystery juice")
							store = StoreRequest(s, 2, 518)
							try:
								store.doRequest()
							except:
								logging.error("dc'ed from server")
								s = Session()
								memcache.flush_all()
								s.login(Data.USERNAME, Data.PASSWORD)
								store.doRequest()
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

							u = UseItemRequest(s, 518)
							u.doRequest()
							totalCost += 95
							currentMP = c.doRequest()["currentMP"]
						else:
							logging.error("No meat or MP, stopping")
							shouldBuff = False
							break

				if shouldBuff and theBuff["available"] and (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded < charData["maxMP"]:
					if not specialCase:
						skill = UseSkillRequest(s, theBuff["id"], 1, kmail["userId"]) if "once" in theBuff else UseSkillRequest(s, theBuff["id"], timesNeeded, kmail["userId"])

						logging.info("Buffing %s with %s" % (kmail["userName"], getSkillFromId(theBuff["id"])["name"]))

						try:
							skill.doRequest()
							totalMP += (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded
							buffsCast.append(theBuff["id"])
						except:
							logging.fatal("Casting error for KMail request.")
					else:
						skill = UseSkillRequest(s, theBuff["id"], 1, specialUID) if "once" in theBuff else UseSkillRequest(s, theBuff["id"], timesNeeded, specialUID)

						logging.info("Buffing %s with %s" % (specialUID, getSkillFromId(theBuff["id"])["name"]))

						try:
							skill.doRequest()
							totalMP += (theBuff["mp"] - Data.MPCOSTREDUCTION) * timesNeeded
							buffsCast.append(theBuff["id"])
						except:
							logging.fatal("Casting error for web interface request.")
			else:
				logging.warn("No buff found matching %s" % buff)

		msg = None
		if not specialCase:
			msg = {
				"userId": kmail["userId"],
				"text": "Thanks for using BuffBot!\nTotal MP used: {0}\nTotal meat spent on magical mystery juice: {1}".format(totalMP, totalCost)
			}
		else:
			msg = {
				"userId": specialUID,
				"text": "Thanks for using BuffBot!\nTotal MP used: {0}\nTotal meat spent on magical mystery juice: {1}".format(totalMP, totalCost)
			}

		for someBuff in buffsCast:
			msg["text"] += "\nGave buff: %s" % getSkillFromId(someBuff)["name"]

		if len(buffsCast) > 0:
			send = SendMessageRequest(s, msg)
			send.doRequest()
			logging.info("KMail sent")
		else:
			if not specialCase:
				msg = {
					"userId": kmail["userId"],
					"text": "Thanks for using BuffBot!\nEither one of two things happened:\n1. BuffBot ran out of meat and MP, so it couldn't complete your request. Please send some meat next time for some magical mystery juice if this is the case.\n2. BuffBot did not know how to interpret your input. If this is the case, please refer to http://rubuffbot.appspot.com/faq/ for information on how to use BuffBot."
				}
			else:
				msg = {
					"userId": specialUID,
					"text": "Thanks for using BuffBot!\nEither one of two things happened:\n1. BuffBot ran out of meat and MP, so it couldn't complete your request. Please send some meat next time for some magical mystery juice if this is the case.\n2. BuffBot did not know how to interpret your input. If this is the case, please refer to http://rubuffbot.appspot.com/faq/ for information on how to use BuffBot."
				}
			send = SendMessageRequest(s, msg)
			send.doRequest()

		d = DeleteMessagesRequest(s, [kmail["id"]])
		d.doRequest()
		logging.info("KMail deleted")

		c = CharpaneRequest(s)
		charData = c.doRequest()
		logging.info("Final MP and Meat: {0}, {1}".format(charData["currentMP"], charData["meat"]))

class Buff(webapp2.RequestHandler):
	def get(self):
		doStuff()
		time.sleep(15)
		doStuff()
		time.sleep(15)
		doStuff()
		time.sleep(15)
		doStuff()
app = webapp2.WSGIApplication([("/buff/", Buff)])
