# Python based controller that labels the pods running in the default namespace

### For local development 
The script uses the local k8s config context ( ~/.kube/config ) 

```
python3 -m venv .venv
```
```
source .venv/bin/activate
```
```
python3 -m pip install -r requirements.txt
```
```
python3 labelPodsController.py
```

### To deploy in a cluster 

Create a container using the provided dockerfile

```
docker build -t label-pods-controller:0.0.1 .
```
Tag for your favourite repository
```
docker tag label-pods-controller:0.0.1 localhost:32000/label-pods-controller:0.0.1
```
Push the image to the registry
```
docker push localhost:32000/label-pods-controller:0.0.1
```
Apply the RBAC related yaml files ( this includes a service account, a role and a rolebinding )
```
kubectl apply -f yaml/rbac
```
Test by deploying a pod
```
kubectl run --image=nginx my-nginx8
```
Or by provisioning a deploymnet
```
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1
```
The labels should get set on the newly created pods or any edited pod (try remove or change the labels)  

### To do
Handle error on naked pod deletion ( and any permananet pod removal ); need to look at the logic loop.   
Improve on the deployment ( security context, etc).   
