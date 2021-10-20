#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
import logging
import sys
import argparse
from kubernetes import client, config

FALLBACK_ARGS = dict(namespace='default', filename='k8s', directory='diagrams',
                     label='Kubernetes',)


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

    def __init__(self, namespace) -> None:

        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.namespace = namespace

    def get_pods(self) -> list:

        pod_list = self.v1.list_namespaced_pod(self.namespace)
        return pod_list.items


def main():

    options = ParseArgs()
    logging.basicConfig(format="%(message)s",
                        stream=sys.stdout, level=logging.INFO)

    k8s_diagrams = K8sDiagrams(namespace=options.args.namespace)
    pods = k8s_diagrams.get_pods()

    for pod in pods:
        print(pod.metadata.name)


if __name__ == '__main__':
    main()
