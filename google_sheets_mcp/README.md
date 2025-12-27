
# Google Workspace MCP Server

This MCP server provides access to multiple Google Workspace apps:
- Sheets (gspread)
- Gmail (google-api-python-client)
- Drive (google-api-python-client)
- Docs (google-api-python-client)
- Slides (google-api-python-client)
- Calendar (google-api-python-client)
- Keep (gkeepapi - Note: Keep API is unofficial/complex, using standard Google API where possible)

## Setup
1. Enable APIs in Google Console: Gmail, Drive, Docs, Slides, Calendar, Sheets.
2. Ensure `credentials.json` is present.
