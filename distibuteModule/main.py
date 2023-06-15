
import manager
import node
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

m = manager.kubemanager()
m.spring_web_server()
m.distributed_server()
m.node_flops_check()
@app.route('/start/<string:mode>')
def distribute_start(mode):
    new_directory = "/home/share/nfs/result"
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)

    Avail_NodeList = m.Node_Information(mode)
    print("main print")
    for n in Avail_NodeList:
        n.print_node()
    json_data = json.dumps([obj.__dict__ for obj in Avail_NodeList])
    print(json_data)
    return jsonify(json_data)

@app.route('/distribution/download')
def happy():
    print('happy')
    return 'Ok'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
