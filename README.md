# CloudNotes Workload Rescue

CloudNotes fails its local Kubernetes release checks. Investigate and repair three manifest faults. Your instructor supplies the assessment and a prepared local cluster.

## Student workflow

Fork this repository, clone your personal fork, and create `fix/workload-rescue`. Use a free editor and the prepared `kubectl` environment. Work only in namespace `cloudnotes-rescue` unless your instructor supplies another name.

**Never push fixes to `kalviumcommunity/cloudnotes-workload-rescue` or open a pull request against it.** Commit/push only to your personal fork after checking `git remote -v`. Submit one PDF through the assessment portal. No PR is required anywhere.

Repair only `k8s/deployment.yaml` and `k8s/service.yaml`. Three planted faults exist across these two files. Application, image, ConfigMap, Secret, PVC, client Pod, probes, resource settings, and helper scripts are supplied; do not modify or bypass them. Do not add optional references, literal credentials, extra volumes, or direct Pod requests as a replacement for required Service tests.

## Application contract

- Image: `cloudnotes-workload:1.0.0`, preloaded into cluster nodes. No image build/download is part of the timed work.
- Application listens on all interfaces at port 8080. Intended Service is `cloudnotes`, ClusterIP, port 80.
- Required environment: `APP_ENV`, `DATA_DIR`, `API_TOKEN`. Runtime configuration comes from supplied Kubernetes objects.
- Data written inside the directory configured by `DATA_DIR` must survive application Pod replacement using existing `cloudnotes-data` PVC. One replica and `Recreate` strategy are intentional for this small SQLite exercise.
- `GET /health`: HTTP 200 with status ok.
- `GET /info`: runtime mode and storage directory (no credential value).
- `POST /notes`: HTTP 201 with saved note; `GET /notes`: saved notes. Both require the injected practice token.
- Client Pod already has the intended authentication configuration. Request helper runs inside it, uses Service DNS, and never prints token values.

## Command reference

```bash
kubectl -n cloudnotes-rescue get pods,pvc,svc
kubectl -n cloudnotes-rescue describe pod <pod-name>
kubectl -n cloudnotes-rescue get events --sort-by=.lastTimestamp
kubectl -n cloudnotes-rescue logs deployment/cloudnotes
kubectl -n cloudnotes-rescue describe secret cloudnotes-access
kubectl -n cloudnotes-rescue get configmap cloudnotes-config -o yaml
kubectl -n cloudnotes-rescue apply -f k8s/deployment.yaml
kubectl -n cloudnotes-rescue apply -f k8s/service.yaml
kubectl -n cloudnotes-rescue rollout status deployment/cloudnotes --timeout=90s
kubectl -n cloudnotes-rescue get pods -l app=cloudnotes -o wide
kubectl -n cloudnotes-rescue get endpointslices -l kubernetes.io/service-name=cloudnotes -o yaml
bash scripts/request.sh GET /health
bash scripts/request.sh GET /info
bash scripts/request.sh POST /notes 'my-rescue-note'
bash scripts/request.sh GET /notes
kubectl -n cloudnotes-rescue get pods -l app=cloudnotes -o custom-columns=NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready
kubectl -n cloudnotes-rescue delete pod -l app=cloudnotes
kubectl -n cloudnotes-rescue rollout status deployment/cloudnotes --timeout=90s
```

Quote custom-column arguments containing brackets if your shell expands them. A startup configuration error may produce no application logs because the container never started; use events/describe rather than claiming nonexistent previous logs. Pod Running does not mean Ready, and an endpoint alone does not prove successful HTTP routing.

Do not expose Secret values: use `describe secret` for key names, not `get secret -o yaml`, decoded values, environment dumps, or authorization headers. Do not delete PVC, Secret, namespace, or unrelated workloads. Save only disposable practice notes.

## Instructor setup — outside timer

Free local Kubernetes (kind, minikube, or k3s), kubectl, Docker Engine for image preparation, Python 3 for setup, and a free IDE/PDF exporter are sufficient. No cloud, payment, registry login, or hosted CI/CD. Docker Desktop optional only if free-use licence applies. Prepare a local context, namespace per student, working default dynamic storage provisioner, enough disk space, and preloaded image on all schedulable nodes. Namespace customization uses `NAMESPACE=...` before helper commands and `-n ...` on kubectl.

```bash
docker build -t cloudnotes-workload:1.0.0 .
# Example image loading; select the command matching your prepared local cluster:
# kind load docker-image cloudnotes-workload:1.0.0 --name <cluster-name>
# minikube image load cloudnotes-workload:1.0.0
bash scripts/setup.sh
```

Image/base retrieval may initially need free internet downloads; prepared assessment does not need external services. Setup must show client Ready and PVC Bound; application may show its intended startup failure. Do not pre-solve manifests for students. Do not run setup again during student work, because it reapplies starter files. Re-check cluster/storage/image compatibility before each exam. Instructor handles cleanup after evidence is saved; no destructive namespace deletion is required of students.
