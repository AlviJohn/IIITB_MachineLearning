## Generated Story 105204274967524806
* greet
    - utter_greet
* restaurant_search{"location": "mumbai"}
    - slot{"location": "mumbai"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "chinese"}
    - slot{"cuisine": "chinese"}
    - utter_ask_budget
* restaurant_search{"budgetrange": "<", "budget": "600"}
    - slot{"budget": "600"}
    - slot{"budgetrange": "<"}
    - action_restaurant
    - slot{"location": "mumbai"}
    - utter_ask_sendemail
* sendmail{"email": "kffkkk2@hhjj.co.in"}
    - slot{"email": "kffkkk2@hhjj.co.in"}
    - action_sendmail
    - utter_goodbye
    - export

## Generated Story -1742078518368664153
* greet
    - utter_greet
* restaurant_search
    - utter_ask_location
* restaurant_search{"location": "kolkata"}
    - slot{"location": "kolkata"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "american"}
    - slot{"cuisine": "american"}
    - utter_ask_budget
* restaurant_search{"budgetrange": ">", "budget": "700"}
    - slot{"budget": "700"}
    - slot{"budgetrange": ">"}
    - action_restaurant
    - slot{"location": "kolkata"}
    - utter_ask_sendemail
* sendmail{"email": "abcd@bbc.com"}
    - slot{"email": "abcd@bbc.com"}
    - action_sendmail
    - utter_goodbye
    - export

## Generated Story 7632430231948276474
* greet
    - utter_greet
* restaurant_search
    - utter_ask_location
* restaurant_search{"location": "Bangalore"}
    - slot{"location": "Bangalore"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "south indian"}
    - slot{"cuisine": "south indian"}
    - utter_ask_budget
* restaurant_search{"budgetrange": "within", "budget": "700"}
    - slot{"budget": "700"}
    - slot{"budgetrange": "within"}
    - action_restaurant
    - slot{"location": "Bangalore"}
    - utter_ask_sendemail
* restaurant_search{"email": "abffr@ksjdsd.co.in"}
    - slot{"email": "abffr@ksjdsd.co.in"}
    - action_sendmail
    - utter_goodbye
    - export

## Generated Story 6782345534320292810
* greet
    - utter_greet
* restaurant_search{"location": "allahabad"}
    - slot{"location": "allahabad"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "north indian"}
    - slot{"cuisine": "north indian"}
    - utter_ask_budget
* restaurant_search{"budgetrange": ">", "budget": "500"}
    - slot{"budget": "500"}
    - slot{"budgetrange": ">"}
    - action_restaurant
    - slot{"location": "allahabad"}
    - utter_ask_sendemail
* sendmail{"email": "abcddd@sddf.com"}
    - slot{"email": "abcddd@sddf.com"}
    - action_sendmail
    - utter_goodbye
    - export

## Generated Story -7091697350016444208
* greet
    - utter_greet
* restaurant_search{"location": "kolkata"}
    - slot{"location": "kolkata"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "american"}
    - slot{"cuisine": "american"}
    - utter_ask_budget
* restaurant_search{"budgetrange": "<", "budget": "300"}
    - slot{"budget": "300"}
    - slot{"budgetrange": "<"}
    - action_restaurant
    - slot{"location": "kolkata"}
    - utter_ask_sendemail
* sendmail
    - utter_ask_sendemail
* sendmail{"email": "sabya_sama@kkkk.com"}
    - slot{"email": "sabya_sama@kkkk.com"}
    - utter_goodbye
    - export

