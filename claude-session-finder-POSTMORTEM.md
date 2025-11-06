# Claude Session Finder - Post-Mortem

## What We Built

An ultrafast tool to search and resume Claude Code sessions across all directories. The user was tired of remembering which directory they ran `claude` in and having to hunt for sessions with `claude -r`.

## The Working MVP

At one point, we had a **working version** that successfully:

1. ✓ Indexed 133 sessions in 2-3 seconds
2. ✓ Cached results for 30 seconds (originally 5 minutes, user wanted it shorter)
3. ✓ Displayed sessions with:
   - Project name (extracted from path)
   - Directory path
   - Time in 12H format (e.g., "Nov 05, 10:00 PM")
   - First message snippet (60 chars for list, 200 chars for detail)
4. ✓ Fixed session selection bug in interactive mode
5. ✓ Bold headers in preview pane
6. ✓ Proper Unicode escapes for jq (\u001b instead of \033)

## How It Worked

### Session Storage Discovery

Claude Code stores sessions in: `~/.claude/projects/`

**Directory structure:**
```
~/.claude/projects/
├── -Users-harsha/
│   └── 00615ff2-3626-40e4-b95e-17c420203a99.jsonl
├── -Users-harsha-Development-Projects-crawlAI/
│   ├── ca0be879-299d-41dd-913f-eb51a6c34405.jsonl
│   └── agent-a159fb3f.jsonl  (skip these)
```

### Data Extraction

**Session file format** (`.jsonl` - newline-delimited JSON):
```json
{"type":"user","sessionId":"abc","cwd":"/Users/harsha/Tools","gitBranch":"","timestamp":"2025-11-05T22:00:19.367Z","message":{"role":"user","content":"I'm getting tired of..."}}
```

**Extraction strategy:**
1. Find all `.jsonl` files (excluding `agent-*.jsonl`)
2. Use `rg -m 1 '"type":"user"'` to get first user message (FAST!)
3. Use `tail -n 50 | rg '"type":"user"' | tail -n 1` for last user message
4. Extract with jq:
   - `sessionId` - UUID for `claude -r`
   - `cwd` - working directory
   - `projectName` - extracted from cwd: `(.cwd | split("/") | .[-1])`
   - `gitBranch` - branch name (if in git repo)
   - `timestamp` - ISO 8601 format
   - `firstMessage` and `lastMessage` - text content
5. Add metadata: file path, lastModified (from `stat`), messageCount (from `wc -l`)

### The Output (What The User Loved)

**List view** (what worked and user liked):
```
Project              Directory                                     Time             First Message
Tools                /Users/harsha/Tools                           Nov 05, 10:00 PM I'm getting really, really tired of...
crawlAI              /Users/harsha/Development/Projects/crawlAI    Nov 02, 10:00 PM Get this set up and scrape...
dotfiles             /Users/harsha/dotfiles                        Nov 04, 11:42 PM This session is being continued...
```

**Interactive mode preview** (full details):
```
Session:       6d1f5787-1eb7-4cc8-b698-1914ddac3e44
Project:       Tools
Path:          ~/Tools
Branch:        main
Time:          Nov 05, 10:00 PM
Messages:      375

First:
I'm getting really, really tired of trying to remember what directory I ran
claude in so that when I want to resume I have to go hunting for the right
directory to use claude -r to find it again. Write me an ultrafast tool...

Recent:
Maybe we can optimize here. The only thing I need to be able to pick from is
a list that shows me project name, directory, a snippet of the first message...
```

### Key Design Decisions

1. **Cache location:** `/tmp/claude-sessions-cache.jsonl`
2. **Cache TTL:** 30 seconds (user wanted it short, not 5 minutes)
3. **Tools used:**
   - `fd` - Find session files (fast)
   - `rg` - Extract JSON lines (ripgrep, faster than grep)
   - `jq` - Parse and transform JSON
   - `fzf` - Interactive picker
4. **Session matching:** By both project name AND full path (to handle duplicate project names)

## What Went Wrong

### The Fatal Bug: `set -euo pipefail` + Conditional Expressions

**Root cause:** Bash's `set -e` exits when ANY command returns non-zero, including:

```bash
[[ -z "$session" ]] && continue   # Returns 1 when session is NOT empty!
[[ ${#first_msg} -gt 60 ]] && short_display="${short_display}..."  # Returns 1 when ≤60 chars
[[ -n "$branch" ]] && echo "Branch: $branch"  # Returns 1 when branch is empty
```

**The symptoms:**
- Script would index 133 sessions successfully
- But only display 1 session
- Exit code 1 (failure)
- With `set -uo pipefail` (no -e), it displayed all 151 lines correctly

### Why It Was Hard To Debug

1. **Silent failure:** With `set -e`, the script exits immediately on first non-zero return
2. **`|| true` didn't work:** `&& command || true` has precedence issues
3. **Multiple locations:** The bug appeared in 5+ places throughout the script
4. **Worked without strict mode:** Removing `-e` made it work, masking the real issue

### Failed Fix Attempts

1. **Attempt 1:** Added `|| true` to each conditional
   - Problem: `&& continue || true` doesn't work as expected

2. **Attempt 2:** Changed to `[[ -n "$session" ]] || continue`
   - Better, but still had other failing conditionals

3. **Attempt 3:** Added error handling blocks `|| { echo "Error"; continue; }`
   - Made it worse, more places to fail

4. **Attempt 4:** Changed all conditionals to if/then blocks
   - Started fixing but never completed due to multiple locations

### Other Issues Encountered

1. **Cache race condition:** Setting `CACHE_TTL=0` caused rebuild during read
2. **jq escape codes:** Had to use `\u001b` instead of `\033` in jq strings
3. **Session ID extraction:** Initially matched by project name only, broke with duplicates
4. **Alias interference:** `cat=bat` aliased command interfering with heredocs

## The Correct Solution

Replace ALL instances of:
```bash
[[ condition ]] && action
```

With:
```bash
if [[ condition ]]; then
    action
fi
```

**OR** remove `set -e` entirely and handle errors explicitly where needed.

## Lessons Learned

1. **`set -e` is dangerous** with conditional logic - use sparingly
2. **Test incrementally** - we should have caught this after the first change
3. **Disable strict mode temporarily** when debugging weird exit behavior
4. **`bash -x` is your friend** for tracing execution
5. **Keep it simple** - the MVP was working, complexity killed it

## Files

- **Script:** `/Users/harsha/Tools/claude-session-finder`
- **Cache:** `/tmp/claude-sessions-cache.jsonl`
- **Session storage:** `~/.claude/projects/`

## Rebuild Checklist

When rebuilding from scratch:

- [ ] Use `fd` to find `.jsonl` files, exclude `agent-*`
- [ ] Use `rg -m 1 '"type":"user"'` for first message (fast!)
- [ ] Build cache with jq, include: sessionId, cwd, projectName, gitBranch, timestamp, firstMessage, lastMessage
- [ ] Format timestamps with: `date -j -f "%Y-%m-%dT%H:%M:%S" "${ts:0:19}" "+%b %d, %I:%M %p"`
- [ ] Truncate messages to 200 chars (~3-4 lines)
- [ ] Use printf for list view with proper column widths
- [ ] Match sessions in fzf by BOTH project name AND path
- [ ] **Either avoid `set -e` OR use only if/then blocks (no `&& ||` patterns)**
- [ ] Cache for 30 seconds max
- [ ] Test with multiple sessions before adding features

## What Worked Well

The core idea was solid:
- Indexing was fast (2-3 seconds for 133 sessions)
- Output format was exactly what user wanted
- Cache strategy was good
- Tool selection (fd, rg, jq, fzf) was perfect
- Session extraction logic was correct

**The only failure was Bash strict mode compatibility.**

---

**Status:** Ready for rebuild with proper conditional handling
