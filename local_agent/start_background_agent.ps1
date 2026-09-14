# Starts the local Studio One worker after Windows sign-in.
# The worker reads the CloudBase URL and its token from local_agent/.env.
$agentRoot = $PSScriptRoot
$python = 'C:\Users\D1954\AppData\Local\Programs\Python\Python313\python.exe'
Set-Location -LiteralPath $agentRoot
& $python 'agent.py'
