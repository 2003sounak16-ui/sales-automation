#!/bin/bash
# GSD Skill Validation Script
# Validates all skill directories for required structure

error_count=0
warning_count=0
skills_checked=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " GSD ► VALIDATING SKILLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
target_dir=".agents/skills"
if [ ! -d "$target_dir" ]; then
    echo "❌ Missing $target_dir directory"
    exit 1
fi

shopt -s nullglob
skill_dirs=("$target_dir"/*/)
shopt -u nullglob

if [ ${#skill_dirs[@]} -eq 0 ]; then
    echo "❌ No skill directories found in $target_dir"
    exit 1
fi

for skill_dir in "${skill_dirs[@]}"; do
    ((skills_checked++))
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    has_errors=false
    
    # Check SKILL.md exists
    if [ ! -f "$skill_file" ]; then
        echo "❌ $skill_name: Missing SKILL.md"
        ((error_count++))
        continue
    fi
    
    # Check for frontmatter
    if ! head -1 "$skill_file" | grep -q "^---"; then
        echo "❌ $skill_name: Missing frontmatter"
        ((error_count++))
        has_errors=true
    fi
    
    # Check for name field
    if ! grep -q "name:" "$skill_file"; then
        echo "❌ $skill_name: Missing name in frontmatter"
        ((error_count++))
        has_errors=true
    fi
    
    # Check for description field
    if ! grep -q "description:" "$skill_file"; then
        echo "❌ $skill_name: Missing description in frontmatter"
        ((error_count++))
        has_errors=true
    fi
    
    # Check minimum length (skills should have substance)
    file_size=$(wc -c < "$skill_file")
    if [ "$file_size" -lt 200 ]; then
        echo "⚠️  $skill_name: Very short skill (<200 chars)"
        ((warning_count++))
    fi
    
    if [ "$has_errors" = false ]; then
        echo "✅ $skill_name"
    fi
done

echo ""
echo "───────────────────────────────────────────────────────"
echo ""
echo "Skills checked: $skills_checked"
echo "Errors: $error_count"
echo "Warnings: $warning_count"
echo ""

if [ $error_count -eq 0 ]; then
    echo "✅ All skills valid!"
    exit 0
else
    echo "❌ Validation failed"
    exit 1
fi
