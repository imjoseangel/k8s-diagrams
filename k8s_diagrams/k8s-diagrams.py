#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W1203

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
import logging
import sys
import argparse
from diagrams import Cluster, Diagram
from diagrams.k8s.clusterconfig import HPA
from diagrams.k8s.compute import Deploy, Pod, RS
from diagrams.k8s.group import NS
from diagrams.k8s.network import Ingress, Service, Endpoint
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

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

    def __init__(self, namespace, label, filename) -> None:

        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.appsv1 = client.AppsV1Api()
        self.namespace = namespace
        self.label = label
        self.filename = filename

    def get_pods(self) -> list:

        try:
            pods = self.v1.list_namespaced_pod(self.namespace)
        except ApiException as e:
            logging.error(
                f'Exception when calling CoreV1Api->list_namespaced_pod: {e}')
            sys.exit(1)

        return pods.items

    def get_deployments(self) -> list:

        deployments = self.appsv1.list_namespaced_deployment(
            self.namespace)
        return deployments.items

    def get_services(self) -> list:

        services = self.v1.list_namespaced_service(self.namespace)
        return services.items

    def get_endpoints(self) -> list:

        endpoint_list = self.v1.list_namespaced_endpoints(self.namespace)
        return endpoint_list.items

    def create_diagram(self, pods, services, deployments) -> None:

        with Diagram(self.label, show=False, filename=self.filename):

            # pod_group = [Pod(pod.metadata.name) for pod in pods]

            [[Pod(pod.metadata.name)
              for pod in pods if pod.metadata.labels.get(
                'app') == deployment.spec.selector.match_labels.get('app')] <<
                Deploy(deployment.metadata.name) for deployment in deployments]

            # for service in services:

            #     if service.spec.selector:
            #         [Pod(pod.metadata.name) for pod in pods if pod.metadata.labels.get(
            #             'app') == service.spec.selector.get('app')] << Service(
            #                 service.metadata.name)

            # ns = NS(self.namespace)
            # for service in services:
            #     svc = Service(service.metadata.name)
            #     svc >> Pod(service.metadata.name)

            # with Cluster(self.namespace):

            # NS(self.namespace)

            # service_group = [Service(service.metadata.name)
            #                  for service in services]

            # pod_group


def main():

    options = ParseArgs()
    logging.basicConfig(format="%(message)s",
                        stream=sys.stdout, level=logging.INFO)

    k8s_diagrams = K8sDiagrams(
        namespace=options.args.namespace, label=options.args.label,
        filename=options.args.filename)

    deployments = k8s_diagrams.get_deployments()
    pods = k8s_diagrams.get_pods()
    services = k8s_diagrams.get_services()

    k8s_diagrams.create_diagram(pods, services, deployments)

    # deployments = k8s_diagrams.get_deployments()

    # for deployment in deployments:
    #     logging.info(deployment.metadata.name)

    # services = k8s_diagrams.get_services()

    # for service in services:
    #     logging.info(service.spec.selector)


if __name__ == '__main__':
    main()
