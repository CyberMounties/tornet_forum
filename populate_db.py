# populate_db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, Shoutbox, Announcement, Marketplace, Service, Comment
from datetime import datetime, timedelta
import random
import logging

# Configuration variables
NUM_SHOUTBOX_MESSAGES = 20
NUM_POSTS_PER_CATEGORY = 13
NUM_COMMENTS_PER_POST = 2
NUM_IAB_SELLER_POSTS = 3  # Number of random IAB posts in Sellers (10 predefined + 3 = 13)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('populate_db.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
bcrypt = Bcrypt(app)

def generate_text(template, replacements):
    """Generate text by replacing placeholders in template with random choices from replacements."""
    try:
        text = template
        for key, values in replacements.items():
            text = text.replace(f"{{{key}}}", random.choice(values))
        return text.strip()
    except Exception as e:
        logger.error(f"Error generating text for template '{template}': {str(e)}")
        return "Generated text error"

def init_db():
    with app.app_context():
        logger.info("Starting database initialization")
        db.drop_all()
        logger.info("Dropped existing tables")
        db.create_all()
        logger.info("Created new tables")

        # Create 10 user profiles
        users = [
            ('DarkHacker', 'pass123', 'darkhacker.jpg'),
            ('CyberGhost', 'ghost456', 'cyberghost.jpg'),
            ('ShadowV', 'shadow789', 'shadowv.jpg'),
            ('AnonX', 'anon101', 'anonx.jpg'),
            ('N3tRunn3r', 'runner202', 'netrunner.jpg'),
            ('Crypt0King', 'king303', 'cryptoking.jpg'),
            ('ZeroByte', 'zero404', 'zerobyte.jpg'),
            ('HackSavvy', 'savvy505', 'hacksavvy.jpg'),
            ('GhostRider', 'rider606', 'ghostrider.jpg'),
            ('DataViper', 'viper707', 'dataviper.jpg'),
        ]
        for username, password, avatar in users:
            if not User.query.filter_by(username=username).first():
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user = User(username=username, password=hashed_password, avatar=avatar)
                db.session.add(user)
                logger.info(f"Added user: {username}")
        try:
            db.session.commit()
            logger.info("Committed 10 users to database")
        except Exception as e:
            logger.error(f"Error committing users: {str(e)}")
            db.session.rollback()
            return

        user_ids = [user.id for user in User.query.all()]

        # Generate timestamps (within last 30 days)
        def random_timestamp():
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            seconds_ago = random.randint(0, 59)
            return (datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago, seconds=seconds_ago)).strftime('%Y-%m-%d %H:%M:%S')

        # Templates and replacements for text generation
        shoutbox_templates = [
            "New {item} drop in {place}!",
            "Looking for {item}, PM me!",
            "Anyone got {item} for sale?",
            "Fresh {item} available, DM for details!"
        ]
        shoutbox_replacements = {
            "item": ["CC dumps", "PayPal accounts", "phishing kits", "DDoS service", "malware"],
            "place": ["marketplace", "services", "dark pool"]
        }
        announcement_templates = {
            "title": [
                "{action} {item}",
                "{item} {status} Update",
                "New {item} Guidelines",
                "Discuss {item} Trends"
            ],
            "content": [
                "{action} {item}. Contact me for details.",
                "Recent {item} trends show {status}. Share your thoughts!",
                "Offering {service} for secure {item} deals. PM to join.",
                "Tips: Always verify {item} before trading."
            ]
        }
        announcement_replacements = {
            "action": ["New rules for", "Tips for trading", "Offering", "Discussing"],
            "item": ["data breaches", "phishing kits", "escrow services", "cyber-crime tools"],
            "status": ["increased activity", "new methods", "high demand", "stricter rules"],
            "service": ["middleman services", "secure deals", "escrow", "verification"]
        }
        marketplace_templates = {
            "title": {
                "Buyers": [
                    "Need {item}, High Budget",
                    "Looking for {item}",
                    "Buying Fresh {item}",
                    "Seeking {item} ASAP"
                ],
                "Sellers": [
                    "Selling {item}",
                    "Fresh {item} Available",
                    "{item} for Sale, {status}",
                    "High-Quality {item} Drop"
                ]
            },
            "description": {
                "Buyers": [
                    "Looking for {item}, willing to pay {price}. PM with offers.",
                    "Need clean {item}, urgent. DM me for details.",
                    "Seeking reliable {item} source, escrow available.",
                    "Buying {item}, top dollar for quality."
                ],
                "Sellers": [
                    "Selling {item}, high quality, {status}. PM for details.",
                    "Fresh batch of {item}, ready to use. Contact me!",
                    "{item} available, {status}. Escrow accepted.",
                    "High-validity {item}, bulk discounts available."
                ]
            }
        }
        marketplace_replacements = {
            "item": ["CC dumps", "PayPal accounts", "gift card codes", "data leaks", "RDP credentials", "VPN logins"],
            "status": ["clean and verified", "high balance", "freshly obtained", "limited stock"],
            "price": ["$100-$500", "$50-$200", "negotiable", "top dollar"]
        }
        iab_marketplace_templates = {
            "title": ["Access to {company} Network", "Selling {company} Credentials", "{company} IAB Drop"],
            "description": ["Compromised {company} access, {status}. PM for secure deal.", "Selling {company} network credentials, clean. Escrow only."]
        }
        iab_replacements = {
            "company": ["Acme Corp", "TechTrend Inc", "GlobalSys Ltd", "DataCore Solutions"],
            "status": ["verified admin access", "full network control", "recent breach", "exclusive access"]
        }
        # Predefined IAB posts for Sellers
        predefined_iab_posts = [
            {
                "title": "TD Bank RDP Access",
                "description": "Company: TD Bank\nRevenue: $1.64 billion\nIndustry: Banking\nAccess type: RDP\nPrice: DM me for price, serious buyers only, MM accepted",
                "price": "DM for price"
            },
            {
                "title": "Selling SMB Access to RBC Bank",
                "description": "Selling SMB access to RBC bank\nRevenue: $5.21\nIndustry: Banking\nCusomters: over 10 million\nCountry: Canada\n\n$12,000 Price is non-negotiatiable, dm me",
                "price": "$12000"
            },
            {
                "title": "Capital Freight Co. Access",
                "description": "Selling access to Capital Freight Co. (Texas-based logistics)\nRevenue: ~$900M\nAccess: Full RDP, domain admin via svc_x backup creds\nExtras: Internal invoices, mapped drives, Outlook web creds\nEDR: minimal – Defender only\nPrice: 0.6 BTC firm, BTC only, DM me quick",
                "price": "0.6 BTC"
            },
            {
                "title": "AspenWell Biotech Ltd Access",
                "description": "Company: AspenWell Biotech Ltd\nLocation: Netherlands\nRevenue: $1.3 billion\nAccess type: VPN > internal RDP > DA\nAdditional: SharePoint exposed, RMM agent deployed\nSecurity: No AV on internal, no logs tripped\nPrice: 1.05 BTC, escrow ok w/ rep\nSelling to ONE buyer only.",
                "price": "1.05 BTC"
            },
            {
                "title": "GLOBEX Holdings VPN Access",
                "description": "got corp vpn + psremote into GLOBEX Holdings, some UK fintech trash\nDA rights, creds pulled from exposed git repo (lol)\nno EDR, just weak-ass AV. internal docs and finance data wide open\nnot waitin long. 0.7 BTC. msg only if u got coin",
                "price": "0.7 BTC"
            },
            {
                "title": "Arctic Foods Group RDP Access",
                "description": "ACCESS TO ARCTIC FOODS GROUP\n– Canada HQ’d food distributor\n– RDP w/ DA, access stable 4 days\n– billing, inventory, HR PDFs open\n– Sophos AV but neutered\nRevenue: 2.1B CAD\nPrice: 1.2 BTC\nFAST BUYERS ONLY. No vouches, no timewasters.",
                "price": "1.2 BTC"
            },
            {
                "title": "Silverline Capital Partners Access",
                "description": "Company: Silverline Capital Partners (NY Private Equity firm)\nRevenue: approx $500M AUM\nAccess: RDP into domain w/ admin rights\nDetected: not yet, 3 days stable\nBonus: Access to doc mgmt system + Zoom internal creds\nSelling for 0.9 BTC – will include persistence script\nDM to deal",
                "price": "0.9 BTC"
            },
            {
                "title": "Veritas Health Partners Access",
                "description": "Access for sale: Veritas Health Partners, Canada\nRevenue: ~$430M\nIndustry: Healthcare\nAccess type: VPN + working RDP\nPrivilege: Local admin w/ internal share access\nNot detected – 6 days uptime\nPrice: 0.58 BTC firm",
                "price": "0.58 BTC"
            },
            {
                "title": "Portwell Maritime Group Access",
                "description": "Selling access to Portwell Maritime Group (Singapore)\nAccess: DA creds via exposed RDP svc acct\nRevenue: Est. $2B\nIndustry: Shipping / Transport\nExtras: payroll exports + crew schedules\nContact: DM if you’ve dealt before. Fast buyers only.",
                "price": "DM for price"
            },
            {
                "title": "Monarch Real Estate Access",
                "description": "Company: Monarch Real Estate Investments\nLocation: USA, NY\nRevenue: $380M\nAccess: Citrix > internal RDP > DA\nPersistence set, untouched for 4+ days\nBacked up docs + client lease agreements accessible\nPrice: 0.7 BTC, serious people only",
                "price": "0.7 BTC"
            }
        ]
        service_templates = {
            "title": {
                "Buy": [
                    "Need {service} Expert",
                    "Seeking {service}",
                    "Looking for {service} Pro",
                    "Requesting {service}"
                ],
                "Sell": [
                    "Offering {service}",
                    "{service} Available",
                    "Professional {service}",
                    "{service} for Hire"
                ]
            },
            "description": {
                "Buy": [
                    "Need {service} for a project, {status}. PM with rates.",
                    "Looking for reliable {service}, high budget. DM me.",
                    "Seeking {service} expert, escrow available.",
                    "Want {service}, urgent. Contact me!"
                ],
                "Sell": [
                    "Providing {service}, {status}. PM for pricing.",
                    "{service} with fast delivery, contact me.",
                    "Professional {service}, {status}. Escrow accepted.",
                    "Custom {service}, DM for details."
                ]
            }
        }
        service_replacements = {
            "service": ["DDoS attacks", "phishing campaigns", "malware development", "SQL injection", "botnet rental"],
            "status": ["fast and reliable", "guaranteed results", "24/7 support", "custom solutions"]
        }
        comment_templates = [
            "Interested in {item}, PM sent!",
            "Is {item} still available?",
            "Can you verify {item} quality?",
            "DM me for {item} details."
        ]
        comment_replacements = {
            "item": ["this deal", "your service", "the credentials", "this data"]
        }

        # Populate Shoutbox
        logger.info(f"Populating shoutbox with {NUM_SHOUTBOX_MESSAGES} messages")
        for i in range(0, NUM_SHOUTBOX_MESSAGES, 5):  # Batch of 5
            batch_size = min(5, NUM_SHOUTBOX_MESSAGES - i)
            messages = [generate_text(random.choice(shoutbox_templates), shoutbox_replacements)[:50] for _ in range(batch_size)]
            for j, message in enumerate(messages):
                shout = Shoutbox(
                    user_id=random.choice(user_ids),
                    message=message,
                    timestamp=random_timestamp()
                )
                db.session.add(shout)
                logger.info(f"Added shoutbox message {i + j + 1}/{NUM_SHOUTBOX_MESSAGES}: {message[:30]}...")
            try:
                db.session.commit()
                logger.info(f"Committed shoutbox messages {i + 1}-{i + batch_size}")
            except Exception as e:
                logger.error(f"Error committing shoutbox messages: {str(e)}")
                db.session.rollback()
                return

        # Populate Announcements (NUM_POSTS_PER_CATEGORY per category: Announcements, General, MM Service)
        categories = ['Announcements', 'General', 'MM Service']
        for category in categories:
            logger.info(f"Populating {category} announcements with {NUM_POSTS_PER_CATEGORY} posts")
            for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                titles = [generate_text(random.choice(announcement_templates["title"]), announcement_replacements)[:100] for _ in range(batch_size)]
                contents = [generate_text(random.choice(announcement_templates["content"]), announcement_replacements)[:200] for _ in range(batch_size)]
                for j, (title, content) in enumerate(zip(titles, contents)):
                    ann = Announcement(
                        category=category,
                        title=title,
                        content=content,
                        user_id=random.choice(user_ids),
                        date=random_timestamp()
                    )
                    db.session.add(ann)
                    logger.info(f"Added {category} announcement {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {category} announcements {i + 1}-{i + batch_size}")
                except Exception as e:
                    logger.error(f"Error committing {category} announcements: {str(e)}")
                    db.session.rollback()
                    return

        # Populate Marketplace (NUM_POSTS_PER_CATEGORY per category: Buyers, Sellers)
        categories = ['Buyers', 'Sellers']
        for category in categories:
            logger.info(f"Populating {category} marketplace posts with {NUM_POSTS_PER_CATEGORY} posts")
            if category == 'Sellers':
                # Add predefined IAB posts
                predefined_count = len(predefined_iab_posts)
                for i, post in enumerate(predefined_iab_posts):
                    market = Marketplace(
                        category=category,
                        title=post["title"][:100],
                        description=post["description"][:200],
                        user_id=random.choice(user_ids),
                        price=post["price"],
                        date=random_timestamp()
                    )
                    db.session.add(market)
                    logger.info(f"Added {category} predefined IAB post {i + 1}/{predefined_count}: {post['title'][:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {predefined_count} predefined IAB posts for {category}")
                except Exception as e:
                    logger.error(f"Error committing predefined IAB posts: {str(e)}")
                    db.session.rollback()
                    return

                # Add random IAB posts
                iab_posts = min(NUM_IAB_SELLER_POSTS, NUM_POSTS_PER_CATEGORY - predefined_count)
                for i in range(iab_posts):
                    title = generate_text(random.choice(iab_marketplace_templates["title"]), iab_replacements)[:100]
                    description = generate_text(random.choice(iab_marketplace_templates["description"]), iab_replacements)[:200]
                    price = f"${random.randint(50, 1000)}"
                    market = Marketplace(
                        category=category,
                        title=title,
                        description=description,
                        user_id=random.choice(user_ids),
                        price=price,
                        date=random_timestamp()
                    )
                    db.session.add(market)
                    logger.info(f"Added {category} random IAB post {i + 1}/{iab_posts}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {iab_posts} random IAB posts for {category}")
                except Exception as e:
                    logger.error(f"Error committing random IAB posts: {str(e)}")
                    db.session.rollback()
                    return

                # No non-IAB posts needed since 10 predefined + 3 random = 13
            else:
                # Buyers: all non-IAB
                for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                    batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                    titles = [generate_text(random.choice(marketplace_templates["title"][category]), marketplace_replacements)[:100] for _ in range(batch_size)]
                    descriptions = [generate_text(random.choice(marketplace_templates["description"][category]), marketplace_replacements)[:200] for _ in range(batch_size)]
                    for j, (title, description) in enumerate(zip(titles, descriptions)):
                        price = f"Offer ${random.randint(50, 500)}"
                        market = Marketplace(
                            category=category,
                            title=title,
                            description=description,
                            user_id=random.choice(user_ids),
                            price=price,
                            date=random_timestamp()
                        )
                        db.session.add(market)
                        logger.info(f"Added {category} marketplace post {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                    try:
                        db.session.commit()
                        logger.info(f"Committed {category} marketplace posts {i + 1}-{i + batch_size}")
                    except Exception as e:
                        logger.error(f"Error committing {category} marketplace posts: {str(e)}")
                        db.session.rollback()
                        return

        # Populate Services (NUM_POSTS_PER_CATEGORY per category: Buy, Sell)
        categories = ['Buy', 'Sell']
        for category in categories:
            logger.info(f"Populating {category} service posts with {NUM_POSTS_PER_CATEGORY} posts")
            for i in range(0, NUM_POSTS_PER_CATEGORY, 5):  # Batch of 5
                batch_size = min(5, NUM_POSTS_PER_CATEGORY - i)
                titles = [generate_text(random.choice(service_templates["title"][category]), service_replacements)[:100] for _ in range(batch_size)]
                descriptions = [generate_text(random.choice(service_templates["description"][category]), service_replacements)[:200] for _ in range(batch_size)]
                for j, (title, description) in enumerate(zip(titles, descriptions)):
                    price = f"${random.randint(100, 2000)}" if category == 'Sell' else 'Negotiable'
                    service = Service(
                        category=category,
                        title=title,
                        description=description,
                        user_id=random.choice(user_ids),
                        price=price,
                        date=random_timestamp()
                    )
                    db.session.add(service)
                    logger.info(f"Added {category} service post {i + j + 1}/{NUM_POSTS_PER_CATEGORY}: {title[:30]}...")
                try:
                    db.session.commit()
                    logger.info(f"Committed {category} service posts {i + 1}-{i + batch_size}")
                except Exception as e:
                    logger.error(f"Error committing {category} service posts: {str(e)}")
                    db.session.rollback()
                    return

        # Populate Comments (NUM_COMMENTS_PER_POST per post)
        logger.info(f"Populating comments ({NUM_COMMENTS_PER_POST} per post)")
        announcement_ids = [(post.id, 'announcement') for post in Announcement.query.all()]
        marketplace_ids = [(post.id, 'marketplace') for post in Marketplace.query.all()]
        service_ids = [(post.id, 'service') for post in Service.query.all()]
        all_posts = announcement_ids + marketplace_ids + service_ids
        total_comments = len(all_posts) * NUM_COMMENTS_PER_POST
        for i, (post_id, post_type) in enumerate(all_posts):
            for j in range(NUM_COMMENTS_PER_POST):
                content = generate_text(random.choice(comment_templates), comment_replacements)[:100]
                comment = Comment(
                    post_type=post_type,
                    post_id=post_id,
                    user_id=random.choice(user_ids),
                    content=content,
                    date=random_timestamp()
                )
                db.session.add(comment)
                logger.info(f"Added comment {j + 1}/{NUM_COMMENTS_PER_POST} for {post_type} post {post_id}: {content[:30]}...")
            try:
                db.session.commit()
                logger.info(f"Committed comments for {post_type} post {i + 1}/{len(all_posts)}")
            except Exception as e:
                logger.error(f"Error committing comments for {post_type} post {post_id}: {str(e)}")
                db.session.rollback()
                return

        total_posts = NUM_POSTS_PER_CATEGORY * (len(['Announcements', 'General', 'MM Service']) + len(['Buyers', 'Sellers']) + len(['Buy', 'Sell']))
        logger.info("Database population completed successfully")
        print(f"Database initialized with 10 users, {total_posts} posts, {NUM_SHOUTBOX_MESSAGES} shoutbox messages, and {total_comments} comments.")

if __name__ == '__main__':
    init_db()