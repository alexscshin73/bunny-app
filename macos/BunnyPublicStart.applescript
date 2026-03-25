set repoPath to "/Users/sclshin/Projects/bunny-app"
set startCommand to "cd " & quoted form of repoPath & " && bash scripts/bunny_public_start.sh"

tell application "Terminal"
  activate
  do script startCommand
end tell
