# -*- coding: utf-8 -*-
''''' 使用kafka-Python 1.3.3模块 '''
import cv2
import time
import argparse
import numpy as np
from imutils.video import FPS

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from kafka import TopicPartition


class Kafka_producer():
    ''''' 生产模块: 根据不同的key, 区分消息 '''
    def __init__(self, args):
        self.kafkaHost = args.kafka_host
        self.kafkaPort = args.kafka_port
        self.kafkatopic = args.topic
        self.key = args.key
        self.num_frame = args.num_frame
        self.h, self.w = args.resolution
        print("producer:h,p,t,k", self.kafkaHost, self.kafkaPort, self.kafkatopic, self.key)
        bootstrap_servers = f'{self.kafkaHost}:{self.kafkaPort}'
        print("boot svr:", bootstrap_servers)
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, batch_size=16384, linger_ms=0)

    def sendvideo(self):
        # start producer
        producer = self.producer

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception('Could not open video device')
        cap.set(cv2.CAP_PROP_FPS, 10)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        fps_p = FPS().start()

        print("publishing video...")
        num_frame = self.num_frame
        while num_frame == -1 or fps_p._numFrames <= num_frame:
            ret, frame = cap.read()
            if frame is not None:
                frame = cv2.resize(frame, (self.w, self.h))
                print(fps_p._numFrames)
                # send to kafka topic
                k = f'{self.key}_img'.encode()
                producer.send(self.kafkatopic, key=k, value=frame.tobytes())
                fps_p.update()
            else:  # incase camera don't work
                parmas_message = 'No video detected!'
                k = f'{self.key}_noimg'.encode()
                v = parmas_message.encode()
                print("send msg:(k,v)", k, v)
                producer.send(self.kafkatopic, key=k, value=v)
                break

        fps_p.stop()
        print(f'fps: {fps_p.fps():.0f}')
        cap.release()

    def sendchar(self, char):
        # start producer
        producer = self.producer
        producer.send(self.kafkatopic, value=char.encode('utf8'))


class Kafka_consumer():
    ''''' 消费模块: 通过不同groupid消费topic里面的消息 '''

    def __init__(self, args):
        self.kafkaHost = args.kafka_host
        self.kafkaPort = args.kafka_port
        self.key = args.key
        self.consumer = KafkaConsumer(args.topic, group_id=args.group_id,
                                      bootstrap_servers=f'{self.kafkaHost}:{self.kafkaPort}',
                                      auto_offset_reset="earliest",
                                      )
        # partition = TopicPartition(self.kafkatopic, 0)
        # self.consumer.assign([partition])
        # start = 30
        # self.consumer.seek(partition, start)

    def consume_data(self):
        try:
            for message in self.consumer:
                yield message
        except KeyboardInterrupt as e:
            print(e)


def main(args):
    ''''' 测试consumer和producer '''
    if args.producer:
        # 生产模块
        producer = Kafka_producer(args)
        print("===========> producer:", producer)
        # producer.sendjsondata(params)
        # try:
        #     producer.sendvideo()
        # except KafkaError as e:
        #     print(e)
        for i in range(1000):
            time.sleep(0.25)
            producer.sendchar(str(i))
            print(i)

    if args.consumer:
        # 消费模块
        img_h, img_w = args.resolution
        fps = FPS().start()

        consumer = Kafka_consumer(args)
        print("===========> consumer:", consumer)
        message = consumer.consume_data()
        for msg in message:
            print('offset---------------->', msg.offset)
            print(msg.value.decode('utf8'))
            # k, k_state = msg.key.decode().split('_')
        #     if k_state == 'noimg':
        #         print('msg---------------->k,v', k, msg.value.decode())
        #     elif k_state == 'img':
        #         decoded = np.frombuffer(msg.value, np.uint8)
        #         decoded = decoded.reshape(img_h, img_w, 3)
        #         print(fps._numFrames)

        #         # cv2.imshow("Cam", decoded)
        #         cv2.imwrite('./out.jpg', decoded)

        #         fps.update()

        # fps.stop()
        # cv2.destroyAllWindows()
        # print(f'fps: {fps.fps():.0f}')


def make_parser():
    parser = argparse.ArgumentParser("onnxruntime inference sample")
    parser.add_argument(
        "--producer",
        action="store_true",
        help="Being producer.",
    )
    parser.add_argument(
        "--consumer",
        action="store_true",
        help="Being consumer.",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default='test',
        help="Kafka topics.",
    )
    parser.add_argument(
        "--group_id",
        type=str,
        default='g',
        help="Group_id when consumimg data.",
    )
    parser.add_argument(
        "--key",
        type=str,
        default="camera_id0",
        help="The key for each msg, better be the camera id.",
    )
    parser.add_argument(
        "--resolution",
        type=str,
        default="576,768",
        help="The height and weigth of the images.",
    )
    parser.add_argument(
        "--kafka_host",
        type=str,
        default='172.20.10.64',
        help="The host ip of the kafka server.",
    )
    parser.add_argument(
        "--kafka_port",
        type=int,
        default=9092,
        help="The port of the kafka server.",
    )
    parser.add_argument(
        "--num_frame",
        type=int,
        default=-1,
        help="The number of video frames to produce. -1 means take all frames.",
    )
    return parser


if __name__ == '__main__':
    args = make_parser().parse_args()
    args.resolution = list(map(int, args.resolution.split(',')))

    main(args)
    # python testkafka.py --producer --topic test --key key --num_frame 100 --resolution 75,100  # 生产消息
    # python testkafka.py --consumer --topic test --group_id newg --key key --resolution 75,100  # 消费消息
    # 为了可以发送大于1MB的图片需要在broker端修改: message.max.bytes:1048588
    # 查看消息数: kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic test --time -1
    # kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic test --time -2
