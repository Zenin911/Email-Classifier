"""
generate_dataset.py — Synthetic Email Dataset Generator
Generates 3,000+ labeled emails across 6 categories × 3 urgency levels.
"""
import csv
import os
import random

# ─── Configuration ───────────────────────────────────────────────────────────
CATEGORIES = {
    "Billing Issue": {
        "subjects": [
            "Payment failed", "Refund request", "Incorrect charge on my account",
            "Double charged", "Invoice not received", "Subscription billing error",
            "Cancel my subscription", "Payment method update", "Overcharged",
            "Billing dispute", "Credit not applied", "Promo code not working"
        ],
        "bodies": [
            "I was charged twice for my last order #{order}. Please issue a refund immediately.",
            "My payment of ${amount} failed when I tried to renew my subscription. Can you help?",
            "I noticed an incorrect charge of ${amount} on my credit card statement from your company.",
            "I have been waiting for my refund for {days} days now. Order #{order}. This is unacceptable.",
            "I need to cancel my subscription and get a prorated refund for the remaining period.",
            "The promo code {code} is not working at checkout. It should give me {discount}% off.",
            "I was charged ${amount} but my plan only costs ${plan_cost}/month. Please fix this.",
            "My invoice for {month} has not been sent to my email. I need it for my records.",
            "I upgraded my plan but was charged the old rate plus the new rate. Please correct this.",
            "I cancelled {days} days ago but I'm still being charged. Please stop billing me.",
            "The annual billing was supposed to be ${amount} but I was charged ${wrong_amount}.",
            "I need a receipt for my recent purchase of ${amount} for tax purposes.",
        ]
    },
    "Technical Support": {
        "subjects": [
            "App crashing", "Error message", "Feature not working",
            "Slow performance", "Bug report", "Integration issue",
            "Cannot upload files", "Data sync problem", "API error",
            "Dashboard not loading", "Export failing", "Mobile app issue"
        ],
        "bodies": [
            "The application crashes every time I try to open the {feature} section. Error code: {error}.",
            "I'm getting a '{error_msg}' error when I try to {action}. This started {days} days ago.",
            "The {feature} feature stopped working after the latest update. It was fine before.",
            "The app is extremely slow, taking over {seconds} seconds to load each page.",
            "I found a bug: when I click {button}, nothing happens. Expected behavior is {expected}.",
            "The integration with {service} is broken. Data is not syncing properly since {date}.",
            "I cannot upload any files larger than {size}MB. The upload just fails silently.",
            "Data sync between my devices stopped working. Changes on {device1} don't appear on {device2}.",
            "Getting a {status_code} error when calling your API endpoint /api/{endpoint}.",
            "The dashboard shows blank charts and no data, even though I have {count} records.",
            "Export to {format} always fails with a timeout error. I have {count} rows of data.",
            "The mobile app on {platform} freezes when I try to {action}. Version {version}.",
        ]
    },
    "Account Access": {
        "subjects": [
            "Cannot login", "Password reset not working", "Account locked",
            "Two-factor authentication issue", "Email verification failed",
            "Account recovery", "Username change", "Security concern",
            "Session expired", "SSO not working", "Permission denied",
            "Account deactivated"
        ],
        "bodies": [
            "I cannot log in to my account. I've tried resetting my password {attempts} times.",
            "The password reset email is not arriving. I've checked spam folders too.",
            "My account has been locked after {attempts} failed login attempts. Please unlock it.",
            "I lost my phone and can't access my two-factor authentication codes.",
            "The email verification link expired before I could click it. Please resend.",
            "I need to recover my account. The email on file is {old_email} but I now use {new_email}.",
            "How do I change my username from {old_name} to {new_name}?",
            "I think someone accessed my account. I see login activity from {location} which isn't me.",
            "My session keeps expiring every {minutes} minutes. I have to login constantly.",
            "SSO login with {provider} is giving an 'invalid redirect' error.",
            "I'm getting 'permission denied' when trying to access the {section} section.",
            "My account was deactivated without warning. I need it restored as I have important data.",
        ]
    },
    "Complaint": {
        "subjects": [
            "Very disappointed", "Terrible experience", "Want to speak to manager",
            "Worst service ever", "Filing a complaint", "Unacceptable service",
            "Misleading advertising", "Broken promises", "Poor quality",
            "Rude staff", "Wasted my time", "Demand compensation"
        ],
        "bodies": [
            "I am extremely disappointed with your service. I have been a customer for {years} years and this is the worst experience.",
            "Your support team was incredibly unhelpful. I spent {hours} hours on hold and got no resolution.",
            "The product quality has degraded significantly since I first subscribed {months} months ago.",
            "I was promised {feature} when I signed up but it was never delivered. This is misleading.",
            "I want to escalate this to your manager. The issue has been unresolved for {days} days.",
            "Your advertising claims {claim} but the actual product does not deliver on this promise.",
            "I am considering filing a complaint with consumer protection. Your service is unacceptable.",
            "I have had to contact support {times} times for the same issue. This is ridiculous.",
            "The {feature} you advertised as 'industry-leading' is actually worse than your competitors.",
            "I demand compensation for the {days} days of downtime that affected my business.",
            "Your staff member {name} was extremely rude and dismissive of my concerns.",
            "I regret choosing your service over {competitor}. I will be switching immediately.",
        ]
    },
    "Feature Request": {
        "subjects": [
            "Feature suggestion", "New idea", "Enhancement request",
            "Would love to see", "Improvement suggestion", "Feature proposal",
            "Wishlist item", "Product feedback", "Missing functionality",
            "UX improvement", "New integration request", "Roadmap question"
        ],
        "bodies": [
            "It would be great if you could add {feature}. This would save me {hours} hours per week.",
            "I'd love to see integration with {service}. Many of your users also use it.",
            "Could you add the ability to {action}? Currently I have to use {workaround} which is tedious.",
            "A {feature} feature would make your product much more competitive against {competitor}.",
            "Please consider adding dark mode. I use the app for {hours} hours daily and it strains my eyes.",
            "Having bulk {action} capability would be a huge time saver for power users like me.",
            "I suggest adding keyboard shortcuts for common actions like {action1} and {action2}.",
            "An API for {feature} would allow developers like me to build custom integrations.",
            "Please add export functionality to {format} format. We need this for our reporting.",
            "A mobile widget for {feature} would be very useful for quick access.",
            "Could you add customizable {element}? The current fixed options don't suit our workflow.",
            "I'd like to request a {feature} similar to what {competitor} offers. It's the only thing missing.",
        ]
    },
    "General Inquiry": {
        "subjects": [
            "Question about pricing", "How does it work", "Information request",
            "Getting started", "Product comparison", "Documentation question",
            "Training options", "Partnership inquiry", "Enterprise plan",
            "Trial extension", "Webinar question", "General question"
        ],
        "bodies": [
            "Can you tell me more about your {plan} plan? I'm considering upgrading from {current_plan}.",
            "How does the {feature} work? I couldn't find clear documentation on this.",
            "What is the difference between the {plan1} and {plan2} plans?",
            "I'm new to your platform. Could you point me to getting started resources?",
            "Do you offer any discounts for {type} organizations?",
            "Is there a way to try the {feature} before committing to the premium plan?",
            "I'd like to learn more about your enterprise offerings for a team of {size} people.",
            "Do you have any upcoming webinars or training sessions on {topic}?",
            "Can my trial be extended by {days} more days? I haven't had time to fully evaluate.",
            "How does your product compare to {competitor} in terms of {feature}?",
            "I'm interested in a partnership opportunity. Who should I speak with?",
            "What data formats do you support for import? I need to migrate from {service}.",
        ]
    },
}

URGENCY_RULES = {
    "Billing Issue": {"High": 0.4, "Medium": 0.4, "Low": 0.2},
    "Technical Support": {"High": 0.3, "Medium": 0.5, "Low": 0.2},
    "Account Access": {"High": 0.5, "Medium": 0.35, "Low": 0.15},
    "Complaint": {"High": 0.5, "Medium": 0.35, "Low": 0.15},
    "Feature Request": {"High": 0.1, "Medium": 0.3, "Low": 0.6},
    "General Inquiry": {"High": 0.05, "Medium": 0.35, "Low": 0.6},
}

# Filler values for template placeholders
FILLERS = {
    "order": lambda: str(random.randint(100000, 999999)),
    "amount": lambda: str(random.randint(10, 500)),
    "wrong_amount": lambda: str(random.randint(100, 999)),
    "plan_cost": lambda: str(random.choice([9, 19, 29, 49, 99])),
    "days": lambda: str(random.randint(1, 30)),
    "months": lambda: str(random.randint(1, 24)),
    "years": lambda: str(random.randint(1, 10)),
    "hours": lambda: str(random.randint(1, 8)),
    "minutes": lambda: str(random.randint(5, 60)),
    "seconds": lambda: str(random.randint(10, 120)),
    "attempts": lambda: str(random.randint(2, 10)),
    "times": lambda: str(random.randint(3, 15)),
    "count": lambda: str(random.randint(100, 10000)),
    "size": lambda: str(random.choice([5, 10, 25, 50, 100])),
    "discount": lambda: str(random.choice([10, 15, 20, 25, 30, 50])),
    "code": lambda: random.choice(["SAVE20", "WELCOME10", "LOYAL50", "NEWYEAR", "FLASH25"]),
    "month": lambda: random.choice(["January", "February", "March", "April", "May", "June"]),
    "feature": lambda: random.choice(["reports", "analytics", "notifications", "calendar", "search", "export", "import", "dashboard", "settings"]),
    "error": lambda: f"ERR-{random.randint(100,999)}",
    "error_msg": lambda: random.choice(["Something went wrong", "Unexpected error", "Connection timeout", "Invalid request", "Server error 500"]),
    "action": lambda: random.choice(["save my work", "generate a report", "send notifications", "sync data", "upload files", "export data"]),
    "button": lambda: random.choice(["Save", "Submit", "Export", "Delete", "Refresh", "Upload"]),
    "expected": lambda: random.choice(["it should save", "it should redirect", "a confirmation popup", "data refresh"]),
    "service": lambda: random.choice(["Slack", "Google Drive", "Salesforce", "Jira", "Trello", "Zapier", "HubSpot"]),
    "date": lambda: f"Feb {random.randint(1,28)}",
    "device1": lambda: random.choice(["desktop", "laptop", "phone"]),
    "device2": lambda: random.choice(["tablet", "phone", "laptop"]),
    "status_code": lambda: str(random.choice([400, 401, 403, 404, 500, 502, 503])),
    "endpoint": lambda: random.choice(["users", "data", "reports", "settings", "export"]),
    "format": lambda: random.choice(["CSV", "PDF", "Excel", "JSON"]),
    "platform": lambda: random.choice(["iOS", "Android"]),
    "version": lambda: f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
    "old_email": lambda: f"old_{random.randint(1,999)}@email.com",
    "new_email": lambda: f"new_{random.randint(1,999)}@email.com",
    "old_name": lambda: random.choice(["john_doe", "user123", "myname"]),
    "new_name": lambda: random.choice(["john.doe.pro", "real_name", "updated_user"]),
    "location": lambda: random.choice(["Russia", "China", "Brazil", "Nigeria", "unknown IP"]),
    "provider": lambda: random.choice(["Google", "Microsoft", "Okta", "Auth0"]),
    "section": lambda: random.choice(["admin", "billing", "analytics", "settings"]),
    "name": lambda: random.choice(["Alex", "Jordan", "Sam", "Chris", "Pat"]),
    "claim": lambda: random.choice(["99.9% uptime", "fastest in class", "unlimited storage", "24/7 support"]),
    "competitor": lambda: random.choice(["Zendesk", "Freshdesk", "Intercom", "HelpScout"]),
    "plan": lambda: random.choice(["Pro", "Business", "Enterprise", "Premium"]),
    "current_plan": lambda: random.choice(["Free", "Basic", "Starter"]),
    "plan1": lambda: random.choice(["Pro", "Business"]),
    "plan2": lambda: random.choice(["Enterprise", "Premium"]),
    "type": lambda: random.choice(["non-profit", "educational", "startup", "government"]),
    "topic": lambda: random.choice(["automation", "reporting", "API usage", "best practices"]),
    "element": lambda: random.choice(["dashboards", "templates", "workflows", "notifications"]),
    "action1": lambda: random.choice(["copy", "paste", "search"]),
    "action2": lambda: random.choice(["navigate", "filter", "sort"]),
}

# Tone modifiers for augmentation
URGENCY_PREFIXES = {
    "High": [
        "URGENT: ", "CRITICAL: ", "IMMEDIATE ATTENTION NEEDED: ",
        "HELP ASAP: ", "EMERGENCY: ", ""
    ],
    "Medium": [
        "Need help: ", "Question: ", "Help needed: ",
        "Requesting assistance: ", "", ""
    ],
    "Low": [
        "Just wondering: ", "Quick question: ", "FYI: ",
        "When you get a chance: ", "", ""
    ],
}

URGENCY_SUFFIXES = {
    "High": [
        " This is extremely urgent and needs immediate resolution.",
        " I need this fixed RIGHT NOW or I will cancel my account.",
        " This is blocking my entire team from working.",
        " Please prioritize this as it is critically impacting our operations.",
        " I've been waiting too long already. Escalate this immediately.",
        "",
    ],
    "Medium": [
        " I'd appreciate a response within a day or two.",
        " Please let me know when you can look into this.",
        " Looking forward to hearing back from you soon.",
        " Thanks in advance for your help.",
        "",
        "",
    ],
    "Low": [
        " No rush on this, just curious.",
        " Whenever you get a chance would be great.",
        " This is not urgent at all, just a thought.",
        " Take your time with this.",
        "",
        "",
    ],
}

GREETINGS = [
    "Hi, ", "Hello, ", "Dear Support Team, ", "Hey there, ",
    "Good morning, ", "Hi team, ", "To whom it may concern, ",
    "", "", "",  # Sometimes no greeting
]

SIGN_OFFS = [
    "\n\nBest regards,\nCustomer", "\n\nThanks,\nUser",
    "\n\nSincerely,\nClient", "\n\nRegards",
    "\n\nThank you.", "", "", "",  # Sometimes no sign-off
]


def fill_template(template: str) -> str:
    """Replace {placeholder} tokens with random filler values."""
    import re
    def replacer(match):
        key = match.group(1)
        if key in FILLERS:
            return FILLERS[key]()
        return match.group(0)
    return re.sub(r'\{(\w+)\}', replacer, template)


def generate_email(category: str, urgency: str) -> str:
    """Generate a single synthetic email."""
    cat_data = CATEGORIES[category]
    subject = random.choice(cat_data["subjects"])
    body = fill_template(random.choice(cat_data["bodies"]))

    prefix = random.choice(URGENCY_PREFIXES[urgency])
    suffix = random.choice(URGENCY_SUFFIXES[urgency])
    greeting = random.choice(GREETINGS)
    sign_off = random.choice(SIGN_OFFS)

    email = f"{greeting}{prefix}Subject: {subject}\n\n{body}{suffix}{sign_off}"
    return email


def main():
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "raw_emails.csv")

    emails = []
    target_per_category = 550  # ~3,300 total

    for category in CATEGORIES:
        weights = URGENCY_RULES[category]
        for urgency, proportion in weights.items():
            count = int(target_per_category * proportion)
            for _ in range(count):
                text = generate_email(category, urgency)
                emails.append({
                    "email_text": text,
                    "category": category,
                    "urgency": urgency,
                })

    random.shuffle(emails)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email_text", "category", "urgency"])
        writer.writeheader()
        writer.writerows(emails)

    print(f"✅ Generated {len(emails)} emails → {output_path}")
    # Print distribution
    from collections import Counter
    cat_counts = Counter(e["category"] for e in emails)
    urg_counts = Counter(e["urgency"] for e in emails)
    print("\n📊 Category Distribution:")
    for c, n in sorted(cat_counts.items()):
        print(f"   {c}: {n}")
    print("\n📊 Urgency Distribution:")
    for u, n in sorted(urg_counts.items()):
        print(f"   {u}: {n}")


if __name__ == "__main__":
    main()
