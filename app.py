import sys
from flask import Flask
import pymysql
from sshtunnel import SSHTunnelForwarder

app = Flask(__name__)

# change ips and push
master_ip="172.31.21.78" # sys.argv[1]
slaves_ip=[
    "172.31.31.114",
    "172.31.24.46",
    "172.31.27.249"
]  # sys.argv[2:5]
username='ubuntu'


@app.route('/direct')
def direct_hit(master_ip,query):
    print("master_ip:",master_ip)
    print("query:",query)
    
    # change ssh_key import
    with SSHTunnelForwarder(master_ip, username, ssh_pkey='vockey.pem', remote_bind_address=(master_ip, 3306)) as tunnel:
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