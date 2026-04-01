import os

import httpx
import sentry_sdk


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
