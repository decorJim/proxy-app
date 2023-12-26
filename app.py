import sys
from flask import Flask, jsonify
import pymysql
from sshtunnel import SSHTunnelForwarder
from flask import request
import random

# http://3.89.10.113/direct?query=SELECT%20COUNT(*)%20FROM%20film;

from pythonping import ping

app = Flask(__name__)

# change ips and push
master_ip="18.206.227.124" # sys.argv[1]
slaves_ip=[
    "3.88.28.138",
    "54.159.92.226",
    "44.204.37.168"
]  # sys.argv[2:5]

key='tmp1.pem'


@app.route('/direct')
def direct_hit():
    query = request.args.get('query')
    print("master_ip:",master_ip)
    print("query:",query)
    
    with SSHTunnelForwarder(master_ip, ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
        conn = pymysql.connect(host=master_ip, user='root',password='', db='sakila', port=3306, autocommit=True)
        cursor = conn.cursor()
        operation = query
        cursor.execute(operation)
        result=cursor.fetchall()
        print(result)
        conn.close()

    return jsonify({"result":result})

@app.route('/custom')
def custom_hit():
    query = request.args.get('query')
    print("slaves:",slaves_ip)
    print("query:",query)

    latency={}

    print("1")

    for slave in slaves_ip:
        response = ping(slave, timeout=1, count=4)
        latency[slave] = response.rtt_avg_ms


    print("2")

    sorted_dict=dict(sorted(latency.items(), key=lambda item: item[1]))
    print(sorted_dict.keys())
    shortestslave=list(sorted_dict.keys())[0]
    print("shortest:",shortestslave)
    
    with SSHTunnelForwarder((shortestslave,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
            conn = pymysql.connect(host=master_ip, user='root', db='sakila', port=3306, autocommit=True)
            cursor = conn.cursor()
            operation = query
            cursor.execute(operation)
            result = cursor.fetchall()
            print(result)
            conn.close()    

    return jsonify({"result":result})

@app.route('/random')
def random_hit():
    query = request.args.get('query')
    print("slaves:", slaves_ip)
    print("query:", query)

    random_ip = random.choice(slaves_ip)
    print(random_ip)
    
    with SSHTunnelForwarder((random_ip,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
            conn = pymysql.connect(host=master_ip, user='root', db='sakila', port=3306, autocommit=True)
            cursor = conn.cursor()
            operation = query
            cursor.execute(operation)
            result = cursor.fetchall()
            conn.close()
    
    return jsonify({"result": result})
   

        
@app.route('/health')
def health_check():
  # If everything is fine, return a 200 OK response when ping http://your-instance-ip:80/health
  return 'OK', 200

  # 0.0.0.0 allows incoming connections from any IP address
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)


# NEED KEY PAIR