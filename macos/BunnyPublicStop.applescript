set repoPath to "/Users/sclshin/Projects/bunny-app"
set stopCommand to "cd " & quoted form of repoPath & " && bash scripts/bunny_public_stop.sh"

tell application "Terminal"
  activate
  do script stopCommand
end tell
