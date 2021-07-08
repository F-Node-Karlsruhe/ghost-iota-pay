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
    address = client.get_addresses(SEED, input_range_begin=0,input_range_end=10, get_all=True)
    print(f"Generated address: {address}")
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

def create_dust_allowed_address(seed=SERVICE_SEED, account_index:int = 0, dust_address:str = RECIPIENT_ADDRESS, number_of_dust_transactions:int = 10)-> str:
    if number_of_dust_transactions < 10:
        print("Value of possible dust transactions as %d to create a dust enabled account is too low " % number_of_dust_transactions)
        return ""
    if number_of_dust_transactions > 100:
        print("Value of possible dust transactions as %d to create a dust enabled account is too high " % number_of_dust_transactions)
        return ""
    value = 100_000 * number_of_dust_transactions
    message = client.message(
        seed=seed,
        dust_allowance_outputs=[
            {
                'address': dust_address,
                'amount': value,
            }
        ]
    )
    print("Dust is now allowed for %s" % dust_address, end='', flush=True)
    client.retry_until_included(message_id = message['message_id'])
    print(" - now confirmed")
    return message['message_id']

def is_dust_enabled( address:str = RECIPIENT_ADDRESS) -> bool:
    address_balance_pair = client.get_address_balances([address])[0]
    if address_balance_pair['dust_allowed']:
        return True
    return False


if __name__ == '__main__':
    get_address()