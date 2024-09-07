for hook_path in git-hooks/*
do
  if [ "${hook_path##*.}" != "py" ]  # Ignore .py files
  then
    # Create symbolic links inside .git/hooks/ directory
    ln -sf ../../$hook_path .git/hooks/
  fi
done

# Give permission to execute the hooks in the .git/hooks/ directory
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push