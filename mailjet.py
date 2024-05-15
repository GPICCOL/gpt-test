# M&G2024!! for mailjet
# for email PierogiPizza#22
# EMAIL=mng.fusion.cuisine@gmail.com
# EMAIL_PWD=fbaobryekwevzbme

# import the mailjet wrapper
from mailjet_rest import Client
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Get your environment Mailjet keys
api_key = os.getenv('MJ_APIKEY_PUBLIC')
api_secret = os.getenv('MJ_APIKEY_PRIVATE')

print(api_key, api_secret)
sender_email = "mng.fusion.cuisine@gmail.com"
recipient_email = "berkeokur99@gmail.com"
fname = "Berke"
manager_name = "Manager"
day = "Giovedi"

intro = "<html><body><p>Caro " + fname \
  +",<p>Speriamo che tu possa dedicare qualche minuto del tuo prezioso tempo per aiutarci.  " \
  + manager_name + ", il nostro General Manager," \
  + " ci ha detto che " + day + " scorso hai avuto un ottima esperienza presso M&G Fusion Cuisine" \
  + ". </p><p> Ci farebbe immmenso piacerebbe se tu condividessi la tua esperienza.\
  Basandoci sulla tua conversazione con " + manager_name + " abbiamo redatto una possibile recensioni per te. \
  Saresti così gentile da copiarla e pubblicarla su \
  <a href='https://www.yelp.com/writeareview/biz/n-HwtvIHbogu2iCsOc5MQA?return_url=%2Fbiz%2Fn-HwtvIHbogu2iCsOc5MQA&review_origin=biz-details-war-button'>Yelp</a>, \
  <a href='https://www.tripadvisor.com/UserReviewEdit-g40024-d7359790-City_Pork_Jefferson-Baton_Rouge_Louisiana.html'>Tripadvisor</a>, \
  <a href='https://goo.gl/maps/rDbvTLUDbQe45Sdh6'>Google</a>, \
  o il tuo sito di recensioni online preferito? </p><p> Naturalmente puoi modificare la recensione come preferisci. \
  <i>Ti ringraziamo anticipatamente per il tuo prezioso aiuto, e speriamo di rivederti prestissimo!</i></p>"
closing = "<p>I tuoi amici di M&G Fusion Cuisine!</p></body></html>"
title = "<p><b>" + "This is the Title of the Review" + "</b></p>"
review = "<p>" + "This is the body text of the review from GPT" + "</p>"
content = title + review
body = intro + content + closing

mailjet = Client(auth=(api_key, api_secret), version='v3.1')
data = {
  'Messages': [
    {
      "From": {
        "Email": sender_email,
        "Name": "M&G Fusion Cuisine Restaturant"
      },
      "To": [
        {
          "Email": recipient_email,
          "Name": "You"
        }
      ],
      "Bcc": [
        {
          "Email": sender_email,
          "Name": "M&G Fusion Cuisine Restaturant"
        }
      ],
      "Subject": fname + ": Aiutaci a condividere la tua esperienza presso M&G Fusion Cuisine!",
      "TextPart": "In this prototype email only goes as HTML, if you have text email it won't work",
      "HTMLPart": body
    }
  ]
}
result = mailjet.send.create(data=data)
print(result.status_code)
print(result.json())


