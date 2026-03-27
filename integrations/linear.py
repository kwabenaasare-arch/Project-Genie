import hashlib
import hmac
import os

import httpx
import sentry_sdk


def verify_signature(raw_body: bytes, signature: str) -> bool:
    secret = os.environ.get("LINEAR_WEBHOOK_SECRET", "")
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def format_linear_event(payload: dict) -> str | None:
    action = payload.get("action")          # "create" | "update" | "remove"
    event_type = payload.get("type")        # "Issue" | "Comment" | "Project" …
    data = payload.get("data", {})

    if event_type == "Issue":
        title = data.get("title", "Untitled")
        state = data.get("state", {}).get("name", "Unknown")
        url = data.get("url", "")
        assignee = data.get("assignee", {})
        assignee_name = assignee.get("name", "") if assignee else ""

        action_label = {"create": "created", "update": "updated", "remove": "deleted"}.get(action, action)

        line = f"📋 Linear issue *{action_label}*: <{url}|{title}> → *{state}*"
        if assignee_name:
            line += f" (assigned to {assignee_name})"
        return line

    if event_type == "Comment":
        body = data.get("body", "")
        issue = data.get("issue", {})
        issue_title = issue.get("title", "an issue") if issue else "an issue"
        url = issue.get("url", "") if issue else ""
        user = data.get("user", {})
        user_name = user.get("name", "Someone") if user else "Someone"

        preview = body[:120] + ("…" if len(body) > 120 else "")
        return f"💬 {user_name} commented on <{url}|{issue_title}>: _{preview}_"

    return None


def get_pending_issues() -> str:
    api_key = os.environ.get("LINEAR_API_KEY", "")
    if not api_key:
        return "LINEAR_API_KEY is not configured."

    query = """
    query {
      issues(
        filter: { state: { type: { nin: ["completed", "cancelled"] } } }
        orderBy: updatedAt
      ) {
        nodes {
          title
          state { name }
          priority
          assignee { name }
          url
          dueDate
        }
      }
    }
    """

    try:
        response = httpx.post(
            "https://api.linear.app/graphql",
            headers={"Authorization": api_key, "Content-Type": "application/json"},
            json={"query": query},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return "Could not retrieve Linear issues at this time."

    if not issues:
        return "You have no pending issues in Linear. All clear!"

    priority_labels = {0: "No priority", 1: "Urgent", 2: "High", 3: "Medium", 4: "Low"}

    lines = [f"You have *{len(issues)} pending issue(s)* in Linear:\n"]
    for issue in issues:
        title = issue.get("title", "Untitled")
        state = issue.get("state", {}).get("name", "Unknown")
        priority = priority_labels.get(issue.get("priority", 0), "No priority")
        assignee = (issue.get("assignee") or {}).get("name", "Unassigned")
        url = issue.get("url", "")
        due = issue.get("dueDate")

        line = f"• <{url}|{title}> — *{state}* | {priority}"
        if assignee != "Unassigned":
            line += f" | {assignee}"
        if due:
            line += f" | Due: {due}"
        lines.append(line)

    return "\n".join(lines)
