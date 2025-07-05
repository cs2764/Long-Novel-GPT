# 以下为多平台构建方式----------------------------------------------------------------------------------
export DOCKER_BUILDKIT=1

docker buildx rm mybuilder 2>/dev/null || true
# 这里ip为docker0的ip，通过ifconfig查看，配置了本地代理，不要的可以删除
docker buildx create --use --name mybuilder --driver-opt env.http_proxy="http://172.17.0.1:7890" --driver-opt env.https_proxy="http://172.17.0.1:7890"
docker buildx inspect mybuilder --bootstrap
docker buildx build --platform linux/amd64,linux/arm64 -t maoxiaoyuz/long-novel-gpt:latest . --push

# 如果build出现错误：dial tcp 172.17.0.1:7890: connect: connection refused，则需要修改clash配置文件，使其监听0.0.0.0:7890
# 具体来说，在clash配置文件中添加以下内容：
# allow-lan: true
# bind-address: 0.0.0.0