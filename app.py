import sys
from flask import Flask, jsonify
import pymysql
from sshtunnel import SSHTunnelForwarder
from flask import request
import random
import botocore.session
import os
from dotenv import load_dotenv

# http://3.89.10.113/direct?query=SELECT%20COUNT(*)%20FROM%20film;

from pythonping import ping

app = Flask(__name__)

master_ip="" 
slaves_ip=[] 

key='tmp1.pem'

@app.route('/direct')
def direct_hit():
    query = request.args.get('query')
    print("master_ip:",master_ip)
    print("query:",query)
    
    # connection ssh with master
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

    for slave in slaves_ip:
        response = ping(slave, timeout=1, count=4)
        latency[slave] = response.rtt_avg_ms


    sorted_dict=dict(sorted(latency.items(), key=lambda item: item[1]))
    print(sorted_dict.keys())
    shortestslave=list(sorted_dict.keys())[0]
    print("shortest:",shortestslave)
    
    # connection ssh with shortest slave
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
    
       # connection ssh with random
    with SSHTunnelForwarder((random_ip,22), ssh_username="ubuntu", ssh_pkey=key, remote_bind_address=(master_ip, 3306)) as tunnel:
            conn = pymysql.connect(host=master_ip, user='root', db='sakila', port=3306, autocommit=True)
            cursor = conn.cursor()
            operation = query
            cursor.execute(operation)
            result = cursor.fetchall()
            conn.close()
    
    return jsonify({"result": result})
   
def get_instance_ip():
    session = botocore.session.Session()
    load_dotenv()
    session.set_credentials(
        access_key=os.getenv("ACCESS_KEY_ID"),
        secret_key=os.getenv("SECRET_ACCESS_KEY_ID"),
    )
    ec2_client=session.create_client('ec2',region_name=os.getenv("REGION"))
    
    masters = ec2_client.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Name', 'Values': ['master']}
        ]
    )

    master_found=""
    for reservation in masters['Reservations']:
        for instance in reservation['Instances']:
            print(instance.get('PublicIpAddress'))
            master_found = instance.get('PublicIpAddress')

    slaves = ec2_client.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:Name', 'Values': ['slave1','slave2','slave3']}        
        ]
    )

    slaves_found=[]
    for reservation in slaves['Reservations']:
        for instance in reservation['Instances']:
            print(instance.get('PublicIpAddress'))
            ip = instance.get('PublicIpAddress')
            if ip: 
                slaves_found.append(ip)

    return master_found,slaves_found

        
@app.route('/health')
def health_check():
  # If everything is fine, return a 200 OK response when ping http://your-instance-ip:80/health
  return 'OK', 200

  # 0.0.0.0 allows incoming connections from any IP address
if __name__ == '__main__':
  master_ip,slaves_ip=get_instance_ip()
  print("master_ip:",master_ip)
  print("slaves_ip",slaves_ip)
  app.run(host='0.0.0.0', port=80)


# NEED KEY PAIR