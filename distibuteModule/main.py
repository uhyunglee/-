import manager
import node
from flask import Flask, request, jsonify
import json


app = Flask(__name__)

m = manager.kubemanager()
m.spring_web_server()
m.distributed_server()

@app.route('/start')
def distribute_start():
    Avail_NodeList = m.Node_Information()
    print("main print")
    for n in Avail_NodeList:
        n.print_node()
    json_data = json.dumps([obj.__dict__ for obj in Avail_NodeList])
    print(json_data)
    return jsonify(json_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)