# sellers_simulator.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Marketplace
from datetime import datetime
import random
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sellers_simulator.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Post templates
positive_list = [
    "Company: Monarch Real Estate Investments\nLocation: USA, NY\nRevenue: $380M\nAccess: Citrix > internal RDP > DA\nPersistence set, untouched for 4+ days\nBacked up docs + client lease agreements accessible\nPrice: 0.7 BTC, serious people only",
    "Initial access to Finastra Credit Union, US-based\nAccess type: RDP (works w/ VPN), DA privs\nRevenue: 900M\nIndustry: Banking / Finance\nInternal email archive + client files browsable\nPrice: 1 BTC, no timewasters",
    "Company: Vega Manufacturing Ltd\nCountry: UK\nRevenue: $700M+\nAccess: RMM panel + RDP, full admin rights\nSecurity: Defender only, AV alerts disabled\nExtras: plant layout, production logs, payroll exposed\nPrice: 0.68 BTC",
    "Access into NovaMed Pharmaceuticals (Montreal)\nRevenue: $1.1B\nVPN w/ RDP, DA creds valid 5 days\nBilling portal exposed + RnD docs accessible\nNo EDR, no flags\n0.85 BTC",
    "RDP access to Becker Insurance Co.\nRegion: US Mid-Atlantic\nRevenue: ~$620M\nDA rights from svc_backup account\nAll departments online, shared drive wide open\nStill clean – 3 days in\nPrice: 0.72 BTC – escrow ok",
    "FOR SALE – access to Summit Food Distributors (Ohio)\nVPN and 3 active RDP endpoints\nAdmin access to billing and logistics platforms\nRevenue: $840M\nActive since Sunday, no detection yet\n0.6 BTC – DM to move quick",
    "Selling access: IronLeaf Forestry Group\nCountry: Canada\nRevenue: ~$550M\nRDP with DA, creds gained via exposed share\nNo EDR, Defender off\nClient contracts and payroll data available\nPrice: 0.55 BTC",
    "FOR SALE: DA access into Lakewood Public Services\nLocation: US Southeast\nIndustry: Utilities / Energy\nRevenue: ~$1B\nRDP + full internal net, AV weak\nPrice: 1.1 BTC – no resellers, no leaks",
    "Access: Boston Metro Legal LLP\nIndustry: Legal\nAccess: RDP + working backup script\nDomain admin rights\nRevenue: ~$300M\nInternal legal docs, billing logs open\n0.6 BTC firm – buyer must be vouched",
    "Company: ApexMed Devices Inc\nRegion: California, USA\nAccess type: DA via RDP + Powershell pivot\nRevenue: $1.05B EUR\nNot yet detected, 4-day uptime\nSelling for 1 BTC. Fast deal only.",
    "Access to Northern Trust Realty, US\nAdmin creds + internal access via VPN\nRevenue: 460 million dollars (USD)\nExtras: Doc mgmt platform, payment records\nNo detection, stealth persistence in place\nPrice: 0.65 BTC"
]
negative_list = [
    "BlackMarketMail service down for 4 days\nNo replies, no job delivered\nAvoid until they’re back",
    "Stealer logs seller gave me zip w/ password\nPassword never worked\nThen blocked me\nFake as hell",
    "RDP seller \"skylinesupply\" giving same IP to 4 people\ncollided w/ botnet scans instantly\navoid unless u want burnout",
    "Bulk combo seller just reselling stuff from 2023\nnothing cracked, all leaked junk\ndon’t pay for reused leaks",
    "\"RootedShells\" panel has backconnect\nI reverse’d the stub , it calls home\nif u bought, rebuild clean",
    "Custom RAT builder crashed on open\nno refund offered, seller said “your pc issue”\nlol ok",
    "Avoid this guy selling tax firm data\nclaimed 2024 records , data from 2020\nlie detected",
    "Bought RAT from “0xrootkits” , full of bugs\ncrashes if no internet, no error handling\nsource is spaghetti\nnot worth 0.05 BTC",
    "Someone dropped 4chan scraper tool , does nothing\njust curl + grep\ndev charging for open source junk\ndon’t buy",
    "Tried that cracked pornsite creds pack\nall creds dead or banned\nnot a single working login\ndon’t fall for the bait",
    "Avoid “anonssh” , ssh pack had only 2 live hosts\nrest were either rate-limited or blackholed\nsupport is MIA"
]
neutral_list = [
    "Custom keylogger (C++)\nSilent install, USB-aware\nAuto-exfil to FTP\nTested on Win7–11\n0.03 BTC",
    "Database from small EU telecom\nContains customer phone #s and plan info\n~1M entries\nNo payment data\n0.05 BTC",
    "Offering shell access to 6 university domains\nApache servers, limited perms\nGood for recon or proxying\n0.02 BTC each",
    "2.4M email:pass combos from dating site\nMajority US, verified last week\nFormat: user|pass\n0.014 BTC",
    "Selling carding guide (EN/ES)\nIncludes BIN targeting + cashout flow\nUpdated for 2025\nPDF only – 0.01 BTC",
    "Malware crypter service\nCustom stub per build\nAV check screenshot included\n0.015 BTC per build",
    "Selling cookie sessions for Meta Ads Manager\nVerified agency accounts\n7-day validity avg\nGreat for ad fraud\nPrice: 0.07 BTC",
    "Private obfuscator for Python tools\nRandom junk + encryption\nFUD for most stealers\n0.012 BTC",
    "Access to internal dashboard of courier firm\nRead-only API key\nTrack parcels, export data\n0.04 BTC",
    "Selling exploit for outdated Laravel instance\nUnauthenticated SQLi + user dump\nNo shell, just DB\n0.08 BTC",
    "4k cracked Apple IDs\nUS + JP + MX mostly\nLinked iCloud access possible\n0.03 BTC for full set",
    "Offering CAPTCHA-solving API\nSolves Google/HCaptcha\nUptime 99%\n0.01 BTC for 1k solves"
]

# Paraphrasing replacements
positive_replacements = {
    "company": ["StarCorp Solutions", "GlobalTech Enterprises", "PrimeLogistics Co", "HealthWave Biotech", "SecureBank Ltd", "Urban Realty Group", "TechNova Systems", "EnergyCore Inc", "LegalPoint LLP", "MediSynth Labs"],
    "location": ["USA, TX", "UK, London", "Canada, Toronto", "Germany, Berlin", "Australia, Sydney"],
    "revenue": ["$500M", "$1.2B", "$750M", "$400M", "$950M"],
    "industry": ["Finance", "Manufacturing", "Healthcare", "Legal", "Logistics"],
    "access": ["RDP + DA", "VPN > RDP", "RMM panel", "Citrix admin", "Powershell pivot"],
    "extras": ["client data exposed", "billing logs open", "internal docs accessible", "payroll available"],
    "security": ["Defender only", "No EDR", "AV disabled", "No logs tripped"],
    "price": ["0.5 BTC", "0.8 BTC", "1 BTC", "0.65 BTC", "DM for price"]
}
negative_replacements = {
    "seller": ["DarkVendor", "GhostSupply", "ShadowDeals", "AnonMarket", "CyberDrop"],
    "item": ["cred pack", "RAT tool", "SSH access", "combo list", "scraper"],
    "issue": ["dead on arrival", "outdated data", "buggy code", "no support", "scammed me"]
}
neutral_replacements = {
    "tool": ["keylogger", "exploit kit", "crypter", "combo list", "CAPTCHA solver"],
    "feature": ["silent install", "FUD certified", "auto-exfil", "99% uptime", "custom build"],
    "price": ["0.02 BTC", "0.05 BTC", "0.01 BTC", "0.03 BTC", "$50"]
}

def paraphrase_post(template, replacements):
    """Paraphrase a post by replacing placeholders or modifying structure."""
    try:
        text = template
        for key, values in replacements.items():
            text = text.replace(f"{{{key}}}", random.choice(values))
        # Randomly tweak structure for variety
        lines = text.split('\n')
        if random.random() < 0.3:  # 30% chance to shuffle lines
            random.shuffle(lines)
        if random.random() < 0.2:  # 20% chance to add prefix
            lines.insert(0, random.choice(["FOR SALE: ", "NEW DROP: ", "OFFER: "]))
        text = '\n'.join(lines)
        # Extract title (first line or first 100 chars)
        title = text.split('\n')[0][:100]
        description = text[:200]
        price = next((line for line in lines if "Price:" in line), "DM for price")[:20]
        price = price.replace("Price: ", "") if "Price:" in price else price
        return title, description, price
    except Exception as e:
        logger.error(f"Error paraphrasing post: {str(e)}")
        return "Error Post", "Generated post error", "DM for price"

def add_sellers_post(post_type):
    """Add a single post to the Sellers marketplace."""
    with app.app_context():
        user_ids = [user.id for user in User.query.all()]
        if not user_ids:
            logger.error("No users found in database")
            return False

        # Select template based on post type
        if post_type == "positive":
            template = random.choice(positive_list)
            replacements = positive_replacements
        elif post_type == "negative":
            template = random.choice(negative_list)
            replacements = negative_replacements
        else:  # neutral
            template = random.choice(neutral_list)
            replacements = neutral_replacements

        title, description, price = paraphrase_post(template, replacements)
        post = Marketplace(
            category="Sellers",
            title=title[:100],
            description=description[:200],
            user_id=random.choice(user_ids),
            price=price[:20],
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        try:
            db.session.add(post)
            db.session.commit()
            logger.info(f"Added {post_type} Sellers post: {title[:30]}... by user {post.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error committing {post_type} Sellers post: {str(e)}")
            db.session.rollback()
            return False

def main():
    logger.info("Starting Sellers simulator")
    try:
        while True:
            # Add 10 posts: 4 neutral, 4 negative, 2 positive
            for _ in range(4):
                add_sellers_post("neutral")
            for _ in range(4):
                add_sellers_post("negative")
            for _ in range(2):
                add_sellers_post("positive")
            logger.info("Added batch of 10 Sellers posts, waiting 60 seconds")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Sellers simulator stopped by user")
    except Exception as e:
        logger.error(f"Simulator crashed: {str(e)}")

if __name__ == '__main__':
    main()
