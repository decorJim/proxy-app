import sys
from flask import Flask
import pymysql
from sshtunnel import SSHTunnelForwarder
from flask import request

from pythonping import ping

app = Flask(__name__)

# change ips and push
master_ip="172.31.21.78" # sys.argv[1]
slaves_ip=[
    "172.31.31.114",
    "172.31.24.46",
    "172.31.27.249"
]  # sys.argv[2:5]
username='ubuntu'

key='myp.pem'


@app.route('/direct')
def direct_hit():
    query = request.args.get('query')
    print("master_ip:",master_ip)
    print("query:",query)
    
    # change ssh_key import
    with SSHTunnelForwarder(master_ip, username, ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
        conn = pymysql.connect(host=master_ip, user='root', password='root', db='sakila', port=3306, autocommit=True)
        cursor = conn.cursor()
        operation = query
        cursor.execute(operation)
        print(cursor.fetchall())

    return cursor.fetchall(),200

@app.route('/custom')
def direct_hit():
    query = request.args.get('query')
    print("slaves:",slaves_ip)
    print("query:",query)

    latency={}

    for slave in slaves_ip:
        time=ping(slave,timeout=1)
        latency[slave]=time.rtt_avg_ms

    sorted=dict(sorted(latency.items(), key=lambda item: item[1]))
    shortestslave=sorted[0]

    print(shortestslave)
    
    # change ssh_key import
    with SSHTunnelForwarder(shortestslave, username, ssh_pkey=key, remote_bind_address=(shortestslave, 3306)) as tunnel:
        conn = pymysql.connect(host=shortestslave, user='root', password='root', db='sakila', port=3306, autocommit=True)
        cursor = conn.cursor()
        operation = query
        cursor.execute(operation)
        print(cursor.fetchall())

    return cursor.fetchall(),200

@app.route('/random')
def direct_hit():
    query = request.args.get('query')
    print("slaves:",slaves_ip)
    print("query:",query)
    
    # change ssh_key import
    with SSHTunnelForwarder(master_ip, username, ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
        conn = pymysql.connect(host=master_ip, user='root', password='root', db='sakila', port=3306, autocommit=True)
        cursor = conn.cursor()
        operation = query
        cursor.execute(operation)
        print(cursor.fetchall())

    return cursor.fetchall(),200
        
@app.route('/health')
def health_check():
  # If everything is fine, return a 200 OK response when ping http://your-instance-ip:80/health
  return 'OK', 200

  # 0.0.0.0 allows incoming connections from any IP address
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)


# NEED KEY PAIR