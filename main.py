from socketIO_client import SocketIO
import random
import threading
import time
import requests

def port_check():
    while True:
        try:
            response = requests.get(api_address)
            if response.status_code == 200:
                print(f"Port is open. Status Code: {response.status_code}")
            else:
                print(f"Received unexpected status code {response.status_code}")
        except Exception as e:
            print("Port is not open yet. Retrying in 5 seconds...")
        time.sleep(5)


def send_periodic_quotes(rfq_id):
    while rfq_id in active_rfqs:
        quote_data = {
            "qty_at_price": random.randint(10, 100),
            "full_qty_spread": random.uniform(0.1, 0.5),
            "interestRates": random.uniform(0.05, 0.2)
        }
        print(f"Sending quote for RFQ {rfq_id}")
        socket.emit("send_quote", {"rfq_id": rfq_id, "quote_data": quote_data})
        time.sleep(2)


def handle_new_rfq(*args):
    rfq = args[0]
    print(f"Received RFQ: {rfq}")

    rfq_id = rfq.get("rfq_id", "unknown_id")
    active_rfqs.add(rfq_id)

    t = threading.Thread(target=send_periodic_quotes, args=(rfq_id,))
    t.start()


def handle_rfq_expiry(*args):
    rfq_id = args[0]
    if rfq_id in active_rfqs:
        print(f"RFQ {rfq_id} has expired. Removing...")
        active_rfqs.remove(rfq_id)


# Replace this with your Flask API address
api_address = "https://hotei.replit.app"

try:
    # Start port checking thread
    port_check_thread = threading.Thread(target=port_check)
    port_check_thread.start()

    socket = SocketIO(api_address)
    print(f"Connected to {api_address}. Waiting for RFQs...")

    # Listen for 'new_rfq' and 'rfq_expired' events
    socket.on("new_rfq", handle_new_rfq)
    socket.on("rfq_expired", handle_rfq_expiry)

    active_rfqs = set()

    socket.wait()

except Exception as e:
    print(f"An error occurred: {e}")
