from flask import Flask, request
import json
from twilio.twiml.messaging_response import MessagingResponse
import json  
import os
from services import services
import responses
from language import detect_language
from openai import OpenAI
user_state = {}


app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def ask_ai(user_message):

    response = client.chat.completions.create(

        model="gpt-3.5-turbo",

        messages=[

            {
                "role": "system",
                "content": """

                You are a salon assistant.

                Understand user's language
                and reply in SAME language.

                Detect salon service.

                Available services:
                - haircut
                - hair spa
                - facial
                - makeup
                - waxing
                - manicure
                - pedicure

                Keep replies short, natural and human-like.

                Reply ONLY in this format:

                SERVICE: service_name
                REPLY: short reply
                """
            },

            {
                "role": "user",
                "content": user_message
            }

        ]
    )

    return response.choices[0].message.content

def save_booking(data):
    with open("data.json", "r+") as f:
        bookings = json.load(f)
        bookings.append(data)
        f.seek(0)
        json.dump(bookings, f, indent=2)


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body").lower()
    user = request.form.get("From")

    if user not in user_state:
        user_state[user] = {"step": "start"}

    state = user_state[user]
    resp = MessagingResponse()
    
    
    #welcome logo
    if state["step"] == "start":

      lang = detect_language(msg)
      state["lang"] = lang
      state["step"] = "service"

    # First send branding image
    image_msg = resp.message()
    image_msg.media("https://res.cloudinary.com/dd4bsgg46/image/upload/v1768571938/your-image-link")

    # Then send welcome message
    resp.message(
   """✨ *Glow Salon Assistant* ✨

   Hey beautiful 😊

   I’m here to help you with salon bookings and beauty services 💄

   You can chat with me naturally in different languages like:

   Hindi  
   English  
   Punjabi  
   Chhattisgarhi

   💬 For example:

    • “Haircut karwana hai”
    • “Spa chahiye”
    • “Facial booking”
    • “Makeup appointment”

    Don’t worry — I’ll understand you 😊

    ✨ Which service would you like today?
        """
    )

    return str(resp)
           
    #step 2 service             
           
    if state["step"] == "service":

     ai_reply = ask_ai(msg)

    lines = ai_reply.split("\n")

    service = lines[0].replace("SERVICE:", "").strip().lower()

    reply_text = lines[1].replace("REPLY:", "").strip()

    if service in services:

        state["service"] = services[service]["name"]
        state["step"] = "time"

        resp.message(

            f"{reply_text}\n\n"

            f"Available slots:\n"
            f"11 AM\n"
            f"1 PM\n"
            f"4 PM"
            )

        return str(resp)

    else:

        resp.message(
            "Sorry 😊 please tell me service again."
        )

        return str(resp)        
        
            

    # STEP 3: Time
    if state["step"] == "time":
        state["time"] = msg
        state["step"] = "name"
    resp.message(responses.ask_name(state["lang"]))
    return str(resp)

    # STEP 4: Name
    if state["step"] == "name":
        state["name"] = msg.title()
        state["step"] = "done"

        save_booking(state)

        resp.message(
            responses.confirm(
            state["name"],
            state["service"],
            state["time"],
            state["lang"]
                )    )
        return str(resp)

    resp.message("Type hi to restart 😊")
    return str(resp)

 
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)