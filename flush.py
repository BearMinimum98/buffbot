from google.appengine.api import memcache
import webapp2


class FlushMemcache(webapp2.RequestHandler):
	def get(self):
		memcache.flush_all()
		pass
	pass
app = webapp2.WSGIApplication([("/flush/", FlushMemcache)])