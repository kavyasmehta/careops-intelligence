"""Client case-summary generator.

Always works with zero API keys: `render_template_summary` deterministically
composes a plain-English paragraph from the same operational facts a human
would check before a client call. An LLM rewrite is available strictly as
an opt-in (ENABLE_LLM_SUMMARY=true + LLM_API_KEY set) behind the
SummaryProvider interface below — if it's off, misconfigured, or the call
fails for any reason, generation falls back to the template rather than
erroring, because a summary tool that sometimes just doesn't work isn't
useful. Content is always labeled with how it was produced, and the
prompt/template both explicitly forbid clinical recommendations — this is
an operations summary, not a care-planning tool.
"""
import asyncio
from datetime import UTC, date, datetime
from typing import Protocol

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.case_summary import CaseSummary

logger = get_logger(__name__)

DISCLAIMER = (
    "AI-assisted operational summary generated from synthetic demo data. "
    "Not a clinical assessment or recommendation."
)


class SummaryProvider(Protocol):
    async def generate(self, context: dict) -> str: ...


async def _gather_context(db: AsyncIOMotorDatabase, client: dict) -> dict:
    client_id = client["id"]
    today = date.today().isoformat()
    now_iso = datetime.now(UTC).isoformat()

    latest_eligibility = await db["eligibility_checks"].find_one(
        {"client_id": client_id}, sort=[("check_date", -1)]
    )
    authorizations = await db["authorizations"].find({"client_id": client_id}).to_list(length=None)
    upcoming_appointment = await db["appointments"].find_one(
        {"client_id": client_id, "status": "scheduled", "appointment_datetime": {"$gt": now_iso}},
        sort=[("appointment_datetime", 1)],
    )
    open_alerts = await db["alerts"].find({"client_id": client_id, "status": {"$ne": "resolved"}}).to_list(
        length=None
    )
    overdue_tasks = await db["tasks"].find(
        {"client_id": client_id, "status": {"$ne": "completed"}, "due_date": {"$lt": today}}
    ).to_list(length=None)
    recent_notes = await db["case_notes"].find({"client_id": client_id}).sort("created_at", -1).to_list(length=3)

    return {
        "client": client,
        "latest_eligibility": latest_eligibility,
        "authorizations": authorizations,
        "upcoming_appointment": upcoming_appointment,
        "open_alerts": open_alerts,
        "overdue_tasks": overdue_tasks,
        "recent_notes": recent_notes,
    }


def render_template_summary(context: dict) -> str:
    client = context["client"]
    lines = [f"{client['first_name']} {client['last_name']} (member {client['member_id']}) — operational snapshot."]

    check = context["latest_eligibility"]
    if check:
        status = check["coverage_status"]
        if status == "failed":
            lines.append(f"Latest eligibility check with {check['payer']} FAILED ({check.get('failure_reason', 'reason not recorded')}).")
        else:
            lines.append(f"Latest eligibility check with {check['payer']} is {status}.")
    else:
        lines.append("No eligibility checks on file.")

    active_auths = [a for a in context["authorizations"] if a["status"] in ("active", "pending")]
    if active_auths:
        parts = [f"{a['authorization_number']} ({a['service_type']}, {a['units_used']}/{a['units_approved']} units, expires {a['expiration_date']})" for a in active_auths[:3]]
        lines.append(f"Active/pending authorizations: {'; '.join(parts)}.")
    else:
        lines.append("No active or pending authorizations on file.")

    appt = context["upcoming_appointment"]
    if appt:
        lines.append(f"Next appointment: {appt['service_type']} with {appt['provider']} on {appt['appointment_datetime'][:10]}.")
    else:
        lines.append("No upcoming appointments scheduled.")

    if context["open_alerts"]:
        lines.append(f"{len(context['open_alerts'])} open alert(s), highest severity: {max((a['severity'] for a in context['open_alerts']), key=['low','medium','high','critical'].index)}.")
    else:
        lines.append("No open alerts.")

    if context["overdue_tasks"]:
        lines.append(f"{len(context['overdue_tasks'])} overdue task(s), including: {context['overdue_tasks'][0]['title']}.")
    else:
        lines.append("No overdue tasks.")

    if context["recent_notes"]:
        lines.append(f"Most recent note ({context['recent_notes'][0]['author']}): \"{context['recent_notes'][0]['note_text'][:140]}\"")
    else:
        lines.append("No case notes on file.")

    return " ".join(lines)


class TemplateSummaryProvider:
    async def generate(self, context: dict) -> str:
        return render_template_summary(context)


class LLMSummaryProvider:
    """Optional rewrite of the same facts via an LLM. Never sends anything
    beyond what's already in `context` (all synthetic demo data), and never
    called at all unless explicitly enabled via settings.
    """

    async def generate(self, context: dict) -> str:
        settings = get_settings()
        try:
            import anthropic  # lazy import: never required for the default template path
        except ImportError:
            logger.warning("ENABLE_LLM_SUMMARY is true but the anthropic package isn't installed; using template.")
            return render_template_summary(context)

        client_facts = render_template_summary(context)
        api_client = anthropic.Anthropic(api_key=settings.llm_api_key)

        def _call() -> str:
            # The SDK's default client is synchronous; run it off the event
            # loop so an enabled LLM summary can't block other requests.
            response = api_client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=200,
                system=(
                    "Rewrite the following operational facts about a healthcare-operations "
                    "client case into a concise, professional 2-3 sentence summary for an "
                    "operations team. Do not add any clinical assessment, diagnosis, or "
                    "treatment recommendation — this is operational (billing/scheduling/"
                    "eligibility) context only. Do not invent facts not given."
                ),
                messages=[{"role": "user", "content": client_facts}],
            )
            return response.content[0].text

        return await asyncio.to_thread(_call)


async def generate_case_summary(db: AsyncIOMotorDatabase, client: dict) -> CaseSummary:
    settings = get_settings()
    context = await _gather_context(db, client)

    provider: SummaryProvider
    generated_by = "template"
    if settings.enable_llm_summary and settings.llm_api_key:
        provider = LLMSummaryProvider()
        generated_by = "llm"
    else:
        provider = TemplateSummaryProvider()

    try:
        summary_text = await provider.generate(context)
    except Exception:
        logger.exception("Summary generation failed; falling back to template.")
        summary_text = render_template_summary(context)
        generated_by = "template"

    return CaseSummary(
        client_id=client["id"],
        summary=summary_text,
        generated_by=generated_by,
        disclaimer=DISCLAIMER,
        generated_at=datetime.now(UTC),
    )
