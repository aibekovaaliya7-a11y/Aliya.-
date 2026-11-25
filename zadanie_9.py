zaprosi = ["10.0.0.1", "10.0.0.2", "10.0.0.2", "10.0.0.2"]
limit = 3
schetchik = {}

for ip in zaprosi:
    schetchik[ip] = schetchik.get(ip, 0) + 1
    if schetchik[ip] >= limit:
        print("Ataka s IP:", ip)