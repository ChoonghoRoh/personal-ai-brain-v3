cd /workspace

RULES_FILES="
docs/ai/ai-rule-phase-naming.md
docs/ai/ai-rule-phase-auto-generation.md
docs/ai/ai-rule-decision.md
docs/prompts/phase-auto-create-prompt.md
"

RULES_TEXT=""

for f in $RULES_FILES; do
  if [ -f "$f" ]; then
    RULES_TEXT="${RULES_TEXT}\n\n# --- ${f} ---\n"
    RULES_TEXT="${RULES_TEXT}$(cat "$f")"
  else
    RULES_TEXT="${RULES_TEXT}\n\n# --- ${f} (MISSING) ---\n"
  fi
done

echo -e "$RULES_TEXT"