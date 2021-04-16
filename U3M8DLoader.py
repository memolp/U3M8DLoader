# -*- coding:utf-8 -*-

import u3m8


# cctv6
u3m8_data = u3m8.from_url("http://ivi.bupt.edu.cn/hls/cctv6hd.m3u8")
if u3m8_data:
    u3m8.download(u3m8_data.get_ts_urls(), root="http://ivi.bupt.edu.cn/hls/")

