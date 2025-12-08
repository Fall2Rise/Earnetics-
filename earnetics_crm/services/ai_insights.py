from typing import List

from earnetics_crm import schemas


def generate_contact_summary(contact: schemas.Contact, interactions: List[schemas.Interaction]) -> str:
    lines = [f"Contact: {contact.name} ({contact.type or 'n/a'})"]
    if contact.email:
        lines.append(f"Email: {contact.email}")
    if contact.phone:
        lines.append(f"Phone: {contact.phone}")
    if interactions:
        lines.append(f"Recent interactions ({len(interactions)}):")
        for i in interactions[:5]:
            lines.append(f"- [{i.channel}] {i.direction or ''} {i.content[:120]}")
    else:
        lines.append("No recent interactions.")
    return "\n".join(lines)


def suggest_next_actions_for_deal(deal: schemas.Deal, contact: schemas.Contact, interactions: List[schemas.Interaction]) -> List[str]:
    actions = []
    if deal.stage in {"new", "contacted"}:
        actions.append("Schedule intro call and confirm requirements.")
    if deal.priority == "high":
        actions.append("Send priority follow-up and escalate to executive.")
    if not interactions:
        actions.append("No interactions yet; send first-touch outreach.")
    return actions or ["Review deal and plan next step."]


def draft_followup_message(contact: schemas.Contact, deal: schemas.Deal, tone: str = "neutral") -> str:
    greeting = f"Hi {contact.name},"
    body = (
        f"Thanks for your time discussing {deal.title}. "
        "Let me know if you have any questions or would like to move to the next step."
    )
    closing = "Best regards,\nEarnetics Team"
    return "\n\n".join([greeting, body, closing])
