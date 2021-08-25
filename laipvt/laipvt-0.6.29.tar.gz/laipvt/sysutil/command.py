## gen certs command
gen_server_secure_key_cmd = "openssl genrsa -des3 -passout pass:laiye -out {} 2048"
gen_server_key_cmd = "openssl rsa -in {} -passin pass:laiye -out {}"
gen_server_csr_cmd = "openssl req -new -key {} -out {} -subj '/C=CN/ST=BeiJing/L=BeiJing/O=LaiYe Security/OU=IT Department/CN=*'"
gen_ca_crt_cmd = "openssl req -new -x509 -key {} -out {} -days 3650 -subj '/C=CN/ST=BeiJing/L=BeiJing/O=LaiYe Security/OU=IT Department/CN=*'"
gen_server_crt_cmd = "openssl x509 -req -days 3650 -in {} -CA {} -CAkey {} -CAcreateserial -out {}"

## kubenetes command
BASH_RUN = "/bin/bash {}"
CP_KUBEADM = "\cp -f {}/kubeadm /usr/bin/kubeadm"
KUBE_INIT = "kubeadm init --config {}"
CREATE_KUBE_DIR = "mkdir ~/.kube"
CP_KUBE_CONFIG = "\cp /etc/kubernetes/admin.conf ~/.kube/config"
KUBECTL_COMPLETION = "echo 'source <(kubectl completion bash)' >> ~/.bashrc"
KUBECTL_APPLY = "kubectl apply -f {}"
KUBEADM_TOKEN_CREATE = "kubeadm token create --print-join-command --config {}"
TAR_KUBE_CRETS = """tar -C /etc/kubernetes -zcvf {} \
        admin.conf pki/ca.crt pki/ca.key pki/sa.key pki/sa.pub pki/front-proxy-ca.crt \
        pki/front-proxy-ca.key pki/etcd/ca.crt pki/etcd/ca.key"""
UNTAR_KUBE_CRETS = "tar -zxvf {} -C /etc/kubernetes/"
ADD_MASTER_SUFFIX = "{} --control-plane --node-name {}"
TAINT_MASTER = "kubectl taint nodes {} node-role.kubernetes.io/master-"
HELM_PATH = "/usr/bin/helm"
TILLER_PATH = "/usr/bin/tiller"
TILLER_SERVICE_PATH = "/usr/lib/systemd/system/tiller.service"
CHMOD_EXECUTE = "chmod +x {}"
SYSTEMCTL_DAEMON_RELOAD  = "systemctl daemon-reload"
SYSTEMCTL_START = "systemctl start {}"
SYSTEMCTL_ENABLE = "systemctl enable {}"
ISTIOCTL_PATH = "/usr/bin/istioctl"
ISTIOCTL_INSTALL = "istioctl install -f {}"
CHECK_ISTIO = "kubectl get crds | grep 'istio.io' | wc -l"
GET_POD_INFO = "kubectl -n mid get pod |grep {}"
RESTART_DEPLOYMENT = "kubectl -n {} rollout restart deployment {}"
RESTART_DEPLOYMENT_ALL = "kubectl -n {} rollout restart deployment"
CREATE_NS = "kubectl create ns {}"
ISTIO_INJECTION_NS = "kubectl label namespace {} istio-injection=enabled"

# harbor command
TARGZ_DECOMPRESSION = "tar -zxmf {} -C {}"
CHMOD_USER_GROUP = "chown -R {}:{} {} {}"
ENABLE_HARBOR_SERVICE = "systemctl enable harbor.service"

# middleware command
RM = "rm -fr {}"
###
CREATE_DB = "create database If Not Exists {db_name} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci"

MKDIR_DIR = "mkdir -p {}"
CHMOD_777 = "chmod -R 777 {}"

HELM_LIST = "helm --host=localhost:44134 list --all --chart-name {}|grep -q '{}'"

HELM_INSTALL = """helm --host=localhost:44134 install --name={process} --set replicaCount={replicas} \
                    --set image.hub={registry_hub} --set image.name={image_name} --set image.tag={image_tag} \
                    --set pvtWorkDir={pvt_work_dir} \
                    --set global.LM_LOG_DEBUG=1 \
                    --set global.LM_ETCD_ENDPOINT="{etcd_endpoint}" \
                    --set global.LM_APPLY_LICENSE_PATH='/home/works/program/data/license.lcs' \
                    {file_path}"""

INIT_IDENTITY_USER = "docker exec ids-server dotnet /opt/tool/idsadmin.dll -a add -u admin -p 123456"

HELM_INSTALL_TF_SERVICE = """helm --host=localhost:44134 install --name={process} --set replicaCount={replicas} \
            --set image.hub={registry_hub} --set image.name={image_name} --set image.tag={image_tag} \
            --set pvtWorkDir={pvt_work_dir} \
            --set global.LM_LOG_DEBUG=1 \
            --set global.LM_ETCD_ENDPOINT="{etcd_endpoint}" \
            --set global.LM_APPLY_LICENSE_PATH='/home/works/program/data/license.lcs' \
            {file_path}"""

HELM_INSTALL_COMMANDER = """helm --host=localhost:44134 install --name={process} --set replicaCount={replicas} \
                    --set image.hub={registry_hub} --set image.name={image_name} --set image.tag={image_tag} \
                    --set pvtWorkDir={pvt_work_dir} \
                    --set config.server="{config_server}" --set config.passwd={config_server_passwd} \
                    --set mysql.host={mysql_host} --set mysql.port={mysql_port} --set mysql.user={mysql_user} \
                    --set mysql.password={mysql_password} --set mysql.database={mysql_database} --set mysql.charset={mysql_charset} \
                    --set oidc.authority={oidc_authority} --set oidc.secret={oidc_secret} \
                    --set global.LM_CLIENT_SERVICE_ID=200001 --set global.LM_CLIENT_LICENSE_MANAGER_ADDR=dns:///license-manager.mid:19080 \
                    {file_path}"""

RESTART_LICSERVER = "systemctl restart licServer"

COMMANDER_UPGRADE_INSTALL = """helm --host=localhost:44134 upgrade --install --force --set replicaCount={replicas} \
                    --set image.hub={registry_hub} --set image.name={image_name} --set image.tag={image_tag} \
                    --set pvtWorkDir={pvt_work_dir} \
                    --set config.server="{config_server}" --set config.passwd={config_server_passwd} \
                    --set mysql.host={mysql_host} --set mysql.port={mysql_port} --set mysql.user={mysql_user} \
                    --set mysql.password={mysql_password} --set mysql.database={mysql_database} --set mysql.charset={mysql_charset} \
                    --set oidc.authority={oidc_authority} --set oidc.secret={oidc_secret} \
                    --set global.LM_CLIENT_SERVICE_ID=200001 --set global.LM_CLIENT_LICENSE_MANAGER_ADDR=dns:///license-manager.mid:19080 \
                    {process} {file_path}"""

HELM_UPGRADE_INSTALL = """helm --host=localhost:44134 upgrade --install --set replicaCount={replicas} \
                    --set image.hub={registry_hub} --set image.name={image_name} --set image.tag={image_tag} \
                    --set pvtWorkDir={pvt_work_dir} \
                    --set global.LM_LOG_DEBUG=1 \
                    --set global.LM_ETCD_ENDPOINT="{etcd_endpoint}" \
                    --set global.LM_APPLY_LICENSE_PATH='/home/works/program/data/license.lcs' \
                    {process} {file_path}"""