from flask import Flask, request
import json
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json  
import os
from services import services
from openai import OpenAI
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from supabase import create_client

user_state = {}
booking = []


app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


services= {
    "haircut":300,
    "facial":800,
    "hair spa":1200,
    "cleanup":600,
    "waxing":700,
    "makeup":2500

}

slots = ["03:44 PM" ,"03:45 PM", "03:46 PM"]


responses = {

    "english": {

        "slot":
        "✨ {service} price is ₹{price}\nAvailable slots:\n03:44 PM\n03:45 PM\n03:46 PM 😊",

        "name":
        "😊 May I know your name for booking?",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name}, your {service} appointment is booked for {slot}.\nPrice: ₹{price} 😊",
        
        "reminder": 
        "⏰ Hi {name}, your {service} appointment is in 1 hour at {slot}. See you soon 😊"
        
          
    },

    "hindi": {

        "slot": 
        "✨ {service} ki price ₹{price} hai\nAvailable slots:\n03:44 PM\n03:45 PM\n03:46 PM 😊",

        "name":
        "😊 Booking ke liye aapka naam bata dijiye.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name} ji, aapka {service} appointment {slot} ke liye book ho gaya hai.\nPrice: ₹{price} 😊",
        
        "reminder": 
        "⏰ {name} ji, aapki {service} appointment 1 ghante baad {slot} par hai 😊"
    },

    "punjabi": {
        
        "slot": 
        "✨ {service} da price ₹{price} aa\nAvailable slots:\n03:44 PM\n03:45 PM\n03:46 PM 😊",
    
        "name":
        "😊 Booking layi apna naam dass deo.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name} ji, tuhadi {service} appointment {slot} layi book ho gayi aa.\nPrice: ₹{price} 😊",
        
        "reminder": 
        "⏰ {name} ji, tuhadi {service} appointment 1 ghante baad {slot} te hai 😊"
    },

    "marathi": {
        
         "slot":
            "✨ {service} chi price ₹{price} aahe\nAvailable slots:\n03:44 PM\n03:45 PM\n03:46 PM 😊",
         
        "name":
        "😊 Booking sathi tumcha nav सांगा.",

        "confirm":
        "✨ Booking Confirmed 🎉\n{name}, tumchi {service} appointment {slot} la confirm zali aahe.\nPrice: ₹{price} 😊",
        
        "reminder": 
        "⏰ {name}, tumchi {service} appointment 1 tasane {slot} la aahe 😊"
        
        
    }

}


def detect_user(user_message):

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                 "content": """
                   You are ONLY a language analyzer.

                   Detect:

                   1. language
                   2. tone
                   3. intent

                   Possible languages:
                   english
                   hindi
                   punjabi
                   marathi

                   Possible intents:
                   booking
                   consultation
                   chat
            
                  
                  Roman Punjabi examples:
                  tusi, menu, dasso, karona -> punjabi

                  Roman Hindi examples:
                  mujhe, batao, kya, karna -> hindi

                  Roman Marathi examples:
                  tumcha, pahije -> marathi

                   Roman Chhattisgarhi examples:
                   mor, tor -> chhattisgarhi

                   English salon words like:
                   haircut, spa, facial, booking
                  
                  IMPORTANT RULE:

                  Detect ONLY language.

                   Ignore service words:
                   
                   haircut
                   spa
                   facial
                   booking
                   cleanup
                   waxing
                   makeup

                   User language examples:

                   "menu haircut karona sii tusi kuch daso"
                    -> punjabi

                    "mujhe haircut karwana hai"
                    -> hindi

                    "I want haircut booking"
                    -> english


                    DO NOT use these English salon words to detect language.

                     Detect user's dominant language from Roman text.
                  
                    Return ONLY JSON.
                  
                  
                  Example:
                  {
                    "language":"punjabi",
                     "tone":"casual",
                     "intent":"consultation",
                     
                    }
                    
                    {
                        "language":"punjabi",
                        "tone":"casual",
                        "intent":"booking",
                        
                    }
                    
                    {
                        "language":"punjabi",
                        "tone":"casual",
                        "intent":"chat",
                        
                    }
                    """                
            },

            {
                "role": "user",
                "content": user_message
            }

        ]
    )

    return response.choices[0].message.content

#def send_reminders():
    
   # now = datetime.now().strftime("%I:%M %p")
    
   # with open("data.json", "r+") as f:
        #bookings = json.load(f)

   # for booking in bookings:

      #  slot = booking["slot"]
        #if slot == now:

           # lang = booking["language"]

            #reply = responses[lang]["reminder"].format(
                #3name=booking["name"],
               # service=booking["service"],
                #slot=booking["slot"]
          #  )

           # twilio_client.messages.create(
               # from_='whatsapp:+14155238886',
               # body=reply,
                #to=f'whatsapp:{booking["phone"]}'
           # )

#scheduler = BackgroundScheduler()
#scheduler.add_job(send_reminders, 'interval', minutes=1)
#scheduler.start()



def save_booking(data):
    supabase.table("booking").insert(data).execute( )
                              
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body").lower()
    user = request.form.get("From")
    
    if user not in user_state:
        user_state[user] = {
            "welcome": False,
            "step":"start",
            "service": "",
            "slot": "",
            "name": "",
            "language": "",
            "tone":"casual",
            "intent":"booking"
            
        }

    state = user_state[user]
    
    detected = detect_user(msg)
    
    data = json.loads(detected)
    
    detected_language = data["language"].strip().lower()
    
    ignore_values = [
        "03:44", "03:45", "03:46", "03:44 PM", "03:45 PM", "03:46 PM" 
     ]
    #SLOT AND NAME PE NO LANGUAGE CHANGE
    if (
        msg.upper() not in ignore_values and state["step"] != "name"
        and detected_language in responses
    ):
    
        state["language"] = detected_language
             
    state["tone"] = data["tone"]
    state["intent"] = data["intent"]
      
    
    language = state["language"]
    tone = state["tone"]
    intent = state["intent"]
    
       
    resp = MessagingResponse()
    
    
    #welcome logo
    
    if not state["welcome"]:

        state["welcome"] = True


        #  welcome message and branding logo
        welcome_msg = resp.message("""
             
       ✨ Welcome to Glow Salon ✨

     Every appointment starts with a choice...

     ✨ Fresh Look
     ✨ Self-Care
     ✨ Special Occasion

     🌐 Hindi • English • Punjabi • 
      Marathi • Chhattisgarhi

     what would you like to book today?
       """)
        
        welcome_msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/Untitled_design_2_t1kqlx.png")
        
        return str(resp)
    
      #consultation reply
    booking_words =[
        "haircut",
        "facial",
        "cleanup",
        "waxing",
        "makeup",
        "spa"
    ]
    is_booking =( 
    any(word in msg for word in booking_words) or msg in services)
    
    if (
        intent == "consultation"
        and not is_booking
        and state["step"] == "start"
    ):   
        resp.message(reply)
        return str(resp) 
          
    # detect service
    for service in services:

      if service in msg:

        state["service"] = service
        state["step"] = "slot"

        price = services[service]

        lang = state["language"]
        
        print("LANGUAGE =", lang)
        reply = responses[lang]["slot"].format(service=service,price=price)
        
        resp.message(reply)
        return str(resp)


      # slot selection
    if state["step"] == "slot":
        
        msg = msg.strip().upper()
        
        valid_slots =["03:44","03:45","03:46 PM","03:46","03:45 PM","03:44 PM"]
        
        if msg not in valid_slots:
            resp.message("Please select available slot 😊")
            return str(resp)

        state["slot"] = msg
        state["step"] = "name"
        
        lang = state["language"]
       
        reply = responses[lang]["name"]
       
        resp.message(reply)

        return str(resp)

      # final confirmation
    if state["step"] == "name":

       state["name"] = msg
       state["step"] = "done"

       service = state["service"]
       price = services[service]
       slot = state["slot"]
       name = state["name"]
       
       lang = state["language"]
       reply = responses[lang]["confirm"].format(
           name=name,
           service=service,
           price=price,
           slot=slot
       )  
       
       # booking save
       save_booking({
           
           "phone" : user,
           "name" : name,
           "service" : service,
           "slot" : slot,
           "language" : lang,
           "price" : price,
           "status" : "confirmed"
           
       })
     
       resp.message(reply)

       
       state["language"] = ""
       state["step"] = "start"
       state["service"] = ""
       state["slot"] = ""
       state["name"] = ""

       return str(resp)
 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)