def greet(lang):
    if lang == "hindi":
        return "Namaste 😊 Glow Salon me welcome hai\nAap kya service lena chahenge?\nHaircut / Facial / Spa / Makeup"
    
    elif lang == "punjabi":
        return "Sat Sri Akal 😊 Glow Salon vich welcome\nTusi kehdi service chahunde ho?"
    
    elif lang == "chhattisgarhi":
        return "Johar 😊 Glow Salon ma swagat hai\nTola kaun service chahiye?"
    
    else:
        return "Hi 😊 Welcome to Glow Salon\nWhat service would you like?\nHaircut / Facial / Spa / Makeup"


def ask_name(lang):
    if lang == "hindi":
        return "Great choice 👍 Aapka naam bata dijiye"
    elif lang == "punjabi":
        return "Great 👍 Tuhada naam ki hai?"
    elif lang == "chhattisgarhi":
        return "Badiya 👍 Tor naam ka hai?"
    else:
        return "Great 👍 What's your name?"


def ask_time(lang):
    if lang == "hindi":
        return "Kab aana chahenge?\n11 AM / 1 PM / 4 PM"
    elif lang == "punjabi":
        return "Tusi kad auna chahoge?\n11 AM / 1 PM / 4 PM"
    elif lang == "chhattisgarhi":
        return "Kab aahibo?\n11 AM / 1 PM / 4 PM"
    else:
        return "When would you like to come?\n11 AM / 1 PM / 4 PM"


def confirm(name, service, time, lang):
    if lang == "hindi":
        return f"Done ✅\n\n{name}, aapka appointment confirm ho gaya hai\nService: {service}\nTime: {time}\n\nSee you soon 😊"
    
    elif lang == "punjabi":
        return f"Done ✅\n\n{name}, tuhadi booking confirm ho gayi\nService: {service}\nTime: {time}\n\nMilde haan 😊"
    
    elif lang == "chhattisgarhi":
        return f"Done ✅\n\n{name}, tor booking confirm ho gais\nService: {service}\nTime: {time}\n\nAabo jarur 😊"
    
    else:
        return f"Done ✅\n\n{name}, your appointment is confirmed\nService: {service}\nTime: {time}\n\nSee you soon 😊"