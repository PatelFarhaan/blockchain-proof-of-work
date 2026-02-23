import hashlib
from wallet import Wallet
from flask_cors import CORS
from blockchain import Blockchain
from flask_mail import Mail, Message
from flask_mongoengine import MongoEngine
from flask_marshmallow  import Marshmallow
from flask import Flask, jsonify, request, send_from_directory


app = Flask(__name__)
CORS(app)
app.config['MONGODB_SETTINGS'] = {'host': "mongodb://localhost:27017/admin"}
db = MongoEngine(app)
ma = Marshmallow(app)

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = '***REMOVED***',
    MAIL_PASSWORD = '***REMOVED***',
    MAIL_DEBUG = True
)
mail=Mail(app)



@app.route('/', methods=['GET'])
def get_node_ui():
    print(request.remote_addr)
    return send_from_directory('ui', 'node.html')


@app.route('/all-transactions', methods=['GET'])
def get_transactions():
    bk_obj = BlockChain.objects.all()
    ma_schema = AllTransactions()
    resp = ma_schema.dump(bk_obj, many=True)
    return jsonify({"result": True, "data": resp})


@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed.'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading the keys failed.'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        response = {
            'message': 'Fetched balance successfully.',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'messsage': 'Loading balance failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'],
        values['sender'],
        values['signature'],
        values['amount'],
        is_receiving=True)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': values['sender'],
                'recipient': values['recipient'],
                'amount': values['amount'],
                'signature': values['signature']
            }
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {'message': 'No data found.'}
        return jsonify(response), 400
    if 'block' not in values:
        response = {'message': 'Some data is missing.'}
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {'message': 'Block added'}
            return jsonify(response), 201
        else:
            response = {'message': 'Block seems invalid.'}
            return jsonify(response), 409
    elif block['index'] > blockchain.chain[-1].index:
        response = {
            'message': 'Blockchain seems to differ from local blockchain.'}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            'message': 'Blockchain seems to be shorter, block not added'}
        return jsonify(response), 409


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(
        recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {'message': 'Resolve conflicts first, block not added!'}
        return jsonify(response), 409

    create_keys()
    block = blockchain.mine_block()

    if block is not None:
        dict_block = block.__dict__.copy()

        resp = request.get_json()
        cargo_id =  resp["id"]

        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }
        bk_obj = BlockChain.objects.filter(cargo_id=cargo_id).first()

        if bk_obj:
            # get the list and append response in this list
            blocks = list(bk_obj.blocks)
            last_ele = blocks[-1]
            weight = blocks[0]["data"]["weight"]
            signature = blocks[0]["transactions"][0]["signature"]
            transactions = last_ele["transactions"][0]

            data = {
                "position": resp["position"],
                "temperature": resp["temperature"],
                "weight": resp["weight"]
            }

            if weight != resp["weight"] or signature != transactions["signature"]:
                msg = Message("BLOCKCHAIN ALERT!!!", sender='***REMOVED***', recipients=['***REMOVED***'])
                msg.body = f"""
                Hi,
                
                This mail is just to inform you that your blockchain data has been tampered. 
                Your actual values of "weight": {weight} and "signature": {signature}.
                The passed values are of "weight": {resp["weight"]} and "signature": {transactions["signature"]}.
                
                
                Thank and Regards,
                Team Blockchain.

                """
                mail.send(msg)


            index = last_ele["index"]
            signature = transactions["signature"]
            response["block"]["data"] = data
            response["block"]["index"] = index+1
            del response["block"]["transactions"][0]["amount"]
            response["block"]["transactions"][0]["sender"] = cargo_id
            response["block"]["transactions"][0]["signature"] = signature

            blocks.append(response["block"])
            bk_obj.blocks = blocks
            bk_obj.save()
        else:
            # create a new record in the blockchain
            data = {
                "position": resp["position"],
                "temperature": resp["temperature"],
                "weight": resp["weight"]
            }
            response["block"]["data"] = data
            response["block"]["index"] = 0
            response["block"]["previous_hash"] = ""
            del response["block"]["transactions"][0]["amount"]
            response["block"]["transactions"][0]["sender"] = cargo_id
            response["block"]["transactions"][0]["signature"] = hashlib.sha3_256(cargo_id.encode('utf-8')).hexdigest()

            new_dict = {
                "email": resp["email"],
                "cargo_id": cargo_id,
                "blocks": [response["block"]]
            }
            new_bk_obj = BlockChain(**new_dict)
            new_bk_obj.save()

        return jsonify(response), 201

    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {'message': 'Chain was replaced!'}
    else:
        response = {'message': 'Local chain kept!'}
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [
            tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data attached.'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message': 'No node data found.'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message': 'Node added successfully.',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url is None:
        response = {
            'message': 'No node found.'
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        'message': 'Node removed',
        'all_nodes': blockchain.get_peer_nodes()
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        'all_nodes': nodes
    }
    return jsonify(response), 200


##################################
class BlockChain(db.Document):
    cargo_id = db.StringField()
    email = db.StringField()
    blocks = db.ListField()

class AllTransactions(ma.Schema):
    class Meta:
        fields = ("cargo_id", "blocks")
##################################


if __name__ == '__main__':
    port = 80
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port, use_reloader=True, debug=True)
