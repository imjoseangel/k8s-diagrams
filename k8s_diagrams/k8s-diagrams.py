#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

from kubernetes import client, config


class K8sDiagrams():

    def __init__(self) -> None:

        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def get_pods(self) -> list:

        pod_list = self.v1.list_namespaced_pod('default')
        return pod_list.items


def main():

    k8s_diagrams = K8sDiagrams()
    pods = k8s_diagrams.get_pods()

    for pod in pods:
        print(pod.metadata.name)


if __name__ == '__main__':
    main()
