def detect_language(msg):
    msg = msg.lower()

    if any(w in msg for w in ["hai", "karna", "chahiye"]):
        return "hindi"
    elif any(w in msg for w in ["aa", "chahunde"]):
        return "punjabi"
    elif any(w in msg for w in ["la", "kaun", "tor"]):
        return "chhattisgarhi"
    else:
        return "english"