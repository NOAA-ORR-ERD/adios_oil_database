# test_script

if ! git checkout a_non_existant_branch; then
    echo "-- couldn't checkout server_working_copy"
    echo "creating a new one"
else
    echo "in the else branch"
fi



# if ! git diff-index --quiet HEAD; then
#   echo ">>> git commit -m \"changes made in Web UI\""
#   git commit -m "changes made in Web UI"
# else
#   echo "Nothing to commit."
# fi