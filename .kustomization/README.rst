# Kustomization

Refer to the [main](https://github.com/rena2damas/microservices.git#kustomization) repository.

## Directory structure

Refer to the [main](https://github.com/rena2damas/microservices.git#directory-structure) repository.

## Secret management

Refer to the [main](https://github.com/rena2damas/microservices.git#secret-management) repository.

Sealing secrets would be done this way for this case:

```bash
(
ENV="dev"
basedir="$(pwd)/.kustomization"
cd "${basedir}/overlays/${ENV}/"
kustomize build secrets/ | yq e 'select(.metadata.name=="'portal-service'")' - | kubeseal > secrets/sealed/base.yaml 
kustomize build secrets/ | yq e 'select(.metadata.name=="'portal-service-postgres'")' - | kubeseal > secrets/sealed/postgres.yaml 
)
```

## Usage

Refer to the [main](https://github.com/rena2damas/microservices.git#usage) repository.

After this stage, the pods should be running (or about to). An example output with default settings:

```bash
$ kubctl get pods
NAME                        READY   STATUS      RESTARTS    ...
portal-service-XXX-XXX      1/1     Running     0           ...
portal-service-XXX-XXX      1/1     Running     0           ...
```
