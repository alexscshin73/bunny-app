set repoPath to "/Users/sclshin/Projects/bunny-app"

set dialogText to "Paste the refreshed Cloudflare tunnel token for bunny.carroamix.com:"
set dialogResult to display dialog dialogText default answer "" buttons {"Cancel", "Save Token"} default button "Save Token"
set tokenValue to text returned of dialogResult

if tokenValue is "" then
	display dialog "A non-empty tunnel token is required." buttons {"OK"} default button "OK"
	return
end if

set storeCommand to "cd " & quoted form of repoPath & " && bash scripts/store_cloudflare_tunnel_token.sh " & quoted form of tokenValue
do shell script storeCommand

display dialog "Stored the Cloudflare tunnel token in macOS Keychain." buttons {"OK"} default button "OK"
