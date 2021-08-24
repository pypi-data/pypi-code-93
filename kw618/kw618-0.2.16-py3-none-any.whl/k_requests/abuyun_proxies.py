class AbuyunProxies():

    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H9E6383C4ONW1AOD"
    proxyPass = "11844987BD73DCAD"

    # proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    #   "host" : proxyHost,
    #   "port" : proxyPort,
    #   "user" : proxyUser,
    #   "pass" : proxyPass,
    # }

    proxyMeta = f"http://{proxyUser}:{proxyPass}@{proxyHost}:{proxyPort}"

    proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
    }
