import pprint, json
import zomatopy
import smtplib

class SearchRestaurants:
    
    def get_top_five(location,cuisine,budget):
        
        # provide API key and initialise a 'zomato app' object
        config={ "user_key": '6ce88a5ec1419e335afa1c7f92f4b739'}
        zomato = zomatopy.initialize_app(config)
        
        # get_location gets the lat-long coordinates of 'loc'
        location_detail=zomato.get_location(location, 1)
        # store retrieved data as a dict
        d1 = json.loads(location_detail)
        # separate lat-long coordinates
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        city_ID=zomato.get_city_ID(location)
        cuisines = zomato.get_cuisines(city_ID)
        cuisine_ID = list(cuisines.keys())[list(cuisines.values()).index('Italian')]
        response=zomato.restaurant_search("", lat, lon, str(cuisine_ID), 100)
        r = json.loads(response)
        count=0
        result1 = ""
        for i in r['restaurants'] :
            name = i['restaurant']['name']
            address = i['restaurant']['location']['address']
            rating = i['restaurant']['user_rating']['aggregate_rating']
            costForTwo = i['restaurant']['average_cost_for_two']
            if budget==1 and costForTwo<300 and count<5 :
                print('# less than 300')
                #{restaurant_name} in {restaurant_address} has been rated {rating}.
                count=count+1
                result1 = result1+str(count)+'. '+name+' in '+address+' has been rated '+rating+'.\n\n'
            elif budget==2 and costForTwo>=300 and costForTwo<=700 and count<5 :
                print('#300 to 700')
                count=count+1
                result1 = result1+str(count)+'. '+name+' in '+address+' has been rated '+rating+'.\n\n'
            elif budget==3 and costForTwo>700 and count<5:
                print('# more than 700')
                count=count+1
                result1 = result1+str(count)+'. '+name+' in '+address+' has been rated '+rating+'.\n\n'
        return result1
        
    def email_top_ten(location,cuisine,budget,emailid):
        # provide API key and initialise a 'zomato app' object
        config={ "user_key": '6ce88a5ec1419e335afa1c7f92f4b739'}
        zomato = zomatopy.initialize_app(config)
        # get_location gets the lat-long coordinates of 'loc'
        location_detail=zomato.get_location(location, 1)
        # store retrieved data as a dict
        d1 = json.loads(location_detail)
        # separate lat-long coordinates
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        city_ID=zomato.get_city_ID(location)
        cuisines = zomato.get_cuisines(city_ID)
        cuisine_ID = list(cuisines.keys())[list(cuisines.values()).index('Italian')]
        response=zomato.restaurant_search("", lat, lon, str(cuisine_ID), 100)
        r = json.loads(response)
        count=0
        result1 = ""
        for i in r['restaurants'] :
            name = i['restaurant']['name']
            address = i['restaurant']['location']['address']
            rating = i['restaurant']['user_rating']['aggregate_rating']
            costForTwo = i['restaurant']['average_cost_for_two']
            if budget==1 and costForTwo<300 and count<10 :
                print('# less than 300')
                #{restaurant_name} in {restaurant_address} has been rated {rating}.
                count=count+1
                result1 = result1+str(count)+'. Name : '+name+'\n Address : '+address+'\n Average budget for two people : '+str(costForTwo)+'\n Zomato user rating : '+rating+'.\n\n'
            elif budget==2 and costForTwo>=300 and costForTwo<=700 and count<10 :
                print('#300 to 700')
                count=count+1
                result1 = result1+str(count)+'. Name : '+name+'\n Address : '+address+'\n Average budget for two people : '+str(costForTwo)+'\n Zomato user rating : '+rating+'.\n\n'
            elif budget==3 and costForTwo>700 and count<10:
                print('# more than 700')
                count=count+1
                result1 = result1+str(count)+'. Name : '+name+'\n Address : '+address+'\n Average budget for two people : '+str(costForTwo)+'\n Zomato user rating : '+rating+'.\n\n'
       
        recipient = emailid
        subject = "Top 10 "+cuisine+ " restaurants in "+location
        body = result1
        user = "chatbot.rasa@gmail.com"
        FROM = user
        TO = recipient if isinstance(recipient, list) else [recipient]
        SUBJECT = subject
        TEXT = body
        
        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(user, 'Ch@tBot826')
            server.sendmail(FROM, TO, message)
            server.close()
            print('successfully sent the mail')
        except:
            print("failed to send mail")

