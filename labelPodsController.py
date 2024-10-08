from os import error
from kubernetes import client, config, watch
import argparse

parser = argparse.ArgumentParser(description='Pod labelling controller')
parser.add_argument('--ns', action="store", dest='namespace', default="default")
args = parser.parse_args()

def controller(namespace):
    v1Api = client.CoreV1Api()
    w = watch.Watch()

    # Monitor k8s events
    for event in w.stream(v1Api.list_pod_for_all_namespaces):  
        # Define labels
        podName = event['object'].metadata.name
        podNamespace = event['object'].metadata.namespace
        podIpAddress = event['object'].status.pod_ip
        eventType =  event['type']
        podOwner = event['object'].metadata.owner_references
        nodeOwner = event['object'].spec.node_name
        # Check for pods that were added
        if ( ( event['type'] == "ADDED" or event['type'] == "MODIFIED" ) and podNamespace == namespace ):
            print(f"The pod {podName} in namespace {podNamespace} has been {eventType}")
            ## Check if the pod belongs to a replicaset, statefulset or if it's a naked pod
            if podOwner:
                # If th epod belongs to another k8s object get the owner ref and update the labels 
                for ownerRef in podOwner:
                    resourceOwner = str(ownerRef.name)
                    print(f"The pod {podName} originates from {resourceOwner} and is part of {ownerRef.kind}")
                    try:
                        update_pods(podName, namespace, resourceOwner, podIpAddress, nodeOwner)
                    except Exception as error:
                        print(f"Coudln't update the pods; see below error \n {error}")
            else:
                # If the pod is a naked pod, update the labels
                resourceOwner = "nakedPod"
                print(f"The pod  {podName} is a naked pod")
                update_pods(podName, namespace, resourceOwner, podIpAddress, nodeOwner)

def update_pods( podName, namespaceName, resourceOwner, podIpAddress, nodeOwner):
    v1Api = client.CoreV1Api()
    # Get the pod definition
    try:
        body = v1Api.read_namespaced_pod(name=podName, namespace=namespaceName)
    except Exception as error:
        print(f"Couldn't retrieve the pods; see below error \n {error}")
    print(f"Updating pod names: {body.metadata.name}")
    print(f"The current labels are: {body.metadata.labels}")
    # Update lables dict
    labels = body.metadata.labels
    labels['environment'] = 'production'
    labels['owningResource'] = f'{resourceOwner}'
    labels['ipAddress'] = f'{podIpAddress}'
    labels['nodeOwner'] = f'{nodeOwner}'
    print(f"This are the updated labels: {labels}")
    body.metadata.labels = labels
    # Patching the pod with the new lables
    try:
        resp = v1Api.patch_namespaced_pod(name=podName, namespace=namespaceName, body=body)
    except Exception as error:
         print(f"Coudln't patch the pods; see below error \n {error}")
    
def main():
    # Uncomment the below line to use the local k8s config context
    # config.load_kube_config()
    # For cluster deployment use the one below
    config.load_incluster_config()
    controller(args.namespace)

if __name__ == '__main__':
    main()