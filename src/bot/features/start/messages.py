DEFAULT_WELCOME_MESSAGE = (
    "🛍️ <b>Welcome to {store_name}!</b>\n\n"
    "Yahan aap ko milen ge premium digital tools, methods, courses, aur resources.\n"
    "Har category mein curated items hain jo aap ke kaam ko fast aur easy banayein.\n\n"
    "What you can explore:\n"
    "- Digital tools & scripts\n"
    "- Marketing/automation methods\n"
    "- Courses & step-by-step guides\n"
    "- Templates, assets, and resources\n\n"
    "Menu se start karein, categories browse karein, cart banayein, aur profile check karein.\n"
)


def welcome_message(store_name: str, template: str | None = None) -> str:
    message = template if template and template.strip() else DEFAULT_WELCOME_MESSAGE
    return message.replace("{store_name}", store_name)
