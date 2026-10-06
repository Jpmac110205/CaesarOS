# Email Agent

Loads messages through the service layer, strips legacy demo classification labels, and asks live Jev to judge action requirements and category. It retains the returned probabilities/confidence in `email_output.classifications`.

Python sorts actionable messages by supplied deadline and identifies interview context. OpenAI generates the summary and a context-specific draft. Sending mail is unimplemented; drafts are never sent. The inbox remains synthetic until the Gmail adapter is connected.
