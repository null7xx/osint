import os
import sys
import time
import subprocess
import platform
import webbrowser
import socket
import requests
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import tempfile
from urllib.request import urlretrieve
from collections import Counter

# Libraries
import phonenumbers
from phonenumbers import geocoder, carrier, timezone as tz_module, PhoneNumberType

try:
    import whois
except ImportError:
    whois = None

try:
    import cv2
    import face_recognition
    from PIL import Image
except ImportError:
    cv2 = None
    face_recognition = None
    Image = None

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RED = Fore.RED
    GREEN = Fore.GREEN
    BLUE = Fore.BLUE
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    RESET = Style.RESET_ALL
except ImportError:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, color='', delay=0.03):
    for char in text:
        sys.stdout.write(color + char + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_spinner(message, duration=3):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for s in spinner:
            sys.stdout.write(f"\r{BLUE}{message} {s}{RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r" + " " * (len(message) + 10))

def open_url(url):
    system = platform.system()
    if system == "Linux" and "Android" in platform.release():
        subprocess.call(["termux-open-url", url])
    else:
        webbrowser.open(url)

def show_banner():
    clear()
    banner_lines = [
        " ███╗   ██╗██╗   ██╗██╗     ██╗       ███████╗    ██╗  ██╗   ██╗  ██╗",
        " ████╗  ██║██║   ██║██║     ██║       ╚════██║    ╚██╗██╔╝   ╚██╗██╔╝",
        " ██╔██╗ ██║██║   ██║██║     ██║           ██╔╝     ╚███╔╝     ╚███╔╝",
        " ██║╚██╗██║██║   ██║██║     ██║          ██╔╝     ██╔██╗     ██╔██╗",
        " ██║ ╚████║╚██████╔╝███████╗███████╗     █╔╝     ██╔╝ ██    ██╔╝ ██╗",
        " ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝    ╚═╝      ╚═╝  ╚═╝   ╚═╝  ╚═╝"
    ]
    for line in banner_lines:
        type_text(line, BLUE, 0.02)
    print()
    type_text(" Threats Don’t Know Us. Until It’s Too Late.", RED, 0.03)
    print()
    type_text(" NULL7xx Osint Toolkit ", MAGENTA, 0.02)
    type_text(" Created by Null7xx | Cyber Alpha", MAGENTA, 0.01)
    print()

def show_description():
    type_text("OSINT Tools:", CYAN)
    type_text("TikTok • Port Scanner • Phone • IP • Username • Domain • Breach • Image • Admin Finder • Report • Face Recognition", GREEN)
    print()

def show_disclaimer():
    type_text("DISCLAIMER", RED)
    type_text("This tool is for educational and ethical purposes only.", RED)
    type_text("Unauthorized scanning or misuse is strictly prohibited.", RED)
    type_text("You are fully responsible for your actions.", RED)
    print()
COMMON_PORTS_SERVICES = {
    1: "TCPMUX", 5: "RJE", 7: "ECHO", 9: "DISCARD", 13: "DAYTIME", 17: "QOTD", 18: "MSP", 19: "CHARGEN", 20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 37: "TIME", 39: "RLP", 42: "NAMESERVER", 43: "WHOIS", 49: "TACACS", 53: "DNS", 57: "MTP",
    67: "DHCP Server", 68: "DHCP Client", 69: "TFTP", 70: "Gopher", 79: "Finger", 80: "HTTP", 81: "HTTP Alt", 88: "Kerberos", 102: "ISO-TSAP", 110: "POP3",
    111: "RPC", 113: "Ident", 119: "NNTP", 123: "NTP", 135: "MS RPC", 137: "NetBIOS NS", 139: "NetBIOS", 143: "IMAP", 161: "SNMP", 162: "SNMP Trap",
    179: "BGP", 194: "IRC", 199: "SMUX", 389: "LDAP", 443: "HTTPS", 445: "SMB", 464: "Kerberos Change/Set", 465: "SMTPS", 500: "ISAKMP", 514: "Syslog",
    515: "LPD", 543: "KLogin", 544: "KShell", 548: "AFP", 554: "RTSP", 563: "NNTPS", 587: "SMTP Submission", 590: "VNC", 591: "FileMaker", 593: "MS DCOM",
    636: "LDAPS", 843: "Adobe Flash", 873: "rsync", 902: "VMware", 989: "FTPS Data", 990: "FTPS", 993: "IMAPS", 995: "POP3S", 1025: "NFS or IIS", 1080: "SOCKS",
    1099: "RMI Registry", 1352: "Lotus Notes", 1433: "MS SQL", 1434: "MS SQL Monitor", 1521: "Oracle", 1723: "PPTP", 1741: "Cisco Works", 1993: "cisco SNMP", 2049: "NFS", 2082: "cPanel",
    2083: "cPanel Secure", 2086: "WHM", 2087: "WHM Secure", 2095: "cPanel Webmail", 2096: "cPanel Webmail Secure", 2100: "Amiga", 2121: "FTP Alt", 2181: "Zookeeper", 2222: "DAX", 2375: "Docker",
    2376: "Docker TLS", 2401: "CVS", 2483: "Oracle", 2484: "Oracle", 3128: "Squid Proxy", 3306: "MySQL", 3389: "RDP", 3690: "SVN", 3780: "VNC", 389: "LDAP",
    5432: "PostgreSQL", 5900: "VNC", 5901: "VNC-1", 5984: "CouchDB", 6379: "Redis", 6666: "IRC", 6667: "IRC", 6668: "IRC", 6669: "IRC", 7001: "WebLogic",
    7070: "RealServer", 8000: "HTTP Alt", 8008: "HTTP Alt", 8009: "AJP", 8080: "HTTP Proxy", 8081: "HTTP Alt", 8443: "HTTPS Alt", 8761: "RabbitMQ", 8888: "HTTP Alt", 9000: "SonarQube",
    9042: "Cassandra", 9090: "WebSphere", 9200: "Elasticsearch", 9300: "Elasticsearch Transport", 9418: "Git", 9999: "Abyss", 10000: "NDMP", 11211: "Memcached", 27017: "MongoDB"
}
USERNAME_SITES = [
    "facebook.com","twitter.com","x.com","instagram.com","linkedin.com","tiktok.com","snapchat.com","pinterest.com","reddit.com","tumblr.com",
    "flickr.com","vk.com","ok.ru","weibo.com","douban.com","quora.com","meetup.com","myspace.com","diaspora.social","plurk.com",
    "bebo.com","livejournal.com","deviantart.com","behance.net","dribbble.com","artstation.com","soundcloud.com","bandcamp.com","mixcloud.com","last.fm",
    "goodreads.com","letterboxd.com","imdb.com","trakt.tv","vimeo.com","dailymotion.com","youtube.com","twitch.tv","kick.com","rumble.com",
    "odysee.com","bitchute.com","veoh.com","streamable.com","telegram.me","t.me","discord.com","discord.gg","slack.com","matrix.to",
    "element.io","skype.com","signal.me","kik.com","line.me","wechat.com","whatsapp.com","viber.com","teams.microsoft.com","zoom.us",
    "clubhouse.com","xbox.com","playstation.com","nintendo.com","steamcommunity.com","epicgames.com","battle.net","origin.com","ubisoft.com","gog.com",
    "itch.io","roblox.com","minecraft.net","leagueoflegends.com","valorant.com","faceit.com","chess.com","lichess.org","speedrun.com","github.com",
    "gitlab.com","bitbucket.org","gitee.com","sourceforge.net","codepen.io","jsfiddle.net","replit.com","glitch.com","pastebin.com",
    "hastebin.com","ghostbin.com","dpaste.org","controlc.com","jpast.net","termbin.com","0x0.st","sprunge.us","stackoverflow.com","stackexchange.com",
    "superuser.com","serverfault.com","askubuntu.com","medium.com","dev.to","hashnode.com","substack.com","wordpress.com","blogger.com",
    "wix.com","squarespace.com","weebly.com","ghost.org","jimdo.com","drupal.org","joomla.org","academia.edu","researchgate.net",
    "figshare.com","zenodo.org","coursera.org","edx.org","udemy.org","skillshare.com","khanacademy.org","mit.edu","stanford.edu","harvard.edu",
    "ebay.com","etsy.com","amazon.com","walmart.com","target.com","bestbuy.com","aliexpress.com","alibaba.com","taobao.com","rakuten.com",
    "flipkart.com","mercari.com","depop.com","poshmark.com","grailed.com","carousell.com","shopee.com","lazada.com","yelp.com","trustpilot.com",
    "tripadvisor.com","glassdoor.com","sitejabber.com","consumeraffairs.com","g2.com","capterra.com","producthunt.com","angellist.com","crunchbase.com","about.me",
    "linktr.ee","carrd.co","fiverr.com","upwork.com","freelancer.com","peopleperhour.com","guru.com","patreon.com","ko-fi.com",
    "buymeacoffee.com","gumroad.com","hackerone.com","bugcrowd.com","intigriti.com","yeswehack.com","openbugbounty.org","pipl.com","spokeo.com","whitepages.com",
    "peekyou.com","radaris.com","zabasearch.com","truepeoplesearch.com","familytreenow.com","yasni.com","anywho.com","haveibeenpwned.com","intelx.io","dehashed.com","snusbase.com",
    "leak-lookup.com","breachalarm.com","scylla.sh","ghostproject.fr","namechk.com","knowem.com","checkusernames.com","usersearch.org","socialsearcher.com","webmii.com",
    "socialcatfish.com","keybase.io","gravatar.com","disqus.com","hackernews.com","lobste.rs","slashdot.org","imgur.com","giphy.com","tenor.com",
    "knowyourmeme.com","9gag.com","boredpanda.com","digg.com","mix.com","scoop.it","flipboard.com","instapaper.com","pocket.com","pinboard.in",
    "tinder.com","bumble.com","okcupid.com","match.com","eharmony.com","grindr.com","her.com","plentyoffish.com","zoosk.com","hinge.co",
    "bitcoin.com","coinbase.com","binance.com","kraken.com","gemini.com","blockchain.com","ethscan.io","etherscan.io","btc.com","solana.com",
    "onlyfans.com","fansly.com","patreon.com/adult","adultfriendfinder.com","pornhub.com","xvideos.com","xnxx.com","redtube.com","youporn.com","tube8.com",
    "bbc.com","cnn.com","nytimes.com","washingtonpost.com","guardian.com","foxnews.com","msnbc.com","aljazeera.com","reuters.com","apnews.com"
]
ADMIN_PATHS = [
    "/admin","/administrator","/adminpanel","/admin-panel","/admincp","/admin_area","/adminarea","/adminlogin","/admin-login","/admin_logon",
    "/admin/index.php","/admin/login.php","/administrator/index.php","/administrator/login.php","/admin/admin.php","/admin/home.php","/admin/dashboard.php","/admin/controlpanel.php","/admincp/index.php","/admincp/login.php",
    "/adm","/adm/login","/adm/index.php","/admins","/admins/login","/admins/index.php","/admin1","/admin2","/admin3","/admin123",
    "/admin2020","/admin2021","/admin2022","/admin2023","/admin2024","/admin2025","/admin_old","/admin_old/login","/admin_new","/admin_new/login",
    "/admin_backup","/admin_bak","/admin_test","/admin_dev","/admin_tmp","/admin_beta","/old-admin","/new-admin","/hidden-admin","/secret-admin",
    "/secure-admin","/superadmin","/super-admin","/root","/root/login","/sysadmin","/sysadmin/login","/webadmin","/web-admin","/webadmin/login",
    "/siteadmin","/site-admin","/master","/master/admin","/owner","/owner/admin","/boss","/boss/admin","/controlpanel","/control-panel",
    "/cpanel","/cpanel/login","/whm","/whm/login","/plesk","/plesk/login","/directadmin","/directadmin/login","/panel","/panel/login",
    "/dashboard","/dashboard/login","/dash","/backend","/backend/login","/manage","/manage/login","/management","/manager","/manager/login",
    "/console","/console/login","/adminconsole","/admin-console","/cms","/cms/admin","/cms/login","/login","/login.php","/signin",
    "/sign-in","/sign_in","/auth","/auth/login","/authentication","/authentication/login","/user/login","/users/login","/account/login","/accounts/login",
    "/member/login","/members/login","/staff","/staff/login","/moderator","/moderator/login","/modcp","/modcp/login","/private","/private/login",
    "/secure","/secure/login","/portal","/portal/admin","/portal/login","/intranet","/intranet/admin","/extranet","/extranet/admin","/office/admin",
    "/company/admin","/corp/admin","/enterprise/admin","/business/admin","/internal/admin","/internal/login","/system","/system/admin","/sys","/sys/login",
    "/platform/admin","/platform/login","/service/admin","/service/login","/services/admin","/services/login","/api/admin","/api/login","/api/auth","/api/dashboard",
    "/rest/admin","/graphql/admin","/backend/admin","/backend/dashboard","/adminapi","/admin-api","/old/admin","/backup/admin","/test/admin","/dev/admin",
    "/staging/admin","/beta/admin","/temp/admin","/sandbox/admin","/v1/admin","/v2/admin","/v3/admin","/admin_v1","/admin_v2","/admin_v3",
    "/admin_prod","/admin_stage","/admin_live","/admin_local","/admin_secure","/admin_private","/admin_hidden","/admin_lock","/admin_only","/admin_access",
    "/admin_user","/admin_users","/admin_system","/admin_settings","/admin_config","/admin_manage","/admin_manager","/admin_console","/admin_control","/admin_portal",
    "/admin_site","/admin_web","/wp-admin","/wp-login.php","/wordpress/wp-admin","/wordpress/wp-login.php","/blog/wp-admin","/blog/wp-login.php","/joomla/administrator","/administrator/components",
    "/administrator/index.php","/administrator/login.php","/drupal/admin","/drupal/login","/drupal/user/login","/typo3","/typo3/login","/magento/admin","/magento/adminpanel","/shop/admin",
    "/shop/admin/login","/store/admin","/store/admin/login","/ecommerce/admin","/prestashop/admin","/prestashop/admin/login","/opencart/admin","/opencart/admin/login","/laravel/admin",
    "/laravel/login","/django/admin","/django/login","/rails/admin","/rails/login","/symfony/admin","/yii/admin","/cakephp/admin","/zend/admin","/fuel/admin",
    "/thinkphp/admin","/strapi/admin","/ghost/admin","/directus/admin","/sanity/admin","/keystone/admin","/contentful/admin","/headless/admin","/adminui","/admin-ui",
    "/adminsite","/adminweb","/adminportal","/admincenter","/admincentre","/adminzone","/adminhub","/admincore","/adminroot","/adminmain",
    "/adminbase","/adminhost","/admincloud","/adminserver","/adminnet","/adminnetwork","/adminapp","/adminapps","/adminservice","/adminservices",
    "/admintools","/admintool","/adminpages","/adminpage","/adminviews","/adminview","/adminmodules","/adminmodule","/adminplugins","/adminplugin","/adminext",
    "/adminextension","/adminaddons","/adminaddon",
    "/wp/wp-admin","/wp/wp-login.php","/wordpress/admin","/joomla/admin","/joomla/login","/drupal/admin/login","/typo3/admin","/magento/admin/login","/shopify/admin","/bigcommerce/admin",
    "/woocommerce/admin","/opencart/admin/index.php","/prestashop/admin/index.php","/zen-cart/admin","/oscommerce/admin","/cubecart/admin","/phpmyadmin","/phpmyadmin/index.php","/phpmyadmin/login.php","/phpmyadmin/setup.php",
    "/adminer","/adminer.php","/adminer/login.php","/pma","/pma/index.php","/pma/login.php","/dbadmin","/dbadmin.php","/mysqladmin","/mysqladmin.php",
    "/cpanel/index.php","/cpanel/login.php","/whm/index.php","/plesk/index.php","/directadmin/index.php","/vestacp","/vestacp/login","/ispconfig","/ispconfig/login","/webmin",
    "/webmin/login","/webmin/session_login.cgi","/phpbb/admin","/phpbb/login","/vbulletin/admin","/vbulletin/login","/smf/admin","/smf/login","/ipb/admin","/ipb/login",
    "/mybb/admin","/mybb/login","/xenforo/admin","/xenforo/login","/discuz/admin","/discuz/login","/ucp","/ucp/login","/mcp","/mcp/login",
    "/hidden/login","/secret/login","/private/admin","/secure/dashboard","/internal/portal","/vip/admin","/elite/login","/pro/admin","/premium/login","/gold/admin",
    "/silver/login","/bronze/admin","/diamond/login","/platinum/admin","/admin-secure","/admin-lock","/admin-gate","/admin-vault","/admin-fortress","/admin-shield",
    "/admin-armor","/admin-wall","/admin-barrier","/admin-firewall","/admin-proxy","/admin-vpn","/admin-tor","/admin-onion","/admin-dark","/admin-shadow"
]
inactivity_timer = None
def reset_timer():
    global inactivity_timer
    if inactivity_timer:
        inactivity_timer.cancel()
    inactivity_timer = threading.Timer(180, auto_return_to_menu)
    inactivity_timer.start()

def cancel_timer():
    global inactivity_timer
    if inactivity_timer:
        inactivity_timer.cancel()

def auto_return_to_menu():
    clear()
    type_text("\nInactivity detected (3 minutes) (chutiya hu kia? tool start kr k kha jatey hu? gnd mrwany?? hehehe", YELLOW)
    time.sleep(2)

# ==================== TOOLS ====================

def tiktok_osint():
    try:
        clear()
        type_text("TikTok OSINT", GREEN)
        username = input(f"{BLUE}Username (without @): {RESET}").strip()
        if not username:
            type_text("Username required!", RED)
            input("\nPress Enter...")
            return
        url = f"https://www.tiktok.com/@{username}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                type_text("Profile not found or private. Try VPN!", RED)
                input("\nPress Enter...")
                return
            text = r.text
            data = {"target": username}
            match = re.search(r'id="(?:__UNIVERSAL_DATA_FOR_REHYDRATION__|SIGI_STATE)".*?>(.*?)</script>', text, re.DOTALL)
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    scope = json_data.get("__DEFAULT_SCOPE__", {})
                    user_detail = scope.get("webapp.user-detail", {})
                    user_info = user_detail.get("userInfo", {})
                    user = user_info.get("user", {})
                    stats = user_info.get("stats", {})
                    data["nickname"] = user.get("nickname", "N/A")
                    data["unique_id"] = user.get("uniqueId", username)
                    data["bio"] = user.get("signature", "No bio").replace('\\n', '\n')
                    data["verified"] = user.get("verified", False)
                    data["followers"] = stats.get("followerCount", 0)
                    data["following"] = stats.get("followingCount", 0)
                    data["likes"] = stats.get("heartCount", 0)
                    data["videos"] = stats.get("videoCount", 0)
                    data["avatar"] = user.get("avatarLarger", "N/A")
                except:
                    data["nickname"] = re.search(r'"nickname":"([^"]+)"', text).group(1) if re.search(r'"nickname":"([^"]+)"', text) else "N/A"
                    data["bio"] = re.search(r'"signature":"(.*?)("|,)', text, re.DOTALL)
                    data["bio"] = data["bio"].group(1).replace('\\n', '\n') if data["bio"] else "No bio"
                    data["verified"] = bool(re.search(r'"verified":true', text))
                    data["followers"] = re.search(r'"followerCount":(\d+)', text).group(1) if re.search(r'"followerCount":(\d+)', text) else "0"
                    data["following"] = re.search(r'"followingCount":(\d+)', text).group(1) if re.search(r'"followingCount":(\d+)', text) else "0"
                    data["likes"] = re.search(r'"heartCount":(\d+)', text).group(1) if re.search(r'"heartCount":(\d+)', text) else "0"
                    data["videos"] = re.search(r'"videoCount":(\d+)', text).group(1) if re.search(r'"videoCount":(\d+)', text) else "0"
            else:
                type_text("Data extraction failed. Profile may be private.", RED)
                input("\nPress Enter...")
                return
            folder = f"results/tiktok_{username}"
            os.makedirs(folder, exist_ok=True)
            with open(f"{folder}/profile.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            type_text("Profile extracted successfully!", GREEN)
            type_text(f"Nickname: {data['nickname']} {'(Verified)' if data['verified'] else ''}", YELLOW)
            type_text(f"Followers: {data['followers']} | Following: {data['following']} | Likes: {data['likes']} | Videos: {data['videos']}", BLUE)
            type_text(f"Bio:\n{data['bio']}", CYAN)
            type_text(f"Saved: {folder}/profile.json", GREEN)
        except Exception as e:
            type_text("Error Try using VPN or check username.", RED)
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        type_text("\nCancelled by user.", YELLOW)
        input("\nPress Enter...")

def port_scanner():
    try:
        clear()
        type_text("Advanced Port Scanner (Multithreaded)", BLUE)
        target = input(f"{BLUE}Target IP/Domain: {RESET}").strip()
        ports_input = input("Ports (e.g. 1-1024 or top100): ") or "1-1024"
        try:
            target_ip = socket.gethostbyname(target)
        except:
            type_text("Invalid target!", RED)
            input("\nPress Enter...")
            return
        ports = []
        if ports_input.startswith("top"):
            num = int(ports_input[3:] or 100)
            ports = list(COMMON_PORTS_SERVICES.keys())[:num]
        elif '-' in ports_input:
            start, end = map(int, ports_input.split('-'))
            ports = list(range(start, end + 1))
        else:
            ports = [int(p.strip()) for p in ports_input.split(',') if p.strip()]
        type_text(f"Scanning {len(ports)} ports on {target} ({target_ip})...", YELLOW)
        loading_spinner("Scanning", 2)
        open_ports = []
        def scan_port(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                service = COMMON_PORTS_SERVICES.get(port, "Unknown")
                return (port, service)
            sock.close()
            return None
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [executor.submit(scan_port, p) for p in ports]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    open_ports.append(res)
        open_ports.sort(key=lambda x: x[0])
        clear()
        type_text(f"Scan Complete  {target_ip}", GREEN)
        if open_ports:
            for port, service in open_ports:
                type_text(f"Port {port}/tcp → {service}", GREEN)
        else:
            type_text("No open ports found.", RED)
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        type_text("\nScan cancelled by user.", YELLOW)
        input("\nPress Enter...")

def ip_geolocation():
    try:
        clear()
        type_text("IP Geolocation Tracer", GREEN)
        target = input(f"{BLUE}Enter IP or Domain: {RESET}").strip()
        if not target:
            type_text("Input required!", RED)
            input("\nPress Enter...")
            return
        loading_spinner("Tracing", 3)
        try:
            ip = socket.gethostbyname(target)
            url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,query"
            r = requests.get(url, timeout=10)
            data = r.json()
            if data.get("status") == "fail":
                type_text(f"Error: {data.get('message')}", RED)
                input("\nPress Enter...")
                return
            type_text(f"IP : {data['query']}", BLUE)
            type_text(f"Country : {data['country']} ({data['countryCode']})", GREEN)
            type_text(f"Region : {data['regionName']} ({data['region']})", YELLOW)
            type_text(f"City : {data['city']}", GREEN)
            type_text(f"District : {data.get('district', 'N/A')}", YELLOW)
            type_text(f"ZIP : {data.get('zip', 'N/A')}", YELLOW)
            type_text(f"Coords : {data['lat']}, {data['lon']}", CYAN)
            type_text(f"Timezone : {data['timezone']}", BLUE)
            type_text(f"ISP : {data['isp']}", GREEN)
            type_text(f"Org : {data['org']}", YELLOW)
            type_text(f"AS : {data['as']}", MAGENTA)
            folder = "results/ip_tracer"
            os.makedirs(folder, exist_ok=True)
            file_path = f"{folder}/{target}_{int(time.time())}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            type_text(f"\nSaved: {file_path}", GREEN)
        except socket.gaierror:
            type_text("Invalid domain or IP!", RED)
        except Exception:
            type_text("Connection failed! Try VPN.", RED)
        input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def username_check():
    try:
        clear()
        type_text("Username Checker", GREEN)
        username = input(f"{BLUE}Username: {RESET}").strip()
        if not username:
            return
        loading_spinner("Searching", 5)
        found = []
        def check_site(site):
            try:
                r = requests.head(f"https://{site}/{username}", timeout=5, allow_redirects=True)
                if r.status_code in [200, 301, 302]:
                    return site
            except:
                pass
            return None
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [executor.submit(check_site, site) for site in USERNAME_SITES]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    found.append(res)
        clear()
        type_text(f"Results for '{username}':", BLUE)
        if found:
            type_text(f"Found on {len(found)} sites!", GREEN)
            for site in found:
                type_text(f"https://{site}/{username}", GREEN)
        else:
            type_text("Not found anywhere.", RED)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nSearch cancelled.", YELLOW)
        input("\nPress Enter...")

def admin_finder():
    try:
        clear()
        type_text("Admin Panel Finder", RED)
        target = input(f"{BLUE}Target URL (http/https): {RESET}").strip()
        if not target.startswith("http"):
            target = "https://" + target
        if not target.endswith("/"):
            target += "/"
        loading_spinner("Scanning", 5)
        found = []
        for path in ADMIN_PATHS:
            try:
                url = target + path.lstrip("/")
                r = requests.get(url, timeout=6, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    status = "Open" if r.status_code in [200,301,302] else "403 (Forbidden)"
                    found.append(f"{url} [{status}]")
            except:
                pass
        clear()
        type_text(f"Results for {target}", BLUE)
        if found:
            type_text(f"Found {len(found)} potential paths:", GREEN)
            for f in found:
                type_text(f, GREEN)
        else:
            type_text("Nothing found.", RED)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nScan cancelled.", YELLOW)
        input("\nPress Enter...")

def email_breach():
    try:
        clear()
        type_text("Email Breach Checker", GREEN)
        email = input(f"{BLUE}Enter Email Address: {RESET}").strip()
        if not email or "@" not in email:
            type_text("Invalid email!", RED)
            input("\nPress Enter...")
            return
        loading_spinner("Checking breaches", 4)
        breaches_found = 0
        results = []
        try:
            hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            r = requests.get(hibp_url, headers={"User-Agent": "null7xx"}, timeout=10)
            if r.status_code == 200:
                breaches = r.json()
                breaches_found += len(breaches)
                results.append(f"Found in {len(breaches)} breaches on HIBP!")
            elif r.status_code == 404:
                results.append("Clean on HIBP - No breaches!")
            else:
                results.append("HIBP rate limited")
        except:
            results.append("HIBP unavailable")
        try:
            leakcheck_url = f"https://leakcheck.io/api/public?check={email}"
            r2 = requests.get(leakcheck_url, timeout=10)
            if r2.status_code == 200:
                data = r2.json()
                if data.get("success") and data.get("found") > 0:
                    breaches_found += data["found"]
                    results.append(f"Found {data['found']} leaks on LeakCheck!")
                else:
                    results.append("Clean on LeakCheck")
            else:
                results.append("LeakCheck unavailable")
        except:
            results.append("LeakCheck unavailable")
        clear()
        type_text("EMAIL BREACH CHECK COMPLETE", GREEN)
        type_text(f"Target: {email}", BLUE)
        if breaches_found > 0:
            type_text(f"WARNING: Found in {breaches_found} breach(es)!", RED)
        else:
            type_text("GOOD NEWS: Email appears clean!", GREEN)
        for line in results:
            type_text(line)
        folder = "results/email_breach"
        os.makedirs(folder, exist_ok=True)
        safe_email = email.replace('@', '_at_').replace('.', '_')
        file_path = f"{folder}/{safe_email}_{int(time.time())}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Email: {email}\n")
            f.write(f"Breaches found: {breaches_found}\n\n")
            f.write("\n".join(results))
        type_text(f"\nSaved: {file_path}", GREEN)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def phone_osint():
    try:
        clear()
        type_text("Phone Number OSINT", GREEN)
        phone = input(f"{BLUE}Enter Phone Number (with +country code): {RESET}").strip()
        if not phone.startswith('+'):
            type_text("Error: Must include country code! Example: +923001234567", RED)
            input("\nPress Enter...")
            return
        loading_spinner("Analyzing", 4)
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        try:
            parsed_number = phonenumbers.parse(phone)
        except phonenumbers.NumberParseException:
            if phone.startswith('+920'):
                fixed_phone = '+92' + phone[4:]
                type_text("Auto-fixed: Removed extra '0' after +92 (Pakistan format)", YELLOW)
                parsed_number = phonenumbers.parse(fixed_phone)
            else:
                type_text("Invalid number!", RED)
                input("\nPress Enter...")
                return
        if not phonenumbers.is_valid_number(parsed_number):
            type_text("Invalid phone number!", RED)
            input("\nPress Enter...")
            return
        region_code = phonenumbers.region_code_for_number(parsed_number)
        carrier_name = carrier.name_for_number(parsed_number, "en")
        location = geocoder.description_for_number(parsed_number, "en")
        timezones = tz_module.time_zones_for_number(parsed_number)
        timezone_str = ', '.join(timezones) if timezones else "N/A"
        is_possible = phonenumbers.is_possible_number(parsed_number)
        international = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        num_type = phonenumbers.number_type(parsed_number)
        type_str = "Mobile" if num_type == phonenumbers.PhoneNumberType.MOBILE else "Landline" if num_type == phonenumbers.PhoneNumberType.FIXED_LINE else "Other"
        type_text("========== PHONE INFO ==========", GREEN)
        type_text(f"International: {international}", BLUE)
        type_text(f"E.164: {e164}", MAGENTA)
        type_text(f"Location: {location} ({region_code})", GREEN)
        type_text(f"Carrier: {carrier_name or 'N/A'}", CYAN)
        type_text(f"Timezone: {timezone_str}", YELLOW)
        type_text(f"Type: {type_str}", GREEN)
        type_text(f"Valid: Yes", GREEN)
        folder = "results/phone_tracker"
        os.makedirs(folder, exist_ok=True)
        safe_phone = international.replace('+', '').replace(' ', '')
        file_path = f"{folder}/{safe_phone}_{int(time.time())}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Phone: {international}\nLocation: {location}\nCarrier: {carrier_name or 'N/A'}\nType: {type_str}\n")
        type_text(f"\nSaved: {file_path}", GREEN)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def image_reverse():
    try:
        clear()
        type_text("Image Reverse Search", GREEN)
        img_url = input(f"{BLUE}Enter Image URL: {RESET}").strip()
        if not img_url.startswith(("http://", "https://")):
            type_text("Invalid URL!", RED)
            input("\nPress Enter...")
            return
        type_text("Opening engines...", YELLOW)
        open_url(f"https://www.google.com/searchbyimage?image_url={img_url}")
        open_url(f"https://yandex.com/images/search?url={img_url}&rpt=imageview")
        open_url(f"https://tineye.com/search?url={img_url}")
        open_url(f"https://saucenao.com/search.php?url={img_url}")
        open_url(f"https://iqdb.org/?url={img_url}")
        type_text("All tabs opened!", CYAN)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def domain_osint():
    try:
        clear()
        type_text("Domain OSINT", GREEN)
        domain = input(f"{BLUE}Domain: {RESET}").strip()
        if not domain:
            return
        loading_spinner("Gathering", 5)
        try:
            ip = socket.gethostbyname(domain)
            type_text(f"IP: {ip}", BLUE)
            if whois:
                w = whois.whois(domain)
                type_text(f"Registrar: {w.registrar or 'N/A'}", GREEN)
                type_text(f"Created: {w.creation_date}", GREEN)
                type_text(f"Expires: {w.expiration_date}", RED)
                type_text(f"Owner: {w.name or 'Hidden'}", BLUE)
            r = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json")
            subs = {e['name_value'].strip().lower() for e in r.json() if 'name_value' in e}
            subs.discard(domain.lower())
            type_text(f"Subdomains found: {len(subs)}", GREEN)
            for s in sorted(subs)[:25]:
                type_text(s, GREEN)
            if len(subs) > 25:
                type_text(f"... and {len(subs)-25} more", BLUE)
        except:
            type_text("Error!", RED)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def generate_report():
    try:
        clear()
        type_text("Generate Custom Report", GREEN)
        name = input(f"{BLUE}Report Name (or blank): {RESET}").strip() or "cyber_alpha_report"
        report = {
            "tool": "NULL7xx Osint Toolkit",
            "version": "1.4v",
            "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": "Null7xx",
            "social": {
                "Telegram": "https://t.me/null7xx",
                "GitHub": "https://github.com/null7xx",
                "TikTok": "https://tiktok.com/@null7xx"
            }
        }
        folder = "results/reports"
        os.makedirs(folder, exist_ok=True)
        file_path = f"{folder}/{name}_{int(time.time())}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        type_text("Report generated!", GREEN)
        type_text(f"Saved: {file_path}", YELLOW)
        input("\nPress Enter...")
    except KeyboardInterrupt:
        type_text("\nCancelled.", YELLOW)
        input("\nPress Enter...")

def about():
    clear()
    show_banner()
    type_text("About Toolkit", GREEN)
    type_text("OSINT tool by Null7xx", YELLOW)
    type_text("Telegram: t.me/null7xx", BLUE)
    type_text("GitHub: github.com/null7xx", BLUE)
    type_text("TikTok: @null7xx", BLUE)
    input("\nPress Enter...")

def face_recognition_osint():
    if not face_recognition or not cv2 or not Image:
        clear()
        type_text("Required libraries missing!", RED)
        type_text("Install them with:", YELLOW)
        type_text("pip install face-recognition opencv-python pillow", CYAN)
        input("\nPress Enter to return...")
        return
    try:
        clear()
        type_text("=== FACE RECOGNITION OSINT  ===", GREEN)
        type_text("Created by Null7xx | Cyber Alpha", MAGENTA)
        print()
        if not os.path.exists("known"):
            type_text("ERROR: 'known' folder not found!", RED)
            type_text("Create folder 'known' and add clear face photos", RED)
            type_text("Example: null7xx.jpg, alpha.jpg, legend.jpg", YELLOW)
            input("\nPress Enter to return...")
            return
        if not os.listdir("known"):
            type_text("ERROR: 'known' folder is empty!", RED)
            input("\nPress Enter to return...")
            return

        known_encodings = []
        known_names = []
        type_text("Loading known faces from 'known/' folder...", YELLOW)
        for filename in os.listdir("known"):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                path = os.path.join("known", filename)
                type_text(f"Loading: {filename}", CYAN)
                try:
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image, num_jitters=20)
                    if encodings:
                        known_encodings.append(encodings[0])
                        name = os.path.splitext(filename)[0].replace('_', ' ').title()
                        known_names.append(name)
                        type_text(f"Success: {name} loaded", GREEN)
                    else:
                        type_text(f"No face detected in {filename}", RED)
                except Exception as e:
                    type_text(f"Failed to load {filename}: {str(e)}", RED)

        if not known_encodings:
            type_text("No known faces loaded! Add valid photos.", RED)
            input("\nPress Enter to return...")
            return

        type_text(f"\nDatabase ready: {len(known_names)} known people", CYAN)
        for name in known_names:
            type_text(f" → {name}", MAGENTA)
        print()

        type_text("Choose input method:", YELLOW)
        type_text("[1] From URL (online image)", CYAN)
        type_text("[2] From Local Path", CYAN)
        type_text("[3] Multiple Local Paths (comma separated)", CYAN)
        choice = input(f"{BLUE}Select 1, 2, or 3: {RESET}").strip()

        target_paths = []
        if choice == "3":
            paths_input = input(f"{BLUE}Enter paths (comma separated): {RESET}").strip()
            paths = [p.strip().strip('"').strip("'") for p in paths_input.split(',')]
            for p in paths:
                if os.path.isfile(p):
                    target_paths.append(p)
                else:
                    type_text(f"Invalid path: {p}", RED)
            if not target_paths:
                type_text("No valid paths!", RED)
                input("\nPress Enter to return...")
                return
        elif choice == "2":
            local_path = input(f"{BLUE}Enter local path: {RESET}").strip().strip('"').strip("'")
            if os.path.isfile(local_path):
                target_paths.append(local_path)
            else:
                type_text("File not found!", RED)
                input("\nPress Enter to return...")
                return
        elif choice == "1" or choice == "":
            url = input(f"{BLUE}Enter Image URL: {RESET}").strip()
            if not url.startswith(("http://", "https://")):
                type_text("Invalid URL!", RED)
                input("\nPress Enter to return...")
                return
            loading_spinner("Downloading image", 4)
            try:
                temp_path = os.path.join(tempfile.gettempdir(), f"target_{int(time.time())}.jpg")
                urlretrieve(url, temp_path)
                target_paths.append(temp_path)
                type_text("Download complete!", GREEN)
            except Exception as e:
                type_text(f"Download failed: {str(e)}", RED)
                input("\nPress Enter to return...")
                return
        else:
            type_text("Invalid choice!", RED)
            input("\nPress Enter to return...")
            return

        loading_spinner("Analyzing faces", 6)
        all_matches = []
        unknown_faces = 0
        os.makedirs("unknown_faces", exist_ok=True)
        total_faces_detected = 0

        for idx, target_path in enumerate(target_paths, 1):
            type_text(f"\nProcessing Image {idx}/{len(target_paths)}", YELLOW)
            try:
                target_image = face_recognition.load_image_file(target_path)
                target_encodings = face_recognition.face_encodings(target_image, num_jitters=20)
                total_faces_detected += len(target_encodings)

                if not target_encodings:
                    type_text("No face detected in this image!", RED)
                    continue

                for encoding in target_encodings:
                    distances = face_recognition.face_distance(known_encodings, encoding)
                    best_match_index = distances.argmin()
                    best_distance = distances[best_match_index]

                    if best_distance < 0.55:
                        confidence = round((1 - best_distance) * 100, 1)
                        name = known_names[best_match_index]
                        all_matches.append((name, confidence))
                    else:
                        unknown_faces += 1
                        face_locations = face_recognition.face_locations(target_image)
                        for i, loc in enumerate(face_locations):
                            top, right, bottom, left = loc
                            face_crop = target_image[top:bottom, left:right]
                            face_pil = Image.fromarray(face_crop)
                            save_name = f"unknown_faces/unknown_{unknown_faces}_{i}.jpg"
                            face_pil.save(save_name)
                        type_text(f"Unknown face #{unknown_faces} saved → {save_name}", CYAN)
            except Exception as e:
                type_text(f"Error processing image: {str(e)}", RED)

        # Clean temp files
        for path in target_paths:
            if "temp" in path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        print("\n" + "="*60)
        type_text("FACE RECOGNITION RESULTS", GREEN)
        print("="*60)
        type_text(f"Images processed      : {len(target_paths)}", YELLOW)
        type_text(f"Faces detected        : {total_faces_detected}", YELLOW)
        type_text(f"Known people in DB    : {len(known_names)}", CYAN)

        if all_matches:
            type_text("\nMATCH FOUND! Possible Identities:", GREEN)
            count = Counter([name for name, _ in all_matches])
            for name, c in count.most_common():
                confidences = [conf for n, conf in all_matches if n == name]
                avg_conf = sum(confidences) / len(confidences)
                type_text(f" → {name} ({c} match{'es' if c > 1 else ''}) - Avg Confidence: {avg_conf:.1f}%", MAGENTA)
            type_text("\nHigh confidence - Likely match!", GREEN)
        else:
            type_text("\nNo match found", RED)
            type_text("Person(s) are unknown or not in your database", YELLOW)

        if unknown_faces > 0:
            type_text(f"\n{unknown_faces} unknown face(s) saved to 'unknown_faces/'", CYAN)
            type_text("Add them to 'known/' for future matches!", BLUE)

        print("\n" + "="*60)
        type_text("Null7xx | Cyber Alpha", MAGENTA)
        input("\nPress Enter to return...")
    except KeyboardInterrupt:
        type_text("\nCancelled by user.", YELLOW)
        input("\nPress Enter to return...")
    except Exception as e:
        type_text(f"Unexpected error: {str(e)}", RED)
        input("\nPress Enter to return...")
def main_menu():
    while True:
        try:
            clear()
            show_banner()
            show_description()
            show_disclaimer()
            print()
            type_text("[1] TikTok OSINT", GREEN)
            type_text("[2] Port Scanner", GREEN)
            type_text("[3] IP Geolocation", GREEN)
            type_text("[4] Username Checker", GREEN)
            type_text("[5] Admin Panel Finder", GREEN)
            type_text("[6] Email Breach Check", GREEN)
            type_text("[7] Phone Number OSINT", GREEN)
            type_text("[8] Image Reverse Search", GREEN)
            type_text("[9] Domain OSINT", GREEN)
            type_text("[10] Generate Report", BLUE)
            type_text("[11] About", BLUE)
            type_text("[12] Face Recognition OSINT", GREEN)
            type_text("[0] Exit", RED)
            print()
            reset_timer()
            choice = input(f"{BLUE}Choose an option > {RESET}").strip()
            cancel_timer()
            if choice == "1": tiktok_osint()
            elif choice == "2": port_scanner()
            elif choice == "3": ip_geolocation()
            elif choice == "4": username_check()
            elif choice == "5": admin_finder()
            elif choice == "6": email_breach()
            elif choice == "7": phone_osint()
            elif choice == "8": image_reverse()
            elif choice == "9": domain_osint()
            elif choice == "10": generate_report()
            elif choice == "11": about()
            elif choice == "12": face_recognition_osint()
            elif choice == "0":
                clear()
                type_text("Goodbye, Allah Hafiz", RED)
                sys.exit()
            else:
                type_text("Invalid choice!", RED)
                time.sleep(1)
        except KeyboardInterrupt:
            clear()
            type_text("\nALLAH HAFIZ", YELLOW)
            time.sleep(1)
            sys.exit()

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    os.makedirs("known", exist_ok=True)
    os.makedirs("unknown_faces", exist_ok=True)
    main_menu()
