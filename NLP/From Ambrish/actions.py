from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from flask_mail import Mail, Message

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
import zomatopy
import json
from flask import Flask

app = Flask(__name__)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'chatbot.rasa@gmail.com',
	MAIL_PASSWORD = 'Ch@tBot826'
	)
mail = Mail(app)
mailresponse = ''

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
	
	def checkcities(self,location):
		valid_cities = ["Ahmedabad", "Bangalore", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai", "Pune", "Agra", "Ajmer", "Aligarh", "Allahabad", "Amravati", "Amritsar", "Asansol", "Aurangabad", "Bareilly", "Belgaum", "Bhavnagar", "Bhiwandi", "Bhopal", "Bhubaneswar", "Bikaner", "Bokaro Steel City", "Chandigarh", "Coimbatore", "Cuttack", "Dehradun", "Dhanbad", "Durg-Bhilai Nagar", "Durgapur", "Erode", "Faridabad", "Firozabad", "Ghaziabad", "Gorakhpur", "Gulbarga", "Guntur", "Gurgaon", "Guwahati", "Gwalior","Hubli-Dharwad", "Indore", "Jabalpur", "Jaipur", "Jalandhar", "Jammu", "Jamnagar", "Jamshedpur", "Jhansi", "Jodhpur", "Kannur", "Kanpur", "Kakinada", "Kochi", "Kottayam", "Kolhapur", "Kollam", "Kota", "Kozhikode", "Kurnool", "Lucknow", "Ludhiana", "Madurai", "Malappuram", "Mathura", "Goa", "Mangalore", "Meerut", "Moradabad", "Mysore", "Nagpur", "Nanded", "Nashik", "Nellore", "Noida", "Palakkad", "Patna", "Pondicherry", "Raipur", "Rajkot", "Rajahmundry", "Ranchi", "Rourkela", "Salem", "Sangli", "Siliguri", "Solapur", "Srinagar", "Sultanpur", "Surat", "Thiruvananthapuram", "Thrissur", "Tiruchirappalli", "Tirunelveli", "Tiruppur", "Ujjain", "Vijayapura", "Vadodara", "Varanasi", "Vasai-Virar City", "Vijayawada", "Visakhapatnam", "Warangal"]
		if location.lower().title() in valid_cities:
			return "true"
		else:
			return "false"

	def getbudgetaction(self,budgetrange):
		if ( budgetrange == '>' or budgetrange == 'greater than' ):
			return '>'
		else:
			return '<'

	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"6c76f1274b3e711f16363e1234099b6c"}
		zomato = zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		validity = self.checkcities(loc)
		if validity == "false":
			dispatcher.utter_message("We do not operate in that area yet")
			return [SlotSet('location',loc)]
		cuisine = tracker.get_slot('cuisine')
		budget = tracker.get_slot('budget')
		budgetrange = tracker.get_slot('budgetrange')
		budgetaction = self.getbudgetaction(budgetrange)
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		sort = "rating"
		order = "desc"
		cuisines_dict={'mexican':73,'chinese':25,'american':1,'italian':55,'north indian':50,'south indian':85}
		results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), sort, order, 20)
		d = json.loads(results)
		response=""
		if d['results_found'] == 0:
			response= "no results"
		else:
			for restaurant in d['restaurants']:
				if budgetaction == '>':
					if  restaurant['restaurant']['average_cost_for_two'] >= float(budget):
						response=response+ " "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+" has been rated "+restaurant['restaurant']['user_rating']['aggregate_rating']+" and average cost for two is "+str(restaurant['restaurant']['average_cost_for_two'])+"\n"
				else:
					if  restaurant['restaurant']['average_cost_for_two'] <= float(budget):
						response=response+ " "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+" has been rated "+restaurant['restaurant']['user_rating']['aggregate_rating']+" and average cost for two is "+str(restaurant['restaurant']['average_cost_for_two'])+"\n"

		
		mailresponse =  response 
		dispatcher.utter_message("-----"+mailresponse)
		return [SlotSet('location',loc)]		
		
class ActionSendEmail(Action):
	def name(self):
		return 'action_sendmail'

	def run(self, dispatcher, tracker, domain):
		recipient_email = tracker.get_slot('email')
		if recipient_email is None:
			dispatcher.utter_message("Good bye")
		else:
			try:
				msg = Message("Resturants List",
				  sender="sabyasachi.samanta@gmail.com",
				  recipients=recipient_email)
				msg.body = mailresponse           
				mail.send(msg) ### once gmail is correctly setup message will be sent
				return 'Mail sent!'
			except:
				print ('Error occured while sending mail')
			finally:
				dispatcher.utter_message("Sent mail")
