import json

import requests
import base64


class EtcdHelper(object):
    def __init__(self,ip,port):
        self.ip=ip
        self.port=port
        self.check_version()
        # self.client = Client(ip, port, cert=cert, verify=verify)

    def check_version(self):
        def build_url():
            return "http://{}:{}/version".format(self.ip,self.port)
        resp= requests.get(build_url())
        if resp.status_code>=300:
            resp.raise_for_status()
        else:
            version = resp.json()["etcdserver"]
            print("[*] Etcd Version : {}".format(version))
            version_list=version.strip().split('.')
            if version_list[0]!="3":
                raise Exception("Etcd Not supported.")
            elif int(version_list[1])<=3:
                self.api="v3alpha"
            elif int(version_list[1])>=4:
                self.api="v3"
            else:
                self.api="v3"


    @staticmethod
    def encode(input):
        return str(base64.b64encode(bytes(input,encoding="utf-8")),encoding="utf-8")

    @staticmethod
    def decode(input):
        return str(base64.b64decode(input), encoding="utf-8")


    def put(self,key,value):
        def build_url():
            return "http://{}:{}/{}/kv/put".format(self.ip,self.port,self.api)
        resp = requests.post(build_url(),data='{"key": "%s", "value": "%s"}' % (self.encode(key),self.encode(value)))
        if resp.status_code>=300:
            resp.raise_for_status()

        # print(self.client.version())
        # self.client.put(key, value)

    def get(self,key):
        def build_url():
            return "http://{}:{}/{}/kv/range".format(self.ip,self.port,self.api)
        resp=requests.post(build_url(),data='{"key": "%s"}' % self.encode(key))
        if resp.status_code>=300:
            resp.raise_for_status()
        result = resp.json().get('kvs')
        # result = self.client.range(key).kvs
        if not result or len(result)==0:
            return None
        else:
            for value in result:
                return self.decode(value["value"])


if __name__ == '__main__':
    etcd=EtcdHelper("172.20.100.150",2379)
    etcd.put("test","newtest")
    print(etcd.get("test"))