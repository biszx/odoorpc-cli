# Issue tracker

This repository uses GitHub Issues as its canonical issue tracker. The engineering skills (`to-issues`, `triage`, `to-prd`, `qa`) will use the `gh` CLI to create, read, update, and close issues in this repository.

Actions performed by skills:

- Create an issue: `gh issue create --title "..." --body "..."`
- Read an issue: `gh issue view <number> --comments`
- List issues: `gh issue list --state open --json number,title,body,labels,comments`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply labels: `gh issue edit <number> --add-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

If you prefer a different workflow (GitLab, `.scratch/` local markdown, Jira, etc.), re-run the setup skill or edit this file to describe the alternate workflow.
