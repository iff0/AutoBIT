import netron


# 开netron的本地服务
def net_see(path, port):
    netron.start(path, port=port, browse=False)
