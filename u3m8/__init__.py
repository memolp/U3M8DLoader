# -*- coding:utf-8 -*-

import os
import requests


class U3M8FormatDef:
    EXT_HEAD_TAG            = "#EXTM3U"                 # M3U8文件必须包含的标签，并且必须在文件的第一行，所有的M3U8文件中必须包含这个标签
    EXT_VERSION_TAG         = "#EXT-X-VERSION"          # M3U8文件的版本，常见的是3（目前最高版本应该是7）。
    EXT_MEDIA_SEQUENCE_TAG  = "#EXT-X-MEDIA-SEQUENCE"   # 该标签指定了媒体文件持续时间的最大值，播放文件列表中的媒体文件在EXTINF标签中定义的持续时间必须小于或者等于该标签指定的持续时间。该标签在播放列表文件中必须出现一次。
    EXT_TARGET_DURATION_TAG = "#EXT-X-TARGETDURATION"   # M3U8直播是的直播切换序列，当播放打开M3U8时，以这个标签的值作为参考，播放对应的序列号的切片。
    EXT_INF_TAG             = "#EXTINF"                 # EXTINF为M3U8列表中每一个分片的duration.在EXTINF标签中，除了duration值，还可以包含可选的描述信息，主要为标注切片信息，使用逗号分隔开。
    EXT_END_LIST_TAG        = "#EXT-X-ENDLIST"          # 若出现EXT-X-ENDLIST标签，则表明M3U8文件不会再产生更多的切片,这个M3U8即为点播M3U8
    EXT_STREAM_INF_TAG      = "#EXT-X-STREAM-INF"       # 主要是出现在多级M3U8文件中时，例如M3U8中包含子M3U8列表，或者主M3U8中包含多码率M3U8时


class U3M8Data:
    """
    #EXTM3U
    #EXT-X-VERSION:3
    #EXT-X-MEDIA-SEQUENCE:35232
    #EXT-X-TARGETDURATION:10
    #EXTINF:10.000,
    0.ts
    #EXTINF:10.000,
    1.ts
    #EXT-X-ENDLIST
    """
    def __init__(self):
        # 全部资源地址
        self._mTsUrls = []
        # 标记这个是不是点播
        self._mIsEndData = False

    def set_completed_media(self, v):
        """ 完整的媒体 """
        self._mIsEndData = v

    def add_ts_url(self, url, check_repeat=False):
        """ 添加Ts，必须保存有序哦 """
        if check_repeat and url in self._mTsUrls:
            return
        self._mTsUrls.append(url)

    def get_ts_urls(self):
        """ 获取全部的ts url """
        return self._mTsUrls

    @staticmethod
    def parse(u3m8_content, u3m8_data=None):
        """ 解析 """
        lines = u3m8_content
        if not isinstance(u3m8_content, (list, tuple)):
            lines = u3m8_content.split("\n")
        size = len(lines)
        if size <= 1:
            return None
        first_line = lines[0]
        # 第一行
        if not first_line.startswith(U3M8FormatDef.EXT_HEAD_TAG):
            return None
        if u3m8_data is None:
            u3m8_data = U3M8Data()
        # 解析格式？ 有空再搞吧
        for i in range(1, size):
            line = lines[i]
            if line.startswith("#"):
                if line.startswith(U3M8FormatDef.EXT_END_LIST_TAG):
                    u3m8_data.set_completed_media(True)
            else:
                u3m8_data.add_ts_url(line.strip(), True)
        return u3m8_data


def from_url(url, data=None, u3m8=None, **kwargs):
    """
    从服务器地址下载
    :param url:
    :param data:
    :param u3m8:
    :param kwargs:
    :return:
    """
    u3m8_response = requests.get(url, data, **kwargs)
    if not u3m8_response.ok:
        raise Exception("url:{0} request error!".format(url))
    u3m8_content = u3m8_response.content

    u3m8 = U3M8Data.parse(u3m8_content.decode("utf-8"), u3m8)
    return u3m8


def from_file(filepath):
    """
    从文件读取
    :param filepath:
    :return:
    """
    if not os.path.exists(filepath):
        raise Exception("file:{0} not exist!".format(filepath))
    with open(filepath, "rb") as pf:
        u3m8_content = pf.read()
        return U3M8Data.parse(u3m8_content)


def download(ts_urls, root="", path="./", comb=False, comb_filename="temp.ts", **kwargs):
    """
    下载文件
    :param ts_urls:
    :param root:
    :param path:
    :param comb:
    :param comb_filename:
    :param kwargs:
    :return:
    """
    total = len(ts_urls)
    for i in range(total):
        url = ts_urls[i]
        if not url.startswith("http"):
            url = os.path.join(root, url)
        base_name = os.path.basename(url)
        print("[DEBUG] download url={0} ({1}/{2})".format(url, i+1, total))
        ts_response = requests.get(url, params=kwargs.get("params", None), **kwargs)
        if not ts_response.ok:
            raise Exception("url:{0} request error!".format(url))
        ts_data = ts_response.content
        if comb:
            with open(comb_filename, "ab+") as pf:
                pf.write(ts_data)
        else:
            save_file = os.path.join(path, base_name)
            with open(save_file, "wb") as pf:
                pf.write(ts_data)

