# -*- coding: utf-8 -*-
''''' 使用kafka-Python 1.3.3模块 '''

import sys
import time
import json

from icecream import ic

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError


KAFAKA_HOST = '172.20.10.64'
KAFAKA_PORT = 9092
KAFAKA_TOPIC = "test1"


class Kafka_producer():
    ''''' 生产模块: 根据不同的key, 区分消息 '''

    def __init__(self, kafkahost, kafkaport, kafkatopic, key):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.key = key
        print("producer:h,p,t,k", kafkahost, kafkaport, kafkatopic, key)
        bootstrap_servers = f'{self.kafkaHost}:{self.kafkaPort}'
        print("boot svr:", bootstrap_servers)
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    def sendjsondata(self, params):
        try:
            parmas_message = json.dumps(params, ensure_ascii=False)
            producer = self.producer
            ic(parmas_message)
            v = parmas_message.encode('utf-8')
            k = key.encode('utf-8')
            ic("send msg:(k,v)", k, v)
            producer.send(self.kafkatopic, key=k, value=v)
            producer.flush()
        except KafkaError as e:
            print(e)


class Kafka_consumer():
    ''''' 消费模块: 通过不同groupid消费topic里面的消息 '''

    def __init__(self, kafkahost, kafkaport, kafkatopic, groupid):
        self.kafkaHost = kafkahost
        self.kafkaPort = kafkaport
        self.kafkatopic = kafkatopic
        self.groupid = groupid
        self.key = key
        self.consumer = KafkaConsumer(self.kafkatopic, group_id=self.groupid,
                                      bootstrap_servers=f'{self.kafkaHost}:{self.kafkaPort}'
                                      )

    def consume_data(self):
        try:
            for message in self.consumer:
                yield message
        except KeyboardInterrupt as e:
            print(e)


def main(xtype, group, key):
    ''''' 测试consumer和producer '''
    if xtype == "p":
        # 生产模块
        producer = Kafka_producer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC, key)
        print("===========> producer:", producer)
        for _id in range(10):
            params = f'消息: {_id}'
            producer.sendjsondata(params)
            time.sleep(1)

    if xtype == 'c':
        # 消费模块
        consumer = Kafka_consumer(
            KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC, group)
        print("===========> consumer:", consumer)
        message = consumer.consume_data()
        for msg in message:
            ic('msg---------------->k,v', msg.key, msg.value.decode('utf-8'))
            ic('offset---------------->', msg.offset)


if __name__ == '__main__':
    xtype = sys.argv[1]
    group = sys.argv[2]
    key = sys.argv[3]
    main(xtype, group, key)
    # python testkafka.py p g key  # 生产消息
    # python testkafka.py c g key  # 消费消息
