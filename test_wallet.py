import iota_client
import json

# *** Replace with your testing seed (In case you decided to generate one, otherwise keep this one) ***
USER_SEED = 'a201599ad3bc079378e1e3cba43ee976828c146ec95f296c7d3a4ddc7dee24f37edba7b2bf8055503babd992964e0cb3649af6f184626636741cd9d6813b8c57'
SERVICE_SEED = 'a201599ad3bc079378e1e3cba43ee976828c146ec95f296c7d3a4ddc7dee24f37edba7b2bf8055503babd992964e0cb3649af6f184626636741cd9d6813b8c58'
SEED = USER_SEED
RECIPIENT_ADDRESS = 'atoi1qq4tuenpv2cxlcg7hd2lem6q7qzvt5wlapmtfj92nskpmuq9luqtqyguj6x'
INDEX = "ghost-iota-pay"
DATA = "ee398d5c2373add55c19cdbc4f70a0cce31bda4aed7ec224a55734384649f377".encode()
# Chrysalis testnet node
client = iota_client.Client()

def send():
    output = {
        'address': RECIPIENT_ADDRESS,
        'amount': 1000000  # 1 MIOTA
    }

    message_id = client.message(seed=SEED, index=INDEX, data=DATA, outputs=[output])
    #message_id = client.message(index=INDEX, data=DATA)
    print(f"IOTAs sent!\nhttps://explorer.iota.org/testnet/message/{message_id['message_id']}")

def get_address():    
    address = client.get_unspent_address(SEED)
    print(f"Generated address: {address[0]}")
    print("Copy your address. You'll need it in the next example.")
    print("Go to https://faucet.tanglekit.de/ and paste your address to receive devnet tokens. "
        "You'll need them in the following examples.")

def get_balance():
    seed_balance = client.get_balance(SEED)
    print(f"Total seed balance: {str(seed_balance)} IOTA")

def get_outputs_service():
    print(json.dumps(client.find_outputs(addresses=[RECIPIENT_ADDRESS]), indent = 3))

def get_message():
    message = client.get_message_data("4fb1e6e05e05aaadd389d811bf6064b2dcf0c4cfab5f4378da2c3aa26be2d40d")
    # print(json.dumps(message, indent = 3))
    message_index = message['payload']['transaction'][0]['essence']['payload']['indexation']
    #message_content = bytes(message['payload']['indexation'][0]['data']).decode()
    print(json.dumps(message, indent = 3))
    #print(bytes.fromhex(message_index[0]['index']).decode("utf-8"))
    print(bytes(message_index[0]['data']).decode())
    #print(message_content)


if __name__ == '__main__':
    send()