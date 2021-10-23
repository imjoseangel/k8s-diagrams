#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
import logging
import sys
import argparse
from diagrams import Cluster, Diagram
from diagrams.k8s.compute import Pod
from diagrams.k8s.group import NS
from kubernetes import client, config

FALLBACK_ARGS = dict(namespace='default', filename='k8s', directory='diagrams',
                     label='Kubernetes')


class ParseArgs:
    def __init__(self):

        # Parse arguments passed at cli
        self.parse_arguments()

    def parse_arguments(self):

        description = '''

    ┬┌─┌─┐┌─┐  ┌┬┐┬┌─┐┌─┐┬─┐┌─┐┌┬┐┌─┐
    ├┴┐├─┤└─┐ ─ │││├─┤│ ┬├┬┘├─┤│││└─┐
    ┴ ┴└─┘└─┘  ─┴┘┴┴ ┴└─┘┴└─┴ ┴┴ ┴└─┘

    Create diagram from the Kubernetes API.'''

        parser = argparse.ArgumentParser(description=description,
                                         formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('--namespace',
                            '-n',
                            help=('The namespace we want to draw. (default: '
                                  '"default") [$KUBECTL_NAMESPACE]'),
                            default=FALLBACK_ARGS['namespace'])

        parser.add_argument('--kubeconfig',
                            '-k',
                            help='The path to your kube config file. [$KUBECONFIG]')

        parser.add_argument('--filename',
                            '-f',
                            help='The output filename. (default: "k8s")',
                            default=FALLBACK_ARGS['filename'])

        parser.add_argument('--directory',
                            '-d',
                            help='The output directory. (default: "diagrams")',
                            default=FALLBACK_ARGS['directory'])

        parser.add_argument('--label',
                            '-l',
                            help='The diagram label. (default: "Kubernetes")',
                            default=FALLBACK_ARGS['label'])

        self.args = parser.parse_args()


class K8sDiagrams:

    def __init__(self, namespace, label) -> None:

        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.appsv1 = client.AppsV1Api()
        self.namespace = namespace
        self.label = label

    def get_pods(self) -> list:

        pod_list = self.v1.list_namespaced_pod(self.namespace)
        return pod_list.items

    def get_deployments(self) -> list:

        deployment_list = self.appsv1.list_namespaced_deployment(
            self.namespace)
        return deployment_list.items

    def get_services(self) -> list:

        service_list = self.v1.list_namespaced_service(self.namespace)
        return service_list.items

    def create_diagram(self, pods) -> None:

        with Diagram(self.label, show=False):

            ns = NS(self.namespace)

            with Cluster("Pods"):
                pod_group = [Pod(pod.metadata.name) for pod in pods]

            ns >> pod_group


def main():

    options = ParseArgs()
    logging.basicConfig(format="%(message)s",
                        stream=sys.stdout, level=logging.INFO)

    k8s_diagrams = K8sDiagrams(
        namespace=options.args.namespace, label=options.args.label)
    pods = k8s_diagrams.get_pods()

    k8s_diagrams.create_diagram(pods)

    # for pod in pods:
    #     logging.info(pod.metadata.name)
    #     logging.info(pod.metadata.labels)

    # deployments = k8s_diagrams.get_deployments()

    # for deployment in deployments:
    #     logging.info(deployment.metadata.name)

    # services = k8s_diagrams.get_services()

    # for service in services:
    #     logging.info(service.spec.selector)


if __name__ == '__main__':
    main()
