# ---------------------
from bs4 import BeautifulSoup as bs
import requests
import urllib3
import urllib
from urllib.parse import unquote
import re
import os
import sys
import json
import time
from colorama import Fore, init
from pprint import pprint
from datetime import datetime
import uuid
import threading
# ----------------------
from dhooks import Webhook
from dhooks import Webhook, Embed
# ---------------------
init()
init(autoreset=True)
urllib3.disable_warnings()
os.system('cls' if os.name == 'nt' else 'clear')
# ---------------------

# MUST HAVE PRIME
# MUST HAVE ONE CLICK
# MUST SELECT "Keep me signed in"
# MUST USE AGED ACCOUNT
# ====================================
# MUST HAVE THESE FOR BEST SUCCESS


class main:
    def __init__(self, sku, code, account) -> None:
        self.account = account
        f = open(f'./appdata/cookies.json')
        self.cookies = json.load(f)
        self.sku = sku
        self.code = code

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Making Session')
        self.session = requests.Session()

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Fetching Cookies')
        for cookie in self.cookies:
            self.session.cookies.set(
                self.cookies[cookie]['name'], self.cookies[cookie]['value'])
        self.productPage()

    def productPage(self):
        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Getting Product Page')
        self.asin_page = self.session.get(
            'https://smile.amazon.com/dp/' + str(self.sku),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}
        )

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Getting Product Price:',  end=" ")
        soup = bs(self.asin_page.text, "lxml")
        self.og_price = soup.find(
            'span', {'class': 'a-offscreen'}).getText().strip()
        print(f'{self.og_price}')

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Getting Session ID:',  end=" ")
        self.session_id = self.asin_page.text.split(
            'id="session-id" name="session-id" value="')[1].split('"')[0]
        print(f'{self.session_id}')

        try:
            print(Fore.WHITE + f"Session: {self.account} || " +
                  Fore.YELLOW + '[*] Getting Offer Id:',  end=" ")
            self.offerListingId = re.search(
                "&offerListingId=(.*?)\&", self.asin_page.text).group(1)
            print(f'{self.offerListingId}')
            self.promoPage()  # if we find an OID, it means the the listing have an UNREDEEMED coupon

        except Exception as e:  # This error will occur when the coupon is redeemed OR there is no coupon
            print(Fore.RED + '[-] Coupon Clipped')
            self.addToCart()
            pass

    def promoPage(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'accept-encoding': 'gzip, deflate, br',
        }

        self.productPage = self.session.get(
            f'https://smile.amazon.com/gp/aod/ajax/ref=auto_load_aod?asin={self.sku}', headers=headers)

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Getting Promo Object')
        self.promoObj = {
            'promoId': re.search("&promotionId=(.*?)\&", self.productPage.text).group(1),
            'merchantID': re.search(";seller=(.*?)\&", self.productPage.text).group(1),
            'sku': re.search("&sku=(.*?)\&", self.productPage.text).group(1),
            'anti-csrftoken-a2z': re.search("&anti-csrftoken-a2z=(.*?)\'", self.productPage.text).group(1)
        }
        for i in self.promoObj:
            print(Fore.WHITE + f"Session: {self.account} || " + Fore.YELLOW +
                  f'[*] {i.title()}: ' + Fore.WHITE + f'{self.promoObj[i]}')
        self.clipCoupon()

    # ---------------------

    def clipCoupon(self):
        headers = {
            'anti-csrftoken-a2z': unquote(self.promoObj['anti-csrftoken-a2z']),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'x-requested-with': 'XMLHttpRequest',
            'referer': f'https://www.amazon.com/dp/{self.sku}'
        }
        params = {
            'promotionId': self.promoObj['promoId'],
            'asin': self.sku,
            'offerListingId': self.offerListingId,
            'sku': self.promoObj['sku'],
            'anti-csrftoken-a2z': unquote(self.promoObj['anti-csrftoken-a2z']),
            'source': 'dp_cxcw'
        }
        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Clipping Coupon')
        promoUrl = f'https://www.amazon.com/promotion/redeem/?{urllib.parse.urlencode(params)}'
        while True:
            clipCoupon = self.session.get(promoUrl, headers=headers)
            if 'SUCCESS' in clipCoupon.text:
                print(
                    Fore.WHITE + f"Session: {self.account} || " + Fore.GREEN + '[+] Coupon Clipped')
            break
        self.addToCart()

    def addToCart(self):
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'x-amz-checkout-entry-referer-url': 'https://smile.amazon.com/dp/' + self.sku,
            'x-amz-turbo-checkout-dp-url': 'https://smile.amazon.com/dp/' + self.sku,
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'x-amz-support-custom-signin': '1',
            'x-amz-checkout-csrf-token': self.session_id,
            'Origin': 'https://smile.amazon.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://smile.amazon.com/dp/' + self.sku
        }

        payload = {
            'addressID': 'nmqgnomolpkq',
            'isAsync': '1',
            'quantity.1': '1',
        }

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[+] Adding To Cart')
        while True:
            try:
                self.session_atc = self.session.post(
                    f'https://smile.amazon.com/checkout/turbo-initiate?ref_=dp_start-bbf_1_glance_buyNow_2-1&referrer=detail&pipelineType=turbo&clientId=retailwebsite&weblab=RCX_CHECKOUT_TURBO_DESKTOP_PRIME_87783&temporaryAddToCart=1&asin.1={self.sku}',
                    data=payload, headers=headers
                )
                break

            except self.session_atc.status_code != 200:
                print(Fore.WHITE + f"Session: {self.account} || " +
                      Fore.RED + '[-] Error Adding To Cart', end=" ")
                time.sleep(1)
                print(
                    Fore.WHITE + f"Session: {self.account} || " + Fore.RED + '[-] Retrying', end=" ")
        print(
            Fore.WHITE + f"Session: {self.account} || " + Fore.GREEN + '[+] Added to Cart')

        checkout_url_tuple = re.search(
            '\/(.*)shipmentId=(.*)\d', self.session_atc.text).group(0)
        self.checkout_url_str = ''.join(checkout_url_tuple)

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Getting PID:',  end=" ")
        self.pid = re.search(
            "pid=(.*?)\&", str(self.checkout_url_str)).group(1)
        print(f'{self.pid}')

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Getting Anti CSRF:',  end=" ")
        self.AntiCSRF = re.search(
            "anti-csrftoken-a2z'.value='(.*?)\'", str(self.session_atc.text)).group(1)
        print(f'{self.AntiCSRF}')  # use this to checkout

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Getting SID:',  end=" ")
        self.sid = re.search(
            "'CacheDetection.RequestID': \"(.*?)\",", self.session_atc.text).group(1)
        print(f'{self.sid}')

        if not self.code:  # check if there is no code
            print(
                Fore.WHITE + f"Session: {self.account} || " + Fore.RED + '[-] No Code Found')
            self.checkSummary()
        else:
            self.claimCode()

    def claimCode(self):
        if '' in self.code:
            return
        else:
            headers = {
                'Connection': 'keep-alive',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                'x-amz-checkout-entry-referer-url': 'https://smile.amazon.com/dp/' + self.sku,
                'anti-csrftoken-a2z': self.AntiCSRF,
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
                'x-amz-checkout-csrf-token': self.session_id,
                'Origin': 'https://smile.amazon.com',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://smile.amazon.com/checkout/pay?pid=' + self.pid + '&pipelineType=turbo&clientId=retailwebsite&temporaryAddToCart=1&hostPage=detail&weblab=RCX_CHECKOUT_TURBO_DESKTOP_PRIME_87783'
            }

            payload = {
                'claimcode': self.code,
                'isClientTimeBased': '1'
            }

            print(
                Fore.WHITE + f"Session: {self.account} || " + Fore.YELLOW + '[*] Applying Code')
            claimurl = f'https://smile.amazon.com/checkout/pay/add-gc-promo?ref_=chk_pay_addGcPromo&referrer=pay&temporaryAddToCart=1&hostPage=detail&weblab=RCX_CHECKOUT_TURBO_DESKTOP_PRIME_87783&_srcRID={self.sid}&clientId=retailwebsite&pipelineType=turbo&pid={self.pid}'
            claim = self.session.post(
                claimurl, headers=headers, data=payload, allow_redirects=True)
            with open("./html/claimCode.html", "w", encoding='utf-8') as f:
                f.write(claim.text)

            self.checkSummary()

    def checkSummary(self):
        headers = {
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
        }

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.GREEN + '[+] Reviewing Summary')
        summaryUrl = f'https://www.amazon.com/checkout/ordersummary?ref_=chk_spc_select__summary&referrer=spc&pid={self.pid}&pipelineType=turbo&clientId=retailwebsite&temporaryAddToCart=1&hostPage=detail&weblab=RCX_CHECKOUT_TURBO_DESKTOP_PRIME_87783'
        summary = self.session.get(summaryUrl, headers=headers)

        soup = bs(summary.text, "lxml")
        self.finalPrice = soup.find(
            'td', {'class': 'a-color-price a-text-right a-align-bottom a-text-bold a-nowrap'}).getText().strip()
        print(Fore.WHITE + f"Session: {self.account} || " + Fore.YELLOW +
              '[+] Order Total: ' + Fore.WHITE + f'{self.finalPrice}')

        self.checkout()

    def checkout(self):
        print(Fore.WHITE +
              f"Session: {self.account} || " + Fore.GREEN + '[+] Checking Out')
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'anti-csrftoken-a2z': self.AntiCSRF
        }

        payload = {
            'x-amz-checkout-csrf-token': self.session_id,
            'ref_': 'chk_summary_placeOrder',
            'referrer': 'summary',
            'pid': self.pid,
            'pipelineType': 'turbo',
            'clientId': 'retailwebsite',
            'temporaryAddToCart': 1,
            'hostPage': 'detail',
            'weblab': 'RCX_CHECKOUT_TURBO_DESKTOP_PRIME_87783',
            'isClientTimeBased': 1
        }

        params = {
            'ref_': 'chk_summary_placeOrder',
            '_srcRID': self.sid,
            'clientId': 'retailwebsite',
            'pipelineType': 'turbo',
            'pid': self.pid
        }

        print(Fore.WHITE + f"Session: {self.account} || " +
              Fore.YELLOW + '[*] Status: ', end=' ')
        checkoutUrl = f'https://www.amazon.com/checkout/spc/place-order?{urllib.parse.urlencode(params)}'
        checkout = self.session.post(
            checkoutUrl, data=payload, headers=headers)
        if checkout.status_code == 200:
            print(Fore.GREEN + 'Success')
            self.sendWebhook(self.sku, self.finalPrice)
        else:
            print(f'something went wrong {checkout.text}')

    def sendWebhook(self, sku, finalPrice):
        soup = bs(self.asin_page.text, "lxml")
        title = soup.find('span', {'id': 'productTitle'}).getText().strip()
        a = soup.find('div', {'id': 'imgTagWrapperId'})
        if a.img:
            img = a.img['src']
        price = soup.find('span', {'class': 'a-offscreen'}).getText().strip()
        product_url = f'https://www.amazon.com/dp/{sku}?tag=Chili'

        f = open('./appdata/config.json')
        data = json.load(f)
        url = data['webhook']
        hook = Webhook(url)

        embed = Embed(
            color=0x8AFF8A,
            timestamp='now'
        )
        embed.set_title(
            title='🎉Successful Checkout')
        embed.set_thumbnail(img)
        embed.add_field(
            name='Item', value=f'[{title}]({product_url})', inline=False)
        embed.add_field(name='Original Price', value=f'{price}', inline=False)
        embed.add_field(name='Check Out Price',
                        value=f'{finalPrice}', inline=False)
        embed.add_field(
            name='Account', value=f'||{self.account.replace(".json", "")}||', inline=False)
        embed.set_footer(
            text='Made by #chili9999')

        print(Fore.GREEN + '[+] Sending Webhook')
        hook.send(embed=embed)


def callback(account: str):
    sku = input('Put in a product asin:')
    promo = input('Put in a product promo code, if none, press Enter:')

    threads = []
    threads.append(threading.Thread(
        target=main, args=[sku, promo, account]))

    for thread in threads:
        thread.start()
        time.sleep(.1)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    f = open(f'./appdata/config.json')
    account = json.load(f)['account']
    callback(account)
    # asin, promo code, email
    # if you don't have a promocode, leave it as ''
