#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
import json
import logging
import threading
import time

from confluent_kafka.cimpl import KafkaError, KafkaException
from munch import Munch

from api.model.FactDatasource import FactDatasource, FactDatasourceTypeEnum
from config.annotation import Value
from factdatasource import InnerFdCode, fold_ref_fds
from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from factdatasource.dao.kafka.MultipleKafkaDatasource import CustomKafkaClient
from libs.utils import Singleton

log = logging.getLogger('Ficus')


def wait_using_fd(fd_context_holder: FactDatasourceContextHolder, action: int, fact_datasource: FactDatasource):
    def listen_using_fd():
        fd_code = fact_datasource.code
        if fd_context_holder.is_using_fact_datasource(fd_code):
            while fd_context_holder.is_using_fact_datasource(fd_code):
                log.debug(f'监听到数据源{fd_code}的{action}事件，等待数据源使用完毕')
                time.sleep(0.5)

        if action == FactDatasourceChangeListener.ACTION_UPDATE:
            fd_context_holder.update_fact_datasource(fact_datasource)
        elif action == FactDatasourceChangeListener.ACTION_DELETE:
            fd_context_holder.remove_fact_datasource(fact_datasource)

    thread = threading.Thread(name='wait_using_fd', target=listen_using_fd, daemon=True)
    thread.start()


class FactDatasourceChangeListener(threading.Thread, Singleton):
    """
    监听数据源消息
    """
    ACTION_ADD = 0
    ACTION_UPDATE = 1
    ACTION_DELETE = 2

    FACT_DATASOURCE_CHANGE_TOPIC = 'springCloudBus'

    @Value("${actor.name:unknown}")
    def actor_name(self):
        pass

    def __init__(self):
        threading.Thread.__init__(self)

        client: CustomKafkaClient = get_multiple_datesource(FactDatasourceTypeEnum.KAFKA).get_client()
        self.producer = client.producer
        self.consumer = client.consumer
        self.running = False
        # 守护线程运行
        self.daemon = True

    @property
    def fd_context_holder(self):
        return FactDatasourceContextHolder.instance()

    def run(self):
        if self.running:
            log.warning(f'FD监听线程已启动无需重复启动')
            return
        self.running = True

        # 这里关心已使用过的FD的修改和删除消息，添加应该不需要关心
        # 这里监听到消息有两件事， 1. fd_context的事件处理  2. 多数据源的事件处理
        # 3.修改和删除需要判断该数据源是否正在使用，如果正在使用需要等待使用完成后在进行修改
        self.consumer.subscribe([self.FACT_DATASOURCE_CHANGE_TOPIC])

        while self.running:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        # Error
                        raise KafkaException(msg.error())
                else:
                    # 进行消息的处理
                    message = Munch(json.loads(msg.value()))
                    # 只处理FactDatasourceChangeEvent事件
                    if message.type == 'FactDatasourceChangeEvent':
                        self.deal_message(message)
            except Exception as e:
                log.exception(f"监听FactDatasourceChange消息出现问题,", e)
            finally:
                if self.running == False:
                    # 把消息队列关闭掉
                    self.consumer.close()

    def stop(self):
        self.running = False

    def deal_message(self, change_event):
        action = change_event.action

        # 需要判断是否是这个actor所关心的fd

        # TODO 这里有问题 event里面的fd的 type有可能是ref的.这就导致了后面卸载的时候卸载不了
        #  还有一个问题 那就是 A->ref B   然后某个CE是关联的A.  那么B变更了后,现在这里是不会处理的
        #  要解决这个问题,就需要和JAVA的一样, 要找到这个执行器所关心的FD,并且把ref的也要找出来.处理.
        #  也就是这个类要重写
        fact_datasource = FactDatasource(**change_event.factDatasource)

        if action == self.ACTION_ADD:
            # 不关心添加数据源事件
            return

        # 这里就需要处理了
        actor_name = self.actor_name()
        # 找到这个执行器所有关心的fds
        actor_fds = self.find_actor_fds(actor_name)

        # 这个就是这个执行器所关心的所有的FD
        from client import FactDatasourceManageClient
        fact_datasources = [
            FactDatasourceManageClient.get(inner_fd_code.site, inner_fd_code.project, inner_fd_code.code)
            for inner_fd_code in actor_fds]

        # 把用户关心的FD都查询一遍,找到ref
        actorFdsWithRef = set()
        for datasource in fact_datasources:
            if datasource.type == "REF" and datasource.ref is not None:
                tmp = list(map(lambda fd: InnerFdCode(fd.site, fd.projectCode, fd.code), fold_ref_fds(datasource)))
                actorFdsWithRef.update(tmp)
            else:
                tmp = [InnerFdCode(datasource.site, datasource.projectCode, datasource.code)]
                actorFdsWithRef.update(tmp)

        # 判断是否是这个actor所关心的
        any = list(filter(lambda
                              actor_fd: actor_fd.site == fact_datasource.site and actor_fd.project == fact_datasource.projectCode and actor_fd.code == fact_datasource.code,
                          actorFdsWithRef))
        # 如果这里的any有值,说明满足要求
        if any is None or len(any) == 0:
            # 说明这个执行器不关心这个FD的变化,不进行处理
            return

        # 这里需要找到这个fd变化后 影响到的 fds
        changed_fds = set()
        from client import FactDatasourceClient
        for datasource in fact_datasources:
            # 第二次做遍历
            if datasource.type == "REF" and datasource.ref is not None:
                tmp = fold_ref_fds(datasource)
                rrr = list(filter(lambda
                                      actor_fd: actor_fd.site == fact_datasource.site and actor_fd.projectCode == fact_datasource.projectCode and actor_fd.code == fact_datasource.code,
                                  tmp))
                if rrr is not None and len(rrr) > 0:
                    changed_fds.add(FactDatasource(**FactDatasourceClient.fd(datasource.code)))       # TODO 这里是有问题的,应该使用 FactDatasourceClient.fd(fd_code)
            else:
                if datasource.site == fact_datasource.site and datasource.projectCode == fact_datasource.projectCode and datasource.code == fact_datasource.code:
                    changed_fds.add(FactDatasource(**FactDatasourceClient.fd(datasource.code)))   # TODO 这里是有问题的,应该使用 FactDatasourceClient.fd(fd_code)

        for fd in changed_fds:
            if not self.fd_context_holder.is_loaded_fact_datasource(fd.code):
                # 本地数据源还没有使用不进行处理
                continue

            if self.fd_context_holder.is_using_fact_datasource(fd.code):
                wait_num = 0
                while self.fd_context_holder.is_using_fact_datasource(fd.code):
                    log.debug(f'监听到数据源{fd.code}的{action}事件，等待数据源使用完毕')
                    wait_num += 1
                    time.sleep(0.5)
                    # 5秒都还在使用的话就只能使用新线程来处理了,否则无法处理后续的事件
                    if wait_num > 10:
                        wait_using_fd(self.fd_context_holder, action, fd)
                        break

            log.info(f"FD({fd.get_source_name()}接收到变化:{action} 开始刷新)")

            if action == self.ACTION_UPDATE:
                self.fd_context_holder.update_fact_datasource(fd)
            elif action == self.ACTION_DELETE:
                self.fd_context_holder.remove_fact_datasource(fd)

    def find_actor_fds(self, actor_name) -> set:
        """
        找到这个actor所有的jobs,并找到他们的fdCode
        :param actor_name:
        :return:
        """

        # 找到这个actor所对应的所有的jobs
        from client import JobScheduleClient
        jobs = JobScheduleClient.get_jobs(actor_name)

        if jobs is None or len(jobs) == 0:
            return set()

        return self.__generate_fd_codes(jobs)

    def __generate_fd_codes(self, jobs: list) -> set:
        """
        构造出job的所有FD信息
        :param jobs:
        :return:
        """
        fdCodes = set()

        for job in jobs:
            actorParam = job.actorParam
            if actorParam is None or actorParam == "":
                continue
            try:
                json_object = json.loads(actorParam)
                code_ = json_object["code_"]
                site_ = json_object["site_"]
                projectCode_ = json_object["projectCode_"]
                from client import ComputeExecutionClient
                dataComputeExecution = ComputeExecutionClient.get(site_, projectCode_, code_)
                if dataComputeExecution is None:
                    # 有可能是crawl
                    from client import DataCrawlClient
                    dataCrawl = DataCrawlClient.get(site_, projectCode_, code_)
                    if dataCrawl is None:
                        # 既不是ce又不是crawl,跳过
                        continue
                    fdCodes.update(self.__innerAddFdCodes(site_, projectCode_, dataCrawl.outputFdCodes))
                else:
                    fdCodes.update(self.__innerAddFdCodes(site_, projectCode_, dataComputeExecution.sourceFdCodes))
                    fdCodes.update(self.__innerAddFdCodes(site_, projectCode_, dataComputeExecution.outputFdCodes))
            except:
                pass

        return fdCodes

    def __innerAddFdCodes(self, site_, projectCode_, outputFdCodes: list) -> list:
        if outputFdCodes is None or len(outputFdCodes) == 0:
            return list()

        return list(map(lambda code: InnerFdCode(site_, projectCode_, code), outputFdCodes))
