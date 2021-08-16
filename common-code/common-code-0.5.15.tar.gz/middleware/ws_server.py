import json
import socket
from queue import Queue
from threading import Thread, Lock, Event
from time import sleep
from common.logging_config import logger


class WebSocketServer:
    def __init__(self):
        self.conn_event = {}

    def send_msg(self, conn, msg, encoding="utf-8"):
        """
        发送数据
        :param conn:
        :param msg:
        :param encoding:
        :return:
        """
        if isinstance(msg, dict) or isinstance(msg, list):
            msg = json.dumps(msg)
        # logger.debug("send msg ", msg, conn)
        if not isinstance(msg, bytes):
            msg = msg.encode(encoding)
        try:
            conn.send(msg)
            return True
        except:
            return False

    def recv_msg(self, conn, event: Event, encoding="utf-8"):
        """
        接收客户端发送过来的msg
        :param conn:
        :param encoding:
        :return:
        """
        while event.is_set():
            try:
                data = conn.recv(1024)
            except:
                break
            data = data.decode(encoding)
            logger.info(data)
            # self.send_msg(conn, 'recv' + data)

        logger.info("close recv msg", conn)

    def close_recv_thread(self, conn):
        if conn in self.conn_event.keys():
            event = self.conn_event[conn]
            event.clear()
            del self.conn_event[conn]
            logger.info("close recv thread", conn)
        else:
            logger.warning("non existent key", conn)

    def wait_socket_connect(self):
        """
        循环等待客户端建立连接，并开启后台接收数据
        """
        while True:
            try:
                conn, addr = self.sock.accept()
                logger.debug("连接地址: %s" % str(addr))
                conn.send("connent websocket success".encode("utf-8"))
                event = Event()
                _thread = Thread(target=self.recv_msg, args=(conn, event))
                event.set()
                self.conn_event[conn] = event
                _thread.start()
            except Exception as e:
                logger.exception(e)

    def start_socket_server(self, port=5678, maxwaituser=5):
        """
        socket服务端监听客户端
        1.启动socket
        2.开启等待客户端建立连接的线程
        """
        logger.info("start websocket server", port, maxwaituser)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定端口号
        self.sock.bind(("0.0.0.0", port))

        # 设置最大连接数，超过后排队
        self.sock.listen(maxwaituser)

        # 启线程循环等待客户端建立连接
        Thread(target=self.wait_socket_connect).start()

    def daemon_run_ws_server(self, port=5678, maxwaituser=5):
        Thread(target=self.start_socket_server, args=(port, maxwaituser)).start()


class MeasWSServer(WebSocketServer):
    def __init__(self):
        super().__init__()
        # 保持连接的信息
        self.conn_info = {}

        # 将需要推送的信息入队
        self.q = Queue()

        self.lock = Lock()

    def enqueue_meas(self, topic, meas):
        """
        需要发送的测量数据入队
        :param topic:
        :param meas:
        :return:
        """
        if topic and meas and topic in self.conn_info.keys():
            self.q.put((topic, meas))

    def recv_msg(self, conn, event: Event, encoding="utf-8"):
        """
        重写，接收客户端的msg，订阅数据
        :param conn:
        :param encoding:
        :return:
        """
        while event.is_set():
            try:
                data = conn.recv(1024)
            except:
                break
            data = data.decode(encoding)
            logger.info(data)
            if data in self.conn_info.keys():
                self.conn_info[data].add(conn)
            else:
                self.conn_info[data] = {conn}
            # logger.debug(self.conn_info.keys())
            self.send_msg(conn, "subscrib {data} success".format(data=data))
        logger.info("close recv msg", conn)

    def clear_empty_conn_topic(self):
        """
        清除没有用户连接的topic
        """
        logger.info("start clear empty conn topic thread")
        while True:
            try:
                # 添加没有连接的topic
                empty_list = []
                for topic in self.conn_info:
                    if len(self.conn_info[topic]) == 0:
                        empty_list.append(topic)

                # region 删除当前没有连接的topic
                self.lock.acquire()
                for topic in empty_list:
                    try:
                        if len(self.conn_info[topic]) == 0:
                            del self.conn_info[topic]
                            logger.info("clear empty conn topic", topic)
                    except Exception as e:
                        logger.exception(e)
                self.lock.release()
                # endregion
            except Exception as e:
                logger.exception(e)

            sleep(60)

    def daemon_push_msg(self):
        """
        消息推送到对应的客户端
        """
        logger.info("start daemon push msg thread")
        while True:
            try:
                # region 判断是否有客户端连接，有才推送消息
                if not self.q.empty():
                    data = self.q.get()
                    topic = data[0]
                    if topic in self.conn_info.keys():
                        remove_set = set()
                        for conn in self.conn_info[topic]:
                            status = self.send_msg(conn, data[1])
                            if status == False:
                                # 删除断开连接的记录
                                remove_set.add(conn)
                                # self.conn_info[topic].remove(conn)
                                # logger.info("delete a closed connection", topic, conn)
                        if remove_set:
                            self.conn_info[topic] = self.conn_info[topic] - remove_set
                            logger.info("remove close conn", remove_set, self.conn_info)
                # endregion
            except Exception as e:
                logger.exception(e)

    def daemon_run_server(self, port=5678, maxwaituser=5):
        """
        websockets推送测量数据主线程
        1、启动后台清除空topic（无客户端连接）的线程
        2、启动websockets服务器
        3、启动后台推送测量数据的线程
        :param port:
        :param maxwaituser:
        :return:
        """
        Thread(target=self.clear_empty_conn_topic).start()
        self.daemon_run_ws_server(port=port, maxwaituser=maxwaituser)
        Thread(target=self.daemon_push_msg).start()


if __name__ == "__main__":
    # web = WebSocketServer()
    #
    # web.daemon_run_ws_server()
    web = MeasWSServer()
    web.daemon_run_server()
