#!/usr/bin/env python3
#
# TakeOver - Subdomain TakeOver Finder
# Coded by Momo Outaadi (m4ll0k)

from __future__ import print_function

import re
import os
import sys
import time
import getopt
import urllib3
import urllib.parse
import requests

# -- common services
# -- Add new services
# -- {'NAME SERVICE' : {'code':'[300-499]','error':'ERROR HERE'}}
# -- https://github.com/EdOverflow/can-i-take-over-xyz

services = {
        'AWS/S3'          : {'code':'[300-499]','error':r'The specified bucket does not exist'},
        'BitBucket'       : {'code':'[300-499]','error':r'Repository not found'},
        'Github'          : {'code':'[300-499]','error':r'There isn\'t a Github Pages site here\.'},
        'Shopify'         : {'code':'[300-499]','error':r'Sorry\, this shop is currently unavailable\.'},
        'Fastly'          : {'code':'[300-499]','error':r'Fastly error\: unknown domain\:'},

        'FeedPress'       : {'code':'[300-499]','error':r'The feed has not been found\.'},
        'Ghost'           : {'code':'[300-499]','error':r'The thing you were looking for is no longer here\, or never was'},
        'Heroku'          : {'code':'[300-499]','error':r'no-such-app.html|<title>no such app</title>|herokucdn.com/error-pages/no-such-app.html'},
        'Pantheon'        : {'code':'[300-499]','error':r'The gods are wise, but do not know of the site which you seek.'},
        'Tumbler'         : {'code':'[300-499]','error':r'Whatever you were looking for doesn\'t currently exist at this address.'},
        'Wordpress'       : {'code':'[300-499]','error':r'Do you want to register'},

        'TeamWork'        : {'code':'[300-499]','error':r'Oops - We didn\'t find your site.'},
        'Helpjuice'       : {'code':'[300-499]','error':r'We could not find what you\'re looking for.'},
        'Helpscout'       : {'code':'[300-499]','error':r'No settings were found for this company:'},
        'Cargo'           : {'code':'[300-499]','error':r'<title>404 &mdash; File not found</title>'},
        'StatusPage'      : {'code':'[300-499]','error':r'You are being <a href=\"https://www.statuspage.io\">redirected'},
        'Uservoice'       : {'code':'[300-499]','error':r'This UserVoice subdomain is currently available!'},
        'Surge'           : {'code':'[300-499]','error':r'project not found'},
        'Intercom'        : {'code':'[300-499]','error':r'This page is reserved for artistic dogs\.|Uh oh\. That page doesn\'t exist</h1>'},

        'Webflow'         : {'code':'[300-499]','error':r'<p class=\"description\">The page you are looking for doesn\'t exist or has been moved.</p>'},
        'Kajabi'          : {'code':'[300-499]','error':r'<h1>The page you were looking for doesn\'t exist.</h1>'},
        'Thinkific'       : {'code':'[300-499]','error':r'You may have mistyped the address or the page may have moved.'},
        'Tave'            : {'code':'[300-499]','error':r'<h1>Error 404: Page Not Found</h1>'},

        'Wishpond'        : {'code':'[300-499]','error':r'<h1>https://www.wishpond.com/404?campaign=true'},
        'Aftership'       : {'code':'[300-499]','error':r'Oops.</h2><p class=\"text-muted text-tight\">The page you\'re looking for doesn\'t exist.'},
        'Aha'             : {'code':'[300-499]','error':r'There is no portal here \.\.\. sending you back to Aha!'},
        'Tictail'         : {'code':'[300-499]','error':r'to target URL: <a href=\"https://tictail.com|Start selling on Tictail.'},
        'Brightcove'      : {'code':'[300-499]','error':r'<p class=\"bc-gallery-error-code\">Error Code: 404</p>'},
        'Bigcartel'       : {'code':'[300-499]','error':r'<h1>Oops! We couldn&#8217;t find that page.</h1>'},
        'ActiveCampaign'  : {'code':'[300-499]','error':r'alt=\"LIGHTTPD - fly light.\"'},

        'Campaignmonitor' : {'code':'[300-499]','error':r'Double check the URL or <a href=\"mailto:help@createsend.com'},
        'Acquia'          : {'code':'[300-499]','error':r'The site you are looking for could not be found.|If you are an Acquia Cloud customer and expect to see your site at this address'},
        'Proposify'       : {'code':'[300-499]','error':r'If you need immediate assistance, please contact <a href=\"mailto:support@proposify.biz'},
        'Simplebooklet'   : {'code':'[300-499]','error':r'We can\'t find this <a href=\"https://simplebooklet.com'},
        'GetResponse'     : {'code':'[300-499]','error':r'With GetResponse Landing Pages, lead generation has never been easier'},
        'Vend'            : {'code':'[300-499]','error':r'Looks like you\'ve traveled too far into cyberspace.'},
        'Jetbrains'       : {'code':'[300-499]','error':r'is not a registered InCloud YouTrack.'},

        'Smartling'       : {'code':'[300-499]','error':r'Domain is not configured'},
        'Pingdom'         : {'code':'[300-499]','error':r'pingdom'},
        'Tilda'           : {'code':'[300-499]','error':r'Domain has been assigned'},
        'Surveygizmo'     : {'code':'[300-499]','error':r'data-html-name'},
        'Mashery'         : {'code':'[300-499]','error':r'Unrecognized domain <strong>'},

}

# -- colors 
r ='\033[1;31m'
g ='\033[1;32m'
y ='\033[1;33m'
b ='\033[1;34m'
r_='\033[0;31m'
g_='\033[0;32m'
y_='\033[0;33m'
b_='\033[0;34m'
e_='\033[0m'


# -- print
def plus(string):
        print(f"{g}[+]{e_} {g_}{string}{e_}")


def warn(string):
        print(f"{r}[!]{e_} {r_}{string}{e_}")


def info(string):
        print(f"{y}[i]{e_} {y_}{string}{e_}")


def request(url,proxy,timeout):
        headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        try:
                req = requests.packages.urllib3.disable_warnings(
                        urllib3.exceptions.InsecureRequestWarning
                        )
                if proxy:
                        req = requests.get(url=url,headers=headers,proxies=proxy,timeout=timeout)
                else:
                        req = requests.get(url=url,headers=headers,timeout=timeout)
                return req.status_code,req.content
        except Exception as e:
                pass
        return None,None


def checker(status,content):
        code = ""
        error = ""
        # --
        for service in services:
                values = services[service]
                for value in values:
                        opt = services[service][value]
                        if value == 'error':
                                error = opt
                        if value == 'code':
                                code = opt
                # ---
                if re.search(code,str(status),re.I) and re.search(error,content.decode(),re.I):
                        return service,error
        return None,None


def banner():
        print("\n   /~\\")
        print("  C oo   ---------------")
        print(" _( ^)  |T|A|K|E|O|V|E|R|")
        print("/   ~\\  ----------------")
        print("#> by Momo Outaadi (m4ll0k)")
        print("#> http://github.com/m4ll0k")
        print("-"*40)


def help():
        banner()
        print("Usage: takeover.py [OPTIONS]\n")
        print("\t-s --sub-domain\t\tSet sub-domain URL (e.g: admin.example.com)")
        print("\t-l --sub-domain-list\tScan multiple targets in a text file")
        print("\t-p --set-proxy\t\tUse a proxy to connect to the target URL")
        print("\t-o --set-output\t\tUse this setting for save a file")
        print("\t-t --set-timeout\tSet a request timeout. Default value is 20 seconds\n")
        print("Example:")
        print(f"\t{sys.argv[0]} --sub-domain test.test.com")
        print(f"\t{sys.argv[0]} --sub-domain-list sub.txt --set-output sub_output.txt")
        print(f"\t{sys.argv[0]} --sub-domain-list sub.txt --set-output sub_output.txt --set-timeout 3\n")
        sys.exit()


def sett_proxy(proxy):
        info(f"Setting proxy.. {proxy}")
        return {
        'http':proxy,
        'https':proxy,
        'ftp':proxy
        }


def check_path(path):
        try:
                if os.path.exists(path):
                        return path
        except Exception as e:
                warn(f'{e.message}')
                sys.exit()


def readfile(path):
        info(f'Read wordlist.. {path}')
        try:
                return [l.strip() for l in open(check_path(path),'r')]
        except Exception as e:
                warn(f'{e}')
                sys.exit()


def check_url(url):
        o = urllib.parse.urlsplit(url)
        if o.scheme not in ['http','https','']:
                warn(f'Scheme {o.scheme} not supported!!')
                sys.exit()
        if o.netloc == '':
                return 'http://'+o.path
        elif o.netloc:
                return o.scheme + '://' + o.netloc
        else:
                return 'http://' + o.netloc


def main():
        # ---
        set_proxy = None
        set_output = None
        sub_domain = None
        sub_domain_list = None
        set_timeout = 20
        # ---
        if len(sys.argv) < 2: help()
        try:
                opts,args = getopt.getopt(sys.argv[1:],'s:l:p:o:t:',
                        ['sub-domain=','sub-domain-list=','set-proxy=','set-output=','set-timeout='])
        except Exception as e:
                warn(f"{e.message}")
                time.sleep(1)
                help()
        banner()
        for o,a in opts:
                if o in ('-s','--sub-domain'):sub_domain = check_url(a)
                if o in ('-l','--sub-domain-list'):sub_domain_list = readfile(a)
                if o in ('-p','--set-proxy'):set_proxy = sett_proxy(a)
                if o in ('-o','--set-output'):set_output = a
                if o in ('-t','--set-timeout'):set_timeout = int(a)
        # ---
        if set_output:
                file = open(set_output,"w+")
                file.write(f'Output File\r\n{"-"*50}\r\n')
        if sub_domain:
                plus('Starting scanning...')
                info(f'Target url... {sub_domain}')
                status,content = request(sub_domain,set_proxy,set_timeout)
                service,error = checker(status,content)
                if service and error:
                        plus(f'Found service: {service}')
                        plus('A potential TAKEOVER vulnerability found!')
        elif sub_domain_list:
                plus('Starting scanning...')
                for sub_domain in sub_domain_list:
                        sub_domain = check_url(sub_domain)
                        info(f'Target url... {sub_domain}')
                        status,content = request(sub_domain,set_proxy,set_timeout)
                        service,error = checker(status,content)
                        if service and error:
                                plus(f'Found service: {service}')
                                plus('A potential TAKEOVER vulnerability found!')
                                if set_output:
                                        file.write(f'HOST    : {sub_domain}\r\n')
                                        file.write(f'SERVICE : {service}\r\n')
                                        file.write(f'ERRORS  : {error}\r\n')
        else:help()
        if set_output:
                file.close()
try:
        main()
except KeyboardInterrupt as e:
        warn('Interrupt by user!')
        sys.exit()
