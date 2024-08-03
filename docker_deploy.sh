latest_tag=$(git describe --tags --match "*" --abbrev=0 2>/dev/null)

previous_tag_1=$(git describe --tags --match "*" --abbrev=0 ${latest_tag}^ 2>/dev/null)
previous_tag_2=$(git describe --tags --match "*" --abbrev=0 ${previous_tag_1}^ 2>/dev/null)

file_patterns="Dockerfile* docker* nginx* requirements.txt command.cron"

echo "Latest tag: $latest_tag"
echo "Previous tag 1: $previous_tag_1"
echo "Previous tag 2: $previous_tag_2"

pattern_file_changed_exists=false

if [ -z "$latest_tag" ] || [ -z "$previous_tag_1" ] || [ -z "$previous_tag_2" ]; then
    echo "No tags found"
else
    changed_files_latest_tag_to_previous_tag_1=$(git diff --name-only $previous_tag_1 $latest_tag)
    changed_files_previous_tag_1_to_previous_tag_2=$(git diff --name-only $previous_tag_2 $previous_tag_1)

    for pattern in $file_patterns; do
        if echo "$changed_files_latest_tag_to_previous_tag_1" | grep -q -e "$pattern"; then
            pattern_file_changed_exists=true
            echo "changed_files_latest_tag_to_previous_tag_1 pattern_file_changed_exists"
            break
        fi

        if echo "$changed_files_previous_tag_1_to_previous_tag_2" | grep -q -e "$pattern"; then
            pattern_file_changed_exists=true
            echo "changed_files_previous_tag_1_to_previous_tag_2 pattern_file_changed_exists"
            break
        fi
    done
fi

chmod 777 docker_hard_deploy.sh
chmod 777 docker_soft_deploy.sh

if [ "$pattern_file_changed_exists" = "true" ]; then
    ./docker_hard_deploy.sh
else
    ./docker_soft_deploy.sh
fi