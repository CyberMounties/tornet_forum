# shoutbox_simulator.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Shoutbox
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
        logging.FileHandler('shoutbox_simulator.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Shoutbox templates and replacements (same as populate_db.py)
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

def add_shoutbox_message():
    with app.app_context():
        # Get all user IDs
        user_ids = [user.id for user in User.query.all()]
        if not user_ids:
            logger.error("No users found in database")
            return False

        # Generate message
        message = generate_text(random.choice(shoutbox_templates), shoutbox_replacements)[:50]
        user_id = random.choice(user_ids)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Add to database
        shout = Shoutbox(
            user_id=user_id,
            message=message,
            timestamp=timestamp
        )
        try:
            db.session.add(shout)
            db.session.commit()
            logger.info(f"Added shoutbox message by user {user_id}: {message[:30]}...")
            return True
        except Exception as e:
            logger.error(f"Error committing shoutbox message: {str(e)}")
            db.session.rollback()
            return False

def main():
    logger.info("Starting shoutbox simulator")
    try:
        while True:
            if add_shoutbox_message():
                logger.info("Waiting 5 seconds before next message")
            else:
                logger.error("Failed to add message, retrying in 5 seconds")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shoutbox simulator stopped by user")
    except Exception as e:
        logger.error(f"Simulator crashed: {str(e)}")

if __name__ == '__main__':
    main()

